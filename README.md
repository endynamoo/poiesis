# Poiesis

**Poiesis** — the making. The third of Aristotle's words, after [Rhapsode](https://github.com/endynamoo/rhapsode)
(the reciter) and [Opsis](https://github.com/endynamoo/opsis) (the spectacle): one site
presenting both as working local-first AI products, built end to end.

One page, five movements: a spotlight through dust, a reader where the spoken word lifts off
the page, a film stage scrubbed by scroll, four receipts about how the work is made, and a
way to get in touch.

Live at **https://endynamoo.github.io/poiesis/**.

## What it is

- **Static and self-contained.** Hand-written HTML, CSS and JavaScript. No framework, no
  build step, no CDN, no analytics, no third-party request at runtime. The display face is
  self-hosted; the body uses whatever the visitor's system already renders best.
- **Real stills, drawn interface.** The Opsis stage uses eight actual frames from the
  chapter-one pipeline, not stock imagery. The Rhapsode window is drawn in CSS so it stays
  crisp on any display instead of showing a dated screenshot.
- **Motion with a still version.** A WebGL hero, scroll-driven reveals and a pinned film
  stage — all of which honour `prefers-reduced-motion`, pause off-screen, and degrade to a
  readable page when the shader cannot start.

```
index.html
assets/css/site.css        the visual system
assets/js/site.js          shader, clock, scrub, reveals, opt-in tone
assets/img/*.webp          eight stills + the social card
assets/fonts/*.woff2       Instrument Serif (SIL OFL 1.1, licence beside it)
tools/changelog_render.py  README changelog generator
tests/                     site and changelog checks
```

## Run it locally

```powershell
python -m http.server 8137
# http://localhost:8137
```

There is nothing to install: no `requirements.txt`, no `node_modules`.

## Verify

```powershell
python -m unittest discover -s tests -v
```

`tests/test_site.py` reads `index.html` and checks that every local `src` and `href`
resolves, that there is exactly one `h1`, that every image carries an `alt`, that no
resource loads from another origin, and that every in-page anchor has a target.
`tests/test_changelog.py` checks the block at the bottom of this file.

## Deploy

Push to `main`. `.github/workflows/pages.yml` publishes the repository root to GitHub Pages;
`.github/workflows/check.yml` runs the suite on every push and pull request.

## Licence

MIT — see [LICENSE](LICENSE). The typeface is licensed separately under the SIL Open Font
License 1.1, in [assets/fonts/OFL.txt](assets/fonts/OFL.txt).

<!-- CHANGELOG:BEGIN -->
## Changelog

Newest first. The full history is in [CHANGELOG.md](CHANGELOG.md); this block is generated from it by `tools/changelog_render.py`, so edit the changelog, not this copy.

### Unreleased

**Added**

- The Poiesis site: one scrolling page that presents **Rhapsode** and **Opsis** as working local-first AI products rather than screenshots and adjectives, and says who built them.
- A WebGL hero: a single warm spotlight through drifting dust that leans toward the pointer, painted at capped resolution, paused off-screen, and frozen to one still frame when the visitor asks for reduced motion.
- The Rhapsode reader drawn in HTML and CSS — a passage from the *Meditations* where the spoken word lifts to paper-white, a waveform that follows the same clock, and an opt-in WebAudio tone so the movement is not decoration.
- The Opsis stage: eight real stills from chapter one of the pipeline, dissolved by scroll against a beat timeline with a moving playhead and a running timecode. The same frames become a swipeable storyboard strip on phones.
- Four "receipts" in the making section: local by construction, one door to the GPU, verified not vibed, and built with agents answered by tests — each with measured numbers.
- A generated social card, an SVG favicon, Open Graph and Twitter metadata, and a self-hosted display face so the page makes no third-party requests at runtime.
- `tools/changelog_render.py` and `tests/test_changelog.py`, the same generated-README changelog rule as the sibling repos.

*...and 4 more entries in [CHANGELOG.md](CHANGELOG.md).*

<!-- CHANGELOG:END -->
