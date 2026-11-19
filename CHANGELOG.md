# Changelog

Newest first. Every change lands here in the same commit, under `Unreleased`, and moves
under a version heading when one is cut. `python tools/changelog_render.py` mirrors the top
of this file into the README; `tests/test_changelog.py` fails when that copy is stale.

## [Unreleased]

### Added

- The Poiesis site: one scrolling page that presents **Rhapsode** and **Opsis** as working
  local-first AI products rather than screenshots and adjectives, and says who built them.
- A WebGL hero: a quasar — black event horizon, photon ring, a tilted disk of violet
  ellipses, twin jets — turning over drifting dust and leaning toward the pointer, painted at
  capped resolution, paused off-screen, and frozen to one still frame when the visitor asks
  for reduced motion.
- The Rhapsode reader drawn in HTML and CSS — a passage from the *Meditations* where the
  spoken word lifts to paper-white, a waveform that follows the same clock, and an opt-in
  WebAudio tone so the movement is not decoration.
- The Opsis stage: eight real stills from chapter one of the pipeline, dissolved by scroll
  against a beat timeline with a moving playhead and a running timecode. The same frames
  become a swipeable storyboard strip on phones.
- Four "receipts" in the making section: local by construction, one door to the GPU,
  verified not vibed, and built with agents answered by tests — each with measured numbers.
- A generated social card, an SVG favicon, Open Graph and Twitter metadata, and a
  self-hosted display face so the page makes no third-party requests at runtime.
- `tools/changelog_render.py` and `tests/test_changelog.py`, the same generated-README
  changelog rule as the sibling repos.
- `tests/test_site.py`: every local `src`/`href` in the page resolves, there is exactly one
  `h1`, every image has an `alt`, and nothing loads from another origin.
- GitHub Pages deployment and a CI check on push and pull request.

### Changed

- The whole page wears **Rhapsode's palette** instead of its own warm one: violet signal
  (`#8b7bff`) on near-black (`#07070d`), cyan (`#5fd8f5`) as the second voice, and paper
  tinted the same violet (`#ece9f8`). Contrast was re-measured, not assumed — body text
  16.8:1, accent on ground 6.1:1, secondary 7.6:1, all AA. Opsis keeps its warm stills; only
  the frame around them belongs to the brand.
- The reader's play button plays **Kokoro-82M speaking the passage**, not a synthesised
  placeholder tone. `tools/make_reader_audio.py` renders the clip from the Rhapsode
  install, writes the phoneme timings into the page, and the highlight, the timecode and
  the waveform all follow the audio itself — the bars are the clip's own signal.
- The Opsis capability chips sit in a two-column grid with content-sized pills and
  left-aligned labels, so all four labels line up on two clean edges instead of each
  floating at a different x. Asset URLs carry a `?v=` so a stylesheet change is not
  masked by the browser cache.

### Removed

- The public deployment, for now. The repository is private while the page is finished, and
  GitHub Pages does not publish from a private repository on a free account, so
  `endynamoo.github.io/poiesis` is offline until the repository is public again or the site
  moves to a host that serves private repositories. The deploy workflow is kept, manual-only.

### Fixed

- The Opsis stage no longer pins itself on a short window. Below 760 px of viewport height
  it becomes a static plate — still, storyboard, copy, timeline — so the capability chips
  can no longer run into the timeline rail, which is exactly what a wide, short window was
  doing. The scrub and the live timecode only run while the stage is genuinely pinned.
- The page's text is UTF-8 end to end, and `tests/test_site.py` now fails if a PowerShell
  read/write cycle double-encodes it into `â€"` and `Â·`.
- The Opsis slate and the storyboard captions name the shot and take each frame really is
  (03–21 of 22), rather than a running index.
- The social card is referenced by its absolute Pages URL, so link previews resolve when
  the site is served from a subpath rather than a domain root.
