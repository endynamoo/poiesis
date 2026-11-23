# Poiesis

**Poiesis** — the making. The third of Aristotle's words, after [Rhapsode](https://github.com/endynamoo/rhapsode)
(the reciter) and [Opsis](https://github.com/endynamoo/opsis) (the spectacle): one site
presenting both as working local-first AI products, built end to end.

One page, five movements: a quasar turning over drifting dust, a reader where the spoken word
lifts off the page, a film stage scrubbed by scroll, four receipts about how the work is made,
and a way to get in touch.

Live at **https://endynamoo.github.io/poiesis/** — *currently unpublished.* The repository is
private while the site is finished, and GitHub Pages only publishes from private repositories
on a paid plan. Run it locally (below) or make the repository public again to bring the URL
back; see `.github/workflows/pages.yml`.

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
assets/js/site.js          shader, reader voice, scrub, reveals
assets/audio/reader.mp3    Kokoro-82M speaking the passage (105 KB)
assets/img/*.webp          eight stills + the social card
assets/fonts/*.woff2       Instrument Serif (SIL OFL 1.1, licence beside it)
tools/make_reader_audio.py re-renders the clip and its word timings
tools/changelog_render.py  README changelog generator
tests/                     site and changelog checks
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

- **The look is a field, shown four ways.** One beat of chapter one rendered as four art styles — the shipped warm cel, a black-ink woodcut, a ukiyo-e woodblock and neo-noir — all from the same identity, beat, seed, size and four steps, with only the style string changed. The grid explains the mechanism the product actually uses: every keyframe is composed as *identity + style + scene*, the same style line goes to the motion model, and the director is told not to invent a colour the style does not name. Rendered on this machine by `tools/make_style_variants.py`, which calls Opsis's own keyframe composition.
- **Opsis footage, from the pipeline itself.** Thirty-five seconds cut from four of the twenty-two shots that made chapter one — keyframes painted with FLUX.2 klein, motion generated with Wan 2.2 on the local card, narration spoken by Chatterbox Turbo, the source being Faraday's own 1831 *Experimental Researches*. It sits under the Opsis stage with a shot-by-shot transcript. Every cut lands in a pause the narration leaves between sentences, so the voice finishes its thought before the picture changes. Because a pre-alpha shown beside a shipped product reads as shipped, it is labelled **Alpha footage** twice: a violet pill beside the slate, and the first words of the caption.

*...and 25 more entries in [CHANGELOG.md](CHANGELOG.md).*

<!-- CHANGELOG:END -->
