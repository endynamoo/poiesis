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

Repo: `github.com/endynamoo/poiesis`, **public**, deployed by GitHub Pages on every push to
`main` - public is what free-tier Pages requires, and it is consistent with the pitch. It was
private from 2026-11-17 to 2026-11-26 while the page was finished, which took the site offline;
`.github/workflows/pages.yml` carries the note on how to put it back if that ever recurs.

## The page

One continuous scroll, dark, lit like a stage. Five movements:

### 1. Hero — the light

Full viewport. A WebGL fragment shader paints a quasar — the same figure as Rhapsode's mark:
a black event horizon, a bright photon ring, a tilted accretion disk of violet ellipses, and
twin cyan jets along the spin axis — with dust still drifting through the frame. It leans
toward the pointer and turns. Over it, in a high-contrast serif:

> **I develop software that reads books — and software that films them.**

Eyebrow `Poiesis · the making` small and letterspaced above. Below the headline, one
sentence: two products, built end to end, entirely on the machine in front of you — no
cloud, no accounts, no per-word billing. Then a byline that states the point plainly: **To
empower.** followed by *built in the open at endynamoo — it's our software, not mine, and it
stays free forever*. Authorship is the open-source kind: no solo framing anywhere on the page.
Two text links: `See the work ↓` and `How it's built`. Bottom edge: a hairline scroll progress
rail that fills as you read.

### 2. Signature strip

A slow marquee of the actual ingredients: `Kokoro-82M · FLUX.2 klein · Wan2.2 · ROCm ·
FastAPI · pywebview · PyInstaller · Inno Setup · GitHub Actions`. Pauses on hover and on
focus, and does not run at all under reduced motion.

### 3. Rhapsode — the voice made visible

Split layout, text left, a framed reader mock right. The mock is built in HTML/CSS (not a
screenshot) so it stays crisp at any DPI: a page of prose where the spoken word lifts to
paper-white while the rest sits at 40% ink, a waveform ribbon beneath it, and a small
transport row. The play button plays the passage in **Kokoro-82M's own voice**, rendered
offline by `tools/make_reader_audio.py` from the Rhapsode checkout; the highlight, the
timecode and the waveform all follow that audio, and the timing of each word is the
synthesis's phoneme timing rather than a guess.

Copy is concrete: reads PDF, EPUB, DOCX, RTF, Markdown, a screenshot, a URL; OCR on-device
via Apple Vision / Windows.Media.Ocr / Tesseract; 54 voices across 9 languages; word
highlight from Kokoro's phoneme timings rather than a guess; 20 themes; Quick Read on one
hotkey; a chapter assemby into a 1080p MP4. Ends with `Rhapsode on GitHub →` and the
release line (`v0.2.0-alpha · MIT · Windows · macOS · Linux`).

Then one unedited take of the app itself: 65 seconds recorded by Rhapsode's own
`scripts/record_demo.py`, library → reading → search → chapter film → settings, carrying the
app's Kokoro narration. It is a film frame rather than a screenshot — slate, poster, a
`Watch the demo` button, and a timestamped transcript for anyone who cannot hear it. It is
2 MB on disk and downloads nothing until pressed.

### 4. Opsis — the still that moves

A pinned, full-bleed stage. Real stills from the pipeline (`shot03_b0/b1/b2`,
`shot07_b0/b1/b2`) sit in a horizontal film strip that travel as the section scrolls; the
largest frame dissolves between variants the way the app's chapter player does. Beneath,
a timeline bar of beats — hatched where a clip is missing, wider where the beat is longer
— with a playhead driven by scroll. Copy sits in a narrow column and names the boundary
that makes the product real: the app never holds a GPU context; it writes job files and a
worker behind a scheduled task renders them, so closing the window cannot kill a render.

The frame carries a status banner beside the shot slate — violet beacon, `Unreleased · ETA
~2 weeks to public beta` — because a pre-alpha shown in the same frame as a shipped product
will be read as one. It sits at the top right in both the pinned stage and the static plate,
and it is real text rather than decoration, so it is announced to a screen reader too.

Ends with `Follow the build on GitHub ↗` — not the repository, which stays private until the
beta — and one honest sentence beside it: Opsis is MIT like its sibling, and its source opens
with the beta.

Then, outside the pinned stage, the footage: 35 seconds cut from four of the twenty-two
shots (03, 07, 12, 17) with a shot-by-shot transcript under it. Each cut lands in a pause the
narration leaves between sentences, so the voice finishes before the picture changes — the
seams were found with `silencedetect` on the source clips and checked again after the join.
It is marked **Alpha footage** in the slate pill and again as the caption's first words — a
pre-alpha next to a shipped product will otherwise be read as one. The voice on it is
Chatterbox Turbo, not Kokoro: the pipeline's own narration renderer, named so the page does
not imply otherwise.

After the take, the translation block: the sentence the film speaks, in four languages, with
the source line above it in the serif face and each language labelled in mono with its tag.
Under it, one paragraph that names the model, says it ran here, notes macOS uses Apple's
framework, and admits Hindi is missing because it looped locally — an absence with a reason
reads as honesty where a silent gap reads as an oversight. `tools/make_translation_demo.py`
regenerates it through Rhapsode's own translator; `docs/translation-demo.json` is the record,
and a test fails if the page and that file disagree.

After it, the style grid: one beat of chapter one rendered four ways — warm cel, woodcut,
ukiyo-e, neo-noir — and animated four times, since a still proves the palette and a clip
proves the film. Same identity, beat, seed, size and four steps; only the style string differs,
and the same string is handed to the motion model. Two columns of large tiles, not four
thumbnails, because the point is only visible at size. The caption names the mechanism instead
of admiring the pictures: `identity + style + scene`, the style line reaching the motion prompt,
and the director told not to invent a colour the style does not name. The loops start together
(one beat in four looks must not drift), stop off screen, and stay on their posters under
reduced motion. `tools/make_style_variants.py` renders the keyframes and
`tools/make_style_clips.py` animates them; both are committed with their inputs in
`docs/style-variants/`.

### 5. The making

Four columns, each a receipt rather than a claim, under one sentence about how it is made —
*started at endynamoo and built in the open by everyone who shows up; both products are MIT,
anyone can fork them, and they stay free forever*:

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
| ink | `#07070d` | page ground |
| ink-2 | `#0b0b15` | panels, footer |
| ink-3 | `#11111d` | raised panel (reader window) |
| paper | `#ece9f8` | body text on ink |
| accent | `#8b7bff` | brand violet: eyebrows, links, focus, playhead |
| accent-ink | `#0a0716` | text on an accent fill |
| cold | `#5fd8f5` | second voice: the hero's `film`, waveform peaks |
| ash | `#a09cbb` | secondary text, rules |

The palette is Rhapsode's own: violet signal on near-black, cyan as the second voice, paper
tinted the same violet rather than warm. Poiesis does not assert a new brand — it stands in
the same room as the two products it describes. Opsis keeps the warm stills; the frame
around them is the brand.

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

- The reader's voice is warmed before the press, the way Rhapsode warms the sentence on
  screen: `preload="auto"`, a cached fetch and the analyser graph built when the reader comes
  into view, and `play()` is never awaited behind `AudioContext.resume()`. The measurement is
  in the changelog: the graph now exists ~0.9 s before the click instead of inside it.

- Shader hero: ~100 lines of GLSL painting a quasar (event horizon, photon ring, ringed
  accretion disk, twin jets) at `min(devicePixelRatio, 1.5)`, paused when the tab is hidden
  or the canvas is off-screen. Static single frame under `prefers-reduced-motion` and on
  WebGL failure (CSS radial-gradient fallback).
- Scroll: native scrolling (no hijack). `requestAnimationFrame` reads a cached scroll value;
  parallax and the pinned stages are transform-only. Reveals are
  `IntersectionObserver`-driven, once per element, 700–900ms, cubic-bezier(.16,1,.3,1).
- Word highlight, waveform and playhead are one clock (elapsed time), so they never drift
  apart.
- Custom cursor: a 10px accent dot with a 40px lagging ring that grows over links; disabled
  for coarse pointers and reduced motion. Native cursor stays visible.
- Hover states are 180ms; nothing pulses forever except the strip marquee.

Budget: HTML+CSS+JS under 60 KB uncompressed, one hero shader, at most six still images at
`webp` ~1200px. Lighthouse ≥ 95 on mobile for performance and accessibility. No framework,
no build step, no CDN at runtime, no analytics.

## Responsive

Breakpoints at 1200 / 900 / 640. The two product sections collapse from split to stacked at
900; the Opsis stage loses its pin below 900 **and below 760 px of height** — pinning needs
vertical room, and a wide, short window otherwise pushes the chips into the timeline. Unpinned
it becomes a plate: still, storyboard strip, copy, timeline. Type scales with
`clamp()` so nothing needs a second set of sizes. Tested at 360, 390, 768, 1024, 1440, 2560.

## Accessibility

Semantic landmarks, one `<h1>`, real links (no div-buttons), visible focus rings in accent,
`prefers-reduced-motion` honoured for every animation, alt text on the stills, contrast AA
on ink (paper 16.8:1, accent on ink 6.1:1, ash 7.6:1 — checked, not assumed), and the shader
canvas is `aria-hidden` with the headline as real text.

## Files

```
index.html
assets/css/site.css
assets/js/site.js            shader, reveals, stage, cursor, clock
assets/fonts/instrument-serif-{regular,italic}.woff2
assets/img/frame-01..08.webp  eight stills from chapter one of the pipeline
assets/img/rhapsode-demo-poster.webp  the demo's film beat, shown before playback
assets/video/rhapsode-demo.mp4       the 65-second Rhapsode take, 2 MB
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
4. **Real media over generated stand-ins.** The reader's audio is a Kokoro clip rendered
   from the Rhapsode install by `tools/make_reader_audio.py`, and the word highlight reads
   that synthesis's phoneme timings; the Opsis frames are real pipeline output.
5. **Public repo.** Required for free Pages, and consistent with the pitch.

## Accepted risks

- WebGL is the one fragile piece; it is decorative only, and every section reads fine
  without it.
- Six images is the whole asset budget, so the Opsis stage repeats them across variants;
  that repetition is the app's own dissolve behaviour, not padding.
- No custom domain yet; the site lives at `endynamoo.github.io/poiesis` until one is decided.
