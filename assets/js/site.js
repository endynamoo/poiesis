/* Poiesis — the interactive layer.
   One clock, one scroll read, one shader. Everything degrades to a still frame. */

(function () {
  "use strict";

  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  const finePointer = window.matchMedia("(pointer: fine)");
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const mmss = (s) => {
    s = Math.max(0, Math.round(s));
    return String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0");
  };

  const state = { y: window.scrollY, vh: window.innerHeight, docH: 0, t0: performance.now() };
  const measure = () => {
    state.vh = window.innerHeight;
    state.docH = document.documentElement.scrollHeight;
  };
  measure();

  /* — 1 · hero shader ---------------------------------------------------- */
  const canvas = document.querySelector(".hero__stage");
  let gl = null, program = null, uniforms = {}, heroVisible = true;

  const VERT = "attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}";
  const FRAG = `
precision highp float;
uniform vec2 uRes; uniform float uTime; uniform vec2 uMouse;
float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p){
  vec2 i = floor(p), f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
             mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}
float fbm(vec2 p){
  float v = 0.0, a = 0.5;
  for (int i = 0; i < 4; i++) { v += a * noise(p); p *= 2.03; a *= 0.5; }
  return v;
}
float motes(vec2 uv, float t){
  float sum = 0.0;
  for (int i = 0; i < 3; i++) {
    float fi = float(i);
    vec2 gp = uv * vec2(10.0 + fi * 6.0, 7.0 + fi * 4.0)
            + vec2(t * (0.26 + fi * 0.18), -t * (0.30 + fi * 0.10));
    vec2 cell = floor(gp);
    vec2 f = fract(gp) - 0.5;
    float h = hash(cell + fi * 17.0);
    vec2 off = vec2(hash(cell + 3.1), hash(cell + 7.7)) - 0.5;
    float d = length(f - off * 0.72);
    float spark = smoothstep(0.052, 0.0, d) * step(0.78, h);
    sum += spark * (0.45 + 0.55 * sin(uTime * 1.3 + h * 40.0));
  }
  return sum;
}

void main(){
  vec2 uv = (gl_FragCoord.xy - 0.5 * uRes) / uRes.y;
  float t = uTime * 0.05;

  float sway = sin(t * 0.62) * 0.05 + uMouse.x * 0.038;
  float sx = uv.x - sway;

  float depth = clamp(0.62 - uv.y, 0.0, 2.0);
  float halfW = 0.030 + depth * 0.44;
  float edge = abs(sx) / halfW;

  float beam = exp(-pow(edge, 2.2));
  beam *= 1.0 - smoothstep(0.78, 1.62, depth) * 0.82;

  float core = exp(-pow(edge * 3.6, 2.0)) * (1.0 - smoothstep(0.30, 1.1, depth));
  float m = motes(uv, t) * beam;

  vec3 warm = vec3(1.0, 0.58, 0.33);
  vec3 cold = vec3(0.52, 0.68, 1.0);
  vec3 col = vec3(0.035, 0.032, 0.045);

  col += warm * beam * 0.17;
  col += mix(warm, cold, smoothstep(0.0, 1.35, depth)) * m * 1.35;
  col += warm * core * 0.30;

  // a faint bounce of light on the floor of the frame
  float floorGlow = exp(-pow(length(vec2(sx * 1.3, uv.y + 0.46)) / 0.30, 2.0));
  col += warm * floorGlow * 0.05;

  float vig = 1.0 - smoothstep(0.42, 1.22, length(uv * vec2(1.0, 0.92)));
  col *= 0.30 + 0.70 * vig;
  col += (hash(gl_FragCoord.xy + fract(uTime) * 41.0) - 0.5) * 0.025;

  gl_FragColor = vec4(col, 1.0);
}`;

  function initShader() {
    if (!canvas) return;
    gl = canvas.getContext("webgl", { antialias: false, alpha: false, powerPreference: "high-performance" });
    if (!gl) return;
    const compile = (type, src) => {
      const s = gl.createShader(type);
      gl.shaderSource(s, src);
      gl.compileShader(s);
      return gl.getShaderParameter(s, gl.COMPILE_STATUS) ? s : null;
    };
    const vs = compile(gl.VERTEX_SHADER, VERT);
    const fs = compile(gl.FRAGMENT_SHADER, FRAG);
    if (!vs || !fs) return;
    program = gl.createProgram();
    gl.attachShader(program, vs);
    gl.attachShader(program, fs);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return;
    gl.useProgram(program);

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(program, "a");
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

    uniforms = {
      uRes: gl.getUniformLocation(program, "uRes"),
      uTime: gl.getUniformLocation(program, "uTime"),
      uMouse: gl.getUniformLocation(program, "uMouse")
    };
    resizeShader();
    canvas.classList.add("is-live");
  }

  const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  function resizeShader() {
    if (!gl) return;
    const dpr = Math.min(window.devicePixelRatio || 1, innerWidth < 700 ? 1 : 1.5);
    canvas.width = Math.round(canvas.clientWidth * dpr);
    canvas.height = Math.round(canvas.clientHeight * dpr);
    gl.viewport(0, 0, canvas.width, canvas.height);
    if (uniforms.uRes) gl.uniform2f(uniforms.uRes, canvas.width, canvas.height);
  }

  function drawShader(time) {
    if (!gl || !program) return;
    mouse.x = lerp(mouse.x, mouse.tx, 0.12);
    mouse.y = lerp(mouse.y, mouse.ty, 0.12);
    if (uniforms.uMouse) gl.uniform2f(uniforms.uMouse, mouse.x, mouse.y);
    gl.uniform1f(uniforms.uTime, time);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  /* — 2 · reveal on entry ------------------------------------------------ */
  const revealEls = Array.from(document.querySelectorAll(".reveal"));
  if ("IntersectionObserver" in window && !reduced.matches) {
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      }
    }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add("in"));
  }

  /* — 3 · reader: word clock + waveform ---------------------------------- */
  const prose = document.getElementById("prose");
  const words = [];
  if (prose) {
    const parts = prose.textContent.trim().split(/\s+/);
    prose.textContent = "";
    parts.forEach((w) => {
      const span = document.createElement("span");
      span.textContent = w;
      prose.appendChild(span);
      prose.appendChild(document.createTextNode(" "));
      words.push(span);
    });
  }

  const waveEl = document.getElementById("wave");
  const wctx = waveEl ? waveEl.getContext("2d") : null;
  const clockEl = document.getElementById("clock");

  function sizeCanvas(c, maxDpr) {
    const dpr = Math.min(window.devicePixelRatio || 1, maxDpr || 2);
    const w = c.clientWidth, h = c.clientHeight;
    if (c.width !== Math.round(w * dpr) || c.height !== Math.round(h * dpr)) {
      c.width = Math.round(w * dpr);
      c.height = Math.round(h * dpr);
    }
    return dpr;
  }

  function drawWave(time) {
    if (!wctx) return;
    const dpr = sizeCanvas(waveEl, 2);
    const w = waveEl.width, h = waveEl.height;
    if (!w || !h) return;
    wctx.clearRect(0, 0, w, h);
    const bars = Math.max(28, Math.floor(w / (9 * dpr)));
    const bw = w / bars;
    const phase = (time % 41) / 41;
    for (let i = 0; i < bars; i++) {
      const p = i / bars;
      const env = Math.sin(p * Math.PI) * 0.72 + 0.28;
      const mod =
        0.5 +
        0.5 * Math.sin(p * 17 + time * 2.1) * Math.sin(p * 5 - time * 0.7) +
        0.22 * Math.sin(p * 41 + time * 3.7);
      const bh = clamp(mod * env, 0.08, 1) * h * 0.82;
      const x = i * bw + bw * 0.22;
      wctx.fillStyle = p < phase ? "rgba(228,105,58,.85)" : "rgba(242,235,223,.15)";
      wctx.fillRect(x, (h - bh) / 2, Math.max(1.5 * dpr, bw * 0.5), bh);
    }
  }

  function updateReader(time) {
    if (!words.length) return;
    const per = document.body.classList.contains("is-speaking") ? 0.2 : 0.27;
    const idx = Math.floor(time / per) % words.length;
    for (let i = 0; i < words.length; i++) {
      const w = words[i];
      const cls = i === idx ? "lit" : i < idx ? "done" : "";
      if (w.className !== cls) w.className = cls;
    }
    if (clockEl) {
      const secs = 6 + (idx / words.length) * 35;
      clockEl.innerHTML =
        Math.floor(secs / 60) + ":" + String(Math.floor(secs % 60)).padStart(2, "0") + "<span> / 0:41</span>";
    }
  }

  /* — 4 · Opsis: scroll scrub -------------------------------------------- */
  const opsis = document.querySelector(".opsis");
  const frames = Array.from(document.querySelectorAll(".opsis__frame"));
  const beatsEl = document.getElementById("beats");
  const playhead = document.getElementById("playhead");
  const hudTime = document.getElementById("hud-time");
  const slateShot = document.getElementById("slate-shot");
  const slateTake = document.getElementById("slate-take");
  const TOTAL = 12 * 60 + 3;

  const BEAT_WIDTHS = [5, 3, 6, 4, 7, 3, 5, 4, 6, 3, 5, 5, 3, 6, 4, 5, 3, 6, 4, 5, 4, 4];
  if (beatsEl) {
    BEAT_WIDTHS.forEach((w, i) => {
      const b = document.createElement("i");
      b.style.flex = w + " 1 0";
      if (i === 8 || i === 15) b.className = "void";
      beatsEl.appendChild(b);
    });
  }
  const beats = beatsEl ? Array.from(beatsEl.children) : [];
  const SHOTS = [3, 4, 5, 7, 12, 17, 19, 21];
  const TAKES = ["b2", "b1", "b0", "b1", "b2", "b2", "b0", "b0"];
  let activeFrame = 0, activeBeat = 0;

  function updateOpsis() {
    if (!opsis || !frames.length) return;
    if (reduced.matches || innerWidth <= 900) return;
    const rect = opsis.getBoundingClientRect();
    const span = opsis.offsetHeight - state.vh;
    const progress = clamp(-rect.top / Math.max(1, span), 0, 1);

    const idx = Math.min(frames.length - 1, Math.floor(progress * frames.length));
    if (idx !== activeFrame) {
      frames[activeFrame].classList.remove("is-on");
      frames[idx].classList.add("is-on");
      activeFrame = idx;
      if (slateShot) slateShot.textContent = "SHOT " + String(SHOTS[idx]).padStart(2, "0") + " / 22";
      if (slateTake) slateTake.textContent = "TAKE " + TAKES[idx];
    }

    const beat = Math.min(beats.length - 1, Math.floor(progress * beats.length));
    if (beat !== activeBeat) {
      beats.forEach((b, i) => b.classList.toggle("past", i <= beat && !b.classList.contains("void")));
      activeBeat = beat;
    }

    if (playhead) playhead.style.left = (progress * 100).toFixed(3) + "%";
    if (hudTime) hudTime.textContent = mmss(progress * TOTAL);
  }

  /* — 5 · nav, rail, hero parallax --------------------------------------- */
  const nav = document.querySelector(".nav");
  const rail = document.querySelector(".rail i");
  const heroInner = document.querySelector(".hero__inner");
  const heroFoot = document.querySelector(".hero__foot");

  function updateScrollUI() {
    state.y = window.scrollY;
    if (nav) nav.classList.toggle("is-scrolled", state.y > 40);
    if (rail) {
      const p = clamp(state.y / Math.max(1, state.docH - state.vh), 0, 1);
      rail.style.width = (p * 100).toFixed(2) + "%";
    }
    if (heroInner && !reduced.matches) {
      const p = clamp(state.y / state.vh, 0, 1);
      heroInner.style.transform = "translate3d(0," + (p * -46).toFixed(1) + "px,0)";
      heroInner.style.opacity = (1 - p * 0.85).toFixed(3);
      if (heroFoot) heroFoot.style.opacity = (1 - p * 1.4).toFixed(3);
    }
  }

  /* — 6 · lamp ----------------------------------------------------------- */
  const lamp = document.createElement("div");
  lamp.className = "lamp";
  lamp.setAttribute("aria-hidden", "true");
  document.body.appendChild(lamp);
  const ptr = { x: innerWidth / 2, y: innerHeight / 2 };
  const lampPos = { x: innerWidth / 2, y: innerHeight / 2 };
  const canLamp = finePointer.matches && !reduced.matches;
  window.addEventListener("pointermove", (e) => {
    ptr.x = e.clientX;
    ptr.y = e.clientY;
    mouse.tx = (e.clientX / innerWidth) * 2 - 1;
    mouse.ty = -((e.clientY / innerHeight) * 2 - 1);
    if (canLamp) lamp.classList.add("is-on");
  }, { passive: true });

  /* — 7 · sound (opt in, never autoplay) --------------------------------- */
  const hear = document.getElementById("hear");
  let audio = null;
  function toggleSound() {
    if (!hear) return;
    if (!audio) {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      const ctx = new Ctx();
      const master = ctx.createGain();
      master.gain.value = 0;
      const filter = ctx.createBiquadFilter();
      filter.type = "lowpass";
      filter.frequency.value = 820;
      filter.Q.value = 0.6;
      [130.81, 196.0, 261.63].forEach((f, i) => {
        const o = ctx.createOscillator();
        o.type = i === 2 ? "triangle" : "sine";
        o.frequency.value = f;
        o.detune.value = (i - 1) * 5;
        const g = ctx.createGain();
        g.gain.value = i === 2 ? 0.16 : 0.3;
        o.connect(g).connect(filter);
        o.start();
      });
      const lfo = ctx.createOscillator();
      const lfoGain = ctx.createGain();
      lfo.frequency.value = 0.23;
      lfoGain.gain.value = 0.06;
      lfo.connect(lfoGain).connect(master.gain);
      lfo.start();
      filter.connect(master).connect(ctx.destination);
      audio = { ctx, master, on: false };
    }
    const now = audio.ctx.currentTime;
    audio.on = !audio.on;
    audio.master.gain.cancelScheduledValues(now);
    audio.master.gain.setTargetAtTime(audio.on ? 0.05 : 0, now, audio.on ? 0.6 : 0.25);
    if (audio.on) audio.ctx.resume();
    hear.classList.toggle("is-playing", audio.on);
    hear.setAttribute("aria-label", audio.on ? "Stop the tone" : "Play a soft tone");
    document.body.classList.toggle("is-speaking", audio.on);
  }
  if (hear) hear.addEventListener("click", toggleSound);

  /* — 8 · the loop ------------------------------------------------------- */
  function tick(now) {
    const time = (now - state.t0) / 1000;
    updateScrollUI();
    updateOpsis();
    if (!reduced.matches) {
      drawShader(time);
      drawWave(time);
      if (heroVisible) updateReader(time);
    }

    if (canLamp) {
      lampPos.x = lerp(lampPos.x, ptr.x, 0.085);
      lampPos.y = lerp(lampPos.y, ptr.y, 0.085);
      lamp.style.transform = "translate3d(" + lampPos.x.toFixed(1) + "px," + lampPos.y.toFixed(1) + "px,0)";
    }
    requestAnimationFrame(tick);
  }

  /* — 9 · boot ----------------------------------------------------------- */
  initShader();

  if (reduced.matches) {
    if (gl) drawShader(12.5);      // a single still of the beam
    updateReader(3.2);
    drawWave(9.5);
  }

  if ("IntersectionObserver" in window && canvas) {
    new IntersectionObserver((entries) => {
      heroVisible = entries[0].isIntersecting;
    }, { threshold: 0 }).observe(canvas);
  }

  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => { measure(); resizeShader(); updateOpsis(); }, 150);
  }, { passive: true });

  updateScrollUI();
  updateOpsis();
  requestAnimationFrame(tick);
})();
