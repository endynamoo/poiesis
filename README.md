# Poiesis

**Poiesis** — the making. The third of Aristotle's words, after [Rhapsode](https://github.com/endynamoo/rhapsode)
(the reciter) and [Opsis](https://github.com/endynamoo/opsis) (the spectacle): one site
presenting both as working local-first AI products, built end to end.

One page, five movements: a quasar turning over drifting dust, a reader where the spoken word
lifts off the page, a film stage scrubbed by scroll, four receipts about how the work is made,
and a way to get in touch.

Live at **https://endynamoo.github.io/poiesis/** — the repository is public and Pages deploys
it on every push to `main`. Run it locally with the command below when you want to review a
working tree before it ships.

## What it is

- **Static and self-contained.** Hand-written HTML, CSS and JavaScript. No framework, no
  build step, no CDN, no analytics, no third-party request at runtime. The display face is
  self-hosted; the body uses whatever the visitor's system already renders best.
- **Demos that are the product.** The page shows a real 65-second Rhapsode take, a 35-second
  Opsis montage cut where its narration pauses (labelled alpha), the same beat animated in four
  art styles, and translation samples produced by Rhapsode's own on-device translator - not
  mock-ups, and not stock footage.
- **Real stills, drawn interface.** The Opsis stage uses eight actual frames from the
  chapter-one pipeline, not stock imagery. The Rhapsode window is drawn in CSS so it stays
  crisp on any display instead of showing a dated screenshot.
- **Motion with a still version.** A WebGL hero, scroll-driven reveals and a pinned film
  stage - all of which honour `prefers-reduced-motion`, pause off-screen or behind a hidden
  tab, and degrade to a readable page when the shader cannot start.

```
index.html
assets/css/site.css         the visual system
assets/js/site.js           shader, reader voice, scrub, reveals, demo loops
assets/audio/reader.mp3     Kokoro-82M speaking the passage (105 KB)
assets/video/*.mp4          the two takes and the four style loops
assets/img/*.webp           eight stills, posters and the social card
assets/fonts/*.woff2        Instrument Serif (SIL OFL 1.1, licence beside it)
tools/make_reader_audio.py  re-renders the clip and its word timings
tools/make_opsis_demo.py    re-cuts the Opsis montage at the narration's pauses
tools/make_style_variants.py  the four keyframes of one beat
tools/make_style_clips.py   animates those four keyframes
tools/make_translation_demo.py  the translation samples, via Rhapsode's translator
tools/make_translation_clip.py  the 25-second take of a Spanish voice reading a translation
tools/changelog_render.py   README changelog generator
tests/                      site and changelog checks
```

The reader is not a mock-up of a voice: the clip was rendered by
`tools/make_reader_audio.py`, which calls the Rhapsode checkout's own Kokoro engine and
writes both the MP3 and the per-word phoneme timings into `index.html`. Change the passage
there, re-run the tool with Rhapsode's venv (`C:\Apps\Rhapsode\.venv\Scripts\python.exe
tools/make_reader_audio.py`), and the highlight stays in step.

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

- **The translation take.** A 25-second recording of the app reading a Spanish translation of an English page: the voice is `ef_dora`, the bar under the page carries each translated sentence, and the lit word is the Spanish word being spoken. Recorded by `tools/make_translation_clip.py`, which boots the app against a throwaway data directory and captures the audio the same way the Rhapsode take's is captured.
- **Translation samples, under the Rhapsode take.** The sentence the demo speaks, in Spanish, French, Japanese and Chinese — produced on this machine by the translator Rhapsode installs itself (Qwen2.5-7B-Instruct q4 through llama.cpp), 2.5–3.3 s a line. The caption names the model, says where it ran, notes that macOS uses Apple's framework instead, and explains why Hindi is absent: it looped on every local model measured here, so the app routes it to a server the reader runs.
- **The site is live.** `endynamoo.github.io/poiesis` publishes on every push to `main` again: the repository is public, Pages is configured with `build_type=workflow`, and the deploy workflow has its `push` trigger back.
- **The workflows run the current action majors** — `checkout@v7`, `setup-python@v7`, `configure-pages@v6`, `upload-pages-artifact@v5`, `deploy-pages@v5`. The old ones ran on a deprecated Node, and on two pushes in a row the deploy failed with "No artifacts named github-pages were found" while the upload step still reported success.

*...and 32 more entries in [CHANGELOG.md](CHANGELOG.md).*

<!-- CHANGELOG:END -->
