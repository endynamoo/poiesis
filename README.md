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

- **The style demo moves.** Four clips instead of four stills: one beat of chapter one, animated four times — warm cel, woodcut, ukiyo-e, neo-noir — so the comparison is the film and not the frame. Each keyframe was composed by the product's own path (`identity + style + scene`), then handed to Wan 2.2 I2V with the same style line as its motion prompt, which is what the app's motion job does. Silent, looping, 5 seconds each (~320 KB), all four started together so they stay in step; they pause when the grid leaves the screen and stay on their posters under reduced motion.
- **The look is a field, shown four ways.** The grid explains the mechanism the product actually uses: every keyframe is composed as *identity + style + scene*, the same style line goes to the motion model, and the director is told not to invent a colour the style does not name. Rendered on this machine by `tools/make_style_variants.py` and `tools/make_style_clips.py`, which call Opsis's own keyframe and motion composition.

*...and 26 more entries in [CHANGELOG.md](CHANGELOG.md).*

<!-- CHANGELOG:END -->
