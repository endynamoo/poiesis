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

- **The site is live.** `endynamoo.github.io/poiesis` publishes on every push to `main` again: the repository is public, Pages is configured with `build_type=workflow`, and the deploy workflow has its `push` trigger back.
- **The workflows run the current action majors** — `checkout@v7`, `setup-python@v7`, `configure-pages@v6`, `upload-pages-artifact@v5`, `deploy-pages@v5`. The old ones ran on a deprecated Node, and on two pushes in a row the deploy failed with "No artifacts named github-pages were found" while the upload step still reported success.

**Fixed**

- **The style loops stop when the tab is hidden.** `AGENTS.md` asks that anything looping pause off-screen *or* when the tab is hidden; the four clips only did the first. They now stop on `visibilitychange` and restart together if the grid is still on screen (measured: playing at `t=1.78` on all four, `paused: true` on all four once hidden, in step again on return).
- **The hero no longer waits on an observer to be seen.** Reveals already on screen at first paint are marked in the next animation frame; only below-the-fold reveals still wait. Measured in-browser under 4× CPU and a 1.6 Mbps link, the largest contentful paint is ~1.5 s; Lighthouse's *simulated* mobile run still reports 4.8 s, which is its Lantern estimate rather than a measurement of the page.

**Changed**

- **Rhapsode is at v0.3.6-beta** and the page says so, with the release it points at.

*...and 29 more entries in [CHANGELOG.md](CHANGELOG.md).*

<!-- CHANGELOG:END -->
