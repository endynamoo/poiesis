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

  /* — 3 · reader: the real voice ---------------------------------------- */
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

  const voice = document.getElementById("voice");
  const waveEl = document.getElementById("wave");
  const wctx = waveEl ? waveEl.getContext("2d") : null;
  const clockEl = document.getElementById("clock");
  const hear = document.getElementById("hear");

  /* phoneme timings, rendered into the page by tools/make_reader_audio.py */
  let timings = null;
  const timingsEl = document.getElementById("reader-timings");
  if (timingsEl) {
    try {
      timings = JSON.parse(timingsEl.textContent);
    } catch (err) {
      timings = null;
    }
  }
  let duration = timings ? timings.duration : 0;
  let lastWord = -1;

  const timecode = (s) => {
    s = Math.max(0, Math.floor(s || 0));
    return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0");
  };

  function setClock(t) {
    if (!clockEl) return;
    clockEl.innerHTML = timecode(t) + "<span> / " + timecode(duration) + "</span>";
  }

  function wordAt(t) {
    if (!timings) return -1;
    const list = timings.words;
    for (let i = list.length - 1; i >= 0; i--) {
      if (t >= list[i][0]) return i;
    }
    return -1;
  }

  function paintWords(idx) {
    if (idx === lastWord || !words.length) return;
    for (let i = 0; i < words.length; i++) {
      const cls = i === idx ? "lit" : i < idx ? "done" : "";
      if (words[i].className !== cls) words[i].className = cls;
    }
    lastWord = idx;
  }

  function sizeCanvas(c, maxDpr) {
    const dpr = Math.min(window.devicePixelRatio || 1, maxDpr || 2);
    const w = c.clientWidth, h = c.clientHeight;
    if (c.width !== Math.round(w * dpr) || c.height !== Math.round(h * dpr)) {
      c.width = Math.round(w * dpr);
      c.height = Math.round(h * dpr);
    }
    return dpr;
  }

  /* the clip's own waveform while it plays; a resting envelope until it has */
  let actx = null, analyser = null, samples = null, wired = false;
  const history = [];
  function wireAudio() {
    if (wired || !voice) return;
    wired = true;
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      actx = new Ctx();
      const source = actx.createMediaElementSource(voice);
      analyser = actx.createAnalyser();
      analyser.fftSize = 2048;
      analyser.smoothingTimeConstant = 0;
      source.connect(analyser).connect(actx.destination);
      samples = new Uint8Array(analyser.fftSize);
    } catch (err) {
      analyser = null;   // the element still plays, just without the waveform
    }
  }

  function drawWave(progress, time, playing) {
    if (!wctx) return;
    const dpr = sizeCanvas(waveEl, 2);
    const w = waveEl.width, h = waveEl.height;
    if (!w || !h) return;
    wctx.clearRect(0, 0, w, h);
    const bars = Math.max(28, Math.floor(w / (9 * dpr)));
    const bw = w / bars;
    const live = analyser && playing;

    if (live) {
      analyser.getByteTimeDomainData(samples);
      let peak = 0;
      for (let j = 0; j < samples.length; j += 3) {
        const v = Math.abs(samples[j] - 128) / 128;
        if (v > peak) peak = v;
      }
      history.push(clamp(Math.pow(peak, 0.55) * 1.3, 0.03, 1));
      if (history.length > 260) history.shift();
    }

    for (let i = 0; i < bars; i++) {
      const p = i / bars;
      let level;
      if (history.length > 8) {
        // the last couple of seconds of the real signal, scrolling right to left
        const n = history.length;
        const from = n - Math.min(n, bars * 2);
        level = history[Math.min(n - 1, Math.floor(from + p * (n - from)))];
      } else {
        const env = Math.sin(p * Math.PI) * 0.62 + 0.24;
        const mod =
          0.5 +
          0.5 * Math.sin(p * 11 + 1.7) * Math.sin(p * 4 - 0.6) +
          0.2 * Math.sin(p * 23 + time * 0.35);
        level = clamp(mod * env, 0.08, 1);
      }
      const bh = level * h * 0.86;
      const x = i * bw + bw * 0.22;
      const played = (i + 0.5) / bars <= progress;
      wctx.fillStyle = played ? "rgba(228,105,58,.9)" : "rgba(242,235,223,.16)";
      wctx.fillRect(x, (h - bh) / 2, Math.max(1.5 * dpr, bw * 0.5), bh);
    }
  }

  function syncButton() {
    if (!hear || !voice) return;
    const playing = !voice.paused && !voice.ended;
    hear.classList.toggle("is-playing", playing);
    hear.setAttribute("aria-pressed", playing ? "true" : "false");
    hear.setAttribute("aria-label", playing ? "Pause the voice" : "Play the voice");
  }

  function updateReader(time) {
    if (!voice) return;
    const t = voice.currentTime || 0;
    const playing = !voice.paused && !voice.ended;
    paintWords(wordAt(t));
    setClock(t);
    drawWave(duration ? Math.min(1, t / duration) : 0, time, playing);
  }

  if (voice) {
    voice.addEventListener("loadedmetadata", () => {
      if (voice.duration && isFinite(voice.duration)) duration = voice.duration;
      setClock(voice.currentTime || 0);
    });
    voice.addEventListener("play", syncButton);
    voice.addEventListener("pause", syncButton);
    voice.addEventListener("ended", () => {
      voice.currentTime = 0;
      paintWords(-1);
      setClock(0);
      syncButton();
    });
    if (hear) {
      hear.addEventListener("click", async () => {
        if (voice.paused || voice.ended) {
          wireAudio();
          if (actx && actx.state === "suspended") await actx.resume();
          try {
            await voice.play();
          } catch (err) {
            syncButton();
          }
        } else {
          voice.pause();
        }
      });
    }
    setClock(0);
    syncButton();
  }

  /* — 4 · Opsis: scroll scrub -------------------------------------------- */
  const opsis = document.querySelector(".opsis");
  const pinned = window.matchMedia("(min-width: 901px) and (min-height: 761px)");
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
    if (reduced.matches || !pinned.matches) return;
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

  /* — 7 · the loop ------------------------------------------------------- */
  function tick(now) {
    const time = (now - state.t0) / 1000;
    updateScrollUI();
    updateOpsis();
    if (!reduced.matches) {
      drawShader(time);
      updateReader(time);
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
    updateReader(0);
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
