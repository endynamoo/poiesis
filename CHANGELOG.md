# Changelog

Newest first. Every change lands here in the same commit, under `Unreleased`, and moves
under a version heading when one is cut. `python tools/changelog_render.py` mirrors the top
of this file into the README; `tests/test_changelog.py` fails when that copy is stale.

## [Unreleased]

### Added

- The Poiesis site: one scrolling page that presents **Rhapsode** and **Opsis** as working
  local-first AI products rather than screenshots and adjectives, and says who built them.
- A WebGL hero: a single warm spotlight through drifting dust that leans toward the pointer,
  painted at capped resolution, paused off-screen, and frozen to one still frame when the
  visitor asks for reduced motion.
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

- Nothing yet — 0.1.0 is the first cut.

### Fixed

- The Opsis slate and the storyboard captions name the shot and take each frame really is
  (03–21 of 22), rather than a running index.
- The social card is referenced by its absolute Pages URL, so link previews resolve when
  the site is served from a subpath rather than a domain root.
