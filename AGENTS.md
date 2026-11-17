# Agent rules — Poiesis

Read this before changing anything. It is the durable half of the instructions; the task you
were given is the other half.

## What this is

The portfolio site for **Rhapsode** and **Opsis**: one static page, no framework, no build
step, no runtime dependency. It is served straight from the repository root by GitHub Pages.

**The repository is private and the site is therefore unpublished.** GitHub Pages only
publishes from private repositories on a paid plan; on the free account nothing is deployed
and `.github/workflows/pages.yml` is manual-only on purpose. `python -m http.server 8137` is
how the page is reviewed for now. Do not "fix" the deploy by making the repository public
without being asked.

**The constraints are the point.** A portfolio about lean, local-first software must not ship
a 200 KB framework or call a CDN to show four paragraphs. Before adding anything, ask whether
the page is better without it.

## Verify before you claim

```powershell
python -m unittest discover -s tests -v
```

Run it, and quote the summary line. A change with no test run is not done. For anything
visual, also load the page and look at it at 390, 768 and 1440 pixels wide —
`python -m http.server 8137` then open `http://localhost:8137`. Never describe a layout you
have not seen.

What the suite does **not** cover: WebGL rendering, animation timing, and how a section feels
mid-scroll. Check those by eye, and say plainly what you did not check.

## Rules for the page

- **No third-party origins at runtime.** No CDN fonts, no analytics, no embed. Everything
  ships in `assets/`. `tests/test_site.py` enforces this.
- **No build step.** The files in the repository are the files the browser runs.
- **Every animation has a still version.** New motion goes inside the existing
  `prefers-reduced-motion` block, and anything that loops must pause when it is off-screen or
  the tab is hidden.
- **Accessibility is not a later pass.** One `h1`, real links rather than div-buttons, `alt`
  on every image, visible focus, contrast at AA on `--ink`.
- **Content is evidence.** Numbers on this page are measured ones (VRAM peak, test counts,
  voice counts). Do not swap them for adjectives, and do not invent a number.
- **The reader plays a real voice.** `assets/audio/reader.mp3` and the inline
  `reader-timings` block are both rendered by `tools/make_reader_audio.py` from the Rhapsode
  checkout's Kokoro engine. Never hand-edit either: re-run the tool. `tests/test_site.py`
  fails if the timing count and the passage word count disagree.

## Style

- Match the surrounding code: two-space indent in HTML/CSS/JS, `const`/`let`, no semicolon
  churn, no formatter runs over untouched files.
- Small, atomic commits in Conventional Commits form (`feat(hero): …`, `fix(opsis): …`).
- Do not reformat or "tidy" files outside the task.

## Changelog

- `CHANGELOG.md` is a running history. Add an entry under `## [Unreleased]` in the same
  commit as the change (Added / Changed / Fixed / Removed / Security), phrased for a reader,
  not for a diff.
- When a version is cut, move those entries under `## [<version>] - YYYY-MM-DD`.
- Run `python tools/changelog_render.py` after editing it. It mirrors a truncated copy into
  the `## Changelog` block at the bottom of `README.md`; `tests/test_changelog.py` fails when
  that copy is stale.
- A GitHub release carries the **detailed** section, never the truncated one:
  `python tools/changelog_render.py --release 0.1.0 > notes.md` then
  `gh release create v0.1.0 --notes-file notes.md`.

## PowerShell

Scripts here are launched with Windows PowerShell 5.1, which reads BOM-less UTF-8 as ANSI.
Keep `.ps1` files pure ASCII or save them with a BOM — an em dash in a string is a parse error.

**Never edit `index.html`, the CSS, the JS or the Markdown with `Get-Content`/`Set-Content` in
PowerShell 5.1.** Without `-Encoding utf8` on *both* halves it reads UTF-8 as ANSI and writes
the mojibake back, so every em dash, middot and arrow in the page becomes `â€"` and `Â·`. Use the
editor tools, or a Python one-liner. `tests/test_site.py` fails when the page is double-encoded.

## When in doubt

Ask, or stop and report the ambiguity. A blocked task is cheap; an unreviewable change is not.
