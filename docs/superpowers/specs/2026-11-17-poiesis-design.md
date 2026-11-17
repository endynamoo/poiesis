# Poiesis — portfolio site design

2026-11-17 · endynamoo

## What this is

A single-page portfolio site for two shipped AI products, **Rhapsode** (a book that
speaks) and **Opsis** (a book that becomes a film), presented as evidence of end-to-end
AI engineering. Audience: people who might hire or commission work. After twenty seconds
they should know three things: these are real, working, local-first products; the same
person built both ends of each one (model choice, pipeline, UI, packaging, CI); and the
engineering is disciplined, not demo-grade.

Non-goals: a blog, a CMS, a résumé, a contact form with a backend, analytics that phone
home. Anti-goal: anything that looks like a template — a wall of gradient cards with
"AI-powered" in every heading. If a visitor could swap in another developer's name and
the page still made sense, it has failed.

## Name and framing

The two products are already named after Aristotle's *Poetics*: **Rhapsode** (the reciter),
**Opsis** (the spectacle). The site is **Poiesis** — the making. That gives the page its
spine and its one-line thesis: *the making is the interesting part*. The brand on the page
stays `endynamoo`, the GitHub handle, so the site and both repos agree. No personal name,
no address, no phone number.

Repo: `github.com/endynamoo/poiesis`, **public** (GitHub Pages on a free account requires
it; a public source tree is also on-message for a portfolio about craft).

## The page

One continuous scroll, dark, lit like a stage. Five movements:

### 1. Hero — the light

Full viewport. A WebGL fragment shader paints a single warm spotlight cone through drifting
dust over near-black; it leans toward the pointer and breathes. Over it, in a high-contrast
serif:

> **I make machines that read books — and machines that film them.**

Eyebrow `ENDYNAMoo · POIESIS` small and letterspaced above. Below the headline, one
sentence: two products, built end to end, entirely on the machine in front of you — no
cloud, no accounts, no per-word billing. Two text links: `See the work ↓` and
`How it's built`. Bottom edge: a hairline scroll progress rail that fills as you read.

### 2. Signature strip

A slow marquee of the actual ingredients: `Kokoro-82M · FLUX.2 klein · Wan2.2 · ROCm ·
FastAPI · pywebview · PyInstaller · Inno Setup · GitHub Actions`. Pauses on hover and on
focus, and does not run at all under reduced motion.

### 3. Rhapsode — the voice made visible

Split layout, text left, a framed reader mock right. The mock is built in HTML/CSS (not a
screenshot) so it stays crisp at any DPI: a page of prose where the spoken word lifts to
paper-white while the rest sits at 40% ink, a soft waveform ribbon beneath it, and a small
transport row. The highlight advances word by word on a loop; the waveform is a canvas
that drifts with the same clock. No audio plays unless the visitor presses `hear it`, which
adds a quiet WebAudio tone so the motion is not arbitrary.

Copy is concrete: reads PDF, EPUB, DOCX, RTF, Markdown, a screenshot, a URL; OCR on-device
via Apple Vision / Windows.Media.Ocr / Tesseract; 54 voices across 9 languages; word
highlight from Kokoro's phoneme timings rather than a guess; 20 themes; Quick Read on one
hotkey; a chapter assemby into a 1080p MP4. Ends with `Rhapsode on GitHub →` and the
release line (`v0.2.0-alpha · MIT · Windows · macOS · Linux`).

### 4. Opsis — the still that moves

A pinned, full-bleed stage. Real stills from the pipeline (`shot03_b0/b1/b2`,
`shot07_b0/b1/b2`) sit in a horizontal film strip that travel as the section scrolls; the
largest frame dissolves between variants the way the app's chapter player does. Beneath,
a timeline bar of beats — hatched where a clip is missing, wider where the beat is longer
— with a playhead driven by scroll. Copy sits in a narrow column and names the boundary
that makes the product real: the app never holds a GPU context; it writes job files and a
worker behind a scheduled task renders them, so closing the window cannot kill a render.

Ends with `Opsis on GitHub →`, `v0.1.0-pre-alpha · MIT · Windows 11 · ROCm`, and one honest
sentence about what it is: a studio that is early, and works.

### 5. The making

Four columns, each a receipt rather than a claim:

- **Local by construction** — the model weights, audio cache, library and project folders
  are files on the visitor's disk; nothing is uploaded.
- **One door to the GPU** — quoted VRAM measured on the target card, the quant ladder, the
  four-step LoRA, the reserve the painter must leave. Numbers, not adjectives.
- **Verified, not vibed** — test counts, CI on `windows-latest`, the changelog rule, the
  licence audit that checks every weight file carries a permissive licence.
- **Built with agents, answered by tests** — the honest description of the workflow: coding
  agents do the typing, the suite, the CI run and the install test decide what survives.

### 6. Close

One line of invitation, a `mailto:` and the GitHub profile. Footer: `Poiesis · built on a
Windows box with an AMD card`, the site's own changelog link, and the year.

## Look

| Token | Value | Use |
|---|---|---|
| ink | `#0B0A0C` | page ground |
| ink-2 | `#141317` | panels |
| paper | `#F2EBDF` | body text on ink |
| ember | `#E4693A` | Rhapsode accent, links, focus |
| cold | `#8FB6FF` | Opsis accent, timeline |
| ash | `#8A8590` | secondary text, rules |

Type: **Instrument Serif** for display (self-hosted, two files, `woff2`, `font-display:
swap`), system sans (`Segoe UI Variable` / `-apple-system` / `Inter`) for body at 17–19px,
1.65 line height. Display sizes are fluid with `clamp()`. Text is never centred for longer
than a headline.

Texture: a fixed SVG-turbulence grain at 4–6% opacity, a vignette, and a 1px hairline grid
that only appears in the "making" section. No drop shadows heavier than 24px blur; borders
are 1px at 8–12% paper.

## Motion

Full showpiece, governed by three rules: nothing animates without a reason; nothing blocks
reading; everything has a still version.

- Shader hero: ~90 lines of GLSL, rendered at `min(devicePixelRatio, 1.5)`, paused when the
  tab is hidden or the canvas is off-screen. Static single frame under
  `prefers-reduced-motion` and on WebGL failure (CSS radial-gradient fallback).
- Scroll: native scrolling (no hijack). `requestAnimationFrame` reads a cached scroll value;
  parallax and the pinned stages are transform-only. Reveals are
  `IntersectionObserver`-driven, once per element, 700–900ms, cubic-bezier(.16,1,.3,1).
- Word highlight, waveform and playhead are one clock (elapsed time), so they never drift
  apart.
- Custom cursor: a 10px ember dot with a 40px lagging ring that grows over links; disabled
  for coarse pointers and reduced motion. Native cursor stays visible.
- Hover states are 180ms; nothing pulses forever except the strip marquee.

Budget: HTML+CSS+JS under 60 KB uncompressed, one hero shader, at most six still images at
`webp` ~1200px. Lighthouse ≥ 95 on mobile for performance and accessibility. No framework,
no build step, no CDN at runtime, no analytics.

## Responsive

Breakpoints at 1200 / 900 / 640. The two product sections collapse from split to stacked at
900; the Opsis stage loses its pin below 900 and becomes a swipeable strip with the same
stills; the timeline keeps its hatch language but scrolls horizontally. Type scales with
`clamp()` so nothing needs a second set of sizes. Tested at 360, 390, 768, 1024, 1440, 2560.

## Accessibility

Semantic landmarks, one `<h1>`, real links (no div-buttons), visible focus rings in ember,
`prefers-reduced-motion` honoured for every animation, alt text on the stills, contrast AA
on ink (paper 14:1, ember on ink 5.4:1 — checked, not assumed), and the shader canvas is
`aria-hidden` with the headline as real text.

## Files

```
index.html
assets/css/site.css
assets/js/site.js            shader, reveals, stage, cursor, clock
assets/fonts/instrument-serif-{regular,italic}.woff2
assets/img/frame-01..08.webp  eight stills from chapter one of the pipeline
assets/img/og.png            1200x630 social card
tools/changelog_render.py    same generator as Rhapsode/Opsis
tests/test_changelog.py      fails when the README copy is stale
.github/workflows/pages.yml  deploy on push to main
.github/workflows/check.yml  changelog + link check on PR
CHANGELOG.md                 running history
README.md                    what it is + generated changelog block
AGENTS.md                    repo rules (changelog, ASCII .ps1, verify)
```

## Decisions I made (check these)

1. **Static, no build.** Hand-written HTML/CSS/JS served by GitHub Pages. A portfolio about
   lean local software should not ship a 200 KB framework to show four paragraphs.
2. **Self-hosted display font, system body.** One extra network request, no CDN dependency,
   and body text inherits the visitor's preferred rendering.
3. **Real stills, mocked UI.** Opsis gets genuine pipeline output; Rhapsode's window is
   drawn in CSS so it never goes blurry and never shows a dated screenshot.
4. **No audio by default.** A single opt-in button; autoplay would be hostile.
5. **Public repo.** Required for free Pages, and consistent with the pitch.

## Accepted risks

- WebGL is the one fragile piece; it is decorative only, and every section reads fine
  without it.
- Six images is the whole asset budget, so the Opsis stage repeats them across variants;
  that repetition is the app's own dissolve behaviour, not padding.
- No custom domain yet; the site lives at `endynamoo.github.io/poiesis` until one is decided.
