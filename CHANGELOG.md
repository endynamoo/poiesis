# Changelog

Newest first. Every change lands here in the same commit, under `Unreleased`, and moves
under a version heading when one is cut. `python tools/changelog_render.py` mirrors the top
of this file into the README; `tests/test_changelog.py` fails when that copy is stale.

## [Unreleased]

### Added

- **The look is a field, shown four ways.** One beat of chapter one rendered as four art
  styles — the shipped warm cel, a black-ink woodcut, a ukiyo-e woodblock and neo-noir — all
  from the same identity, beat, seed, size and four steps, with only the style string changed.
  The grid explains the mechanism the product actually uses: every keyframe is composed as
  *identity + style + scene*, the same style line goes to the motion model, and the director is
  told not to invent a colour the style does not name. Rendered on this machine by
  `tools/make_style_variants.py`, which calls Opsis's own keyframe composition.
- **Opsis footage, from the pipeline itself.** Thirty-five seconds cut from four of the
  twenty-two shots that made chapter one — keyframes painted with FLUX.2 klein, motion
  generated with Wan 2.2 on the local card, narration spoken by Chatterbox Turbo, the source
  being Faraday's own 1831 *Experimental Researches*. It sits under the Opsis stage with a
  shot-by-shot transcript. Every cut lands in a pause the narration leaves between sentences,
  so the voice finishes its thought before the picture changes. Because a pre-alpha shown
  beside a shipped product reads as shipped, it is labelled **Alpha footage** twice: a violet
  pill beside the slate, and the first words of the caption.
- The **Rhapsode demo**, embedded: one unedited 65-second take recorded by the app's own
  `scripts/record_demo.py` — library, Kokoro reading with the words lighting up, a search
  that finds the phrase, a chapter film assembled from stills, then the settings that decide
  what the machine may do on its own. Re-encoded to 2 MB (1280 px, CRF 30, mono AAC) with a
  poster frame from the film beat, a written caption, and a timestamped transcript of what is
  on screen, since the take carries the app's own narration rather than captions.
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

- **The Opsis footage no longer cuts sentences in half.** The first cut took a flat six seconds
  from each shot, which chopped the narration mid-thought. Each cut now lands in a pause the
  voice itself makes — found with `silencedetect` on the source clips and confirmed after the
  join: every seam ends in −48 to −54 dB of room tone, and the shots are joined with hard cuts
  instead of fading both ends to black, because the double fade put a dead black frame between
  them. The clip is 35 seconds now, not 24.
- **Each demo silences the other.** Pressing play on the footage pauses the reader's voice and
  vice versa, so the page never talks over itself. A take paused from its own controls gets its
  play pill back.
- **The opening line now says what I actually do.** "I make machines…" was the wrong claim;
  it reads **I develop software that reads books — and software that films them.** The social
  card was re-rendered to match, since the headline is baked into it.
- **The page says whose software this is.** "To empower." now leads the byline under the
  hero, followed by *built in the open at endynamoo — it's our software, not mine, and it
  stays free forever*. The solo framing is gone everywhere: *The making* now says the work is
  built in the open by everyone who shows up, the close section invites the code to be taken,
  and the footer reads *the products are MIT: our software, free forever*. The hero meta says
  `MIT · free forever` instead of just `MIT`.
- **The Rhapsode panel is current with 0.3.4-beta** instead of describing 0.2.0: on-device
  translation through Apple's framework or a local model, library search by words or by
  meaning, the warm-ahead cache that makes the first press of play instant, and spec rows
  rewritten to what the repo actually ships (voice and languages, formats incl. URL, search,
  platforms and 0.75–3×). The demo slate no longer pins a version the take was not recorded
  from.
- **The Opsis stage says it is unreleased.** A banner sits on the frame beside the shot slate —
  violet beacon, `Unreleased · ETA ~2 weeks to public beta` — so a pre-alpha is not read as a
  shipped product. It is real text, not decoration, so it is announced too.
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

- **The reader's first press no longer pays for the audio.** The clip is preloaded and
  fetched, and the analyser graph is built, while the reader is still looking at the page —
  and playback is no longer gated behind `AudioContext.resume()`, which used to sit in front
  of the first frame. This is Rhapsode's `044b2a7` (*warm the sentence on screen before play
  is pressed*, 1257 ms → 75 ms to first sound) applied to a page whose clip is a file rather
  than a synthesis. Instrumented run: the audio graph used to be constructed inside the click
  (created 1204 ms, press 1201 ms); it is now built 905 ms before the press, and press →
  first frame measures 5–15 ms locally.
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
