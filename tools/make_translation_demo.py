r"""Render the translation demo with Rhapsode's own on-device translator.

The page claims translation is local, so the samples on it must come from the same
path the app uses - not from a chat window. This starts Rhapsode's bundled
translator (`murmur.localmt`: llama.cpp plus a Qwen2.5 GGUF the app downloads
itself), translates the reader's passage into each language the model is measured
on, and writes `docs/translation-demo.json` for the page.

    set RHAPSODE_ROOT=C:\Apps\rhapsode
    <rhapsode venv python> tools/make_translation_demo.py [--variant 7b|1.5b]

The first run downloads the runtime and the weights (4.7 GB for 7b, 1.1 GB for
1.5b) into Rhapsode's models directory; the server is stopped again at the end.
Hindi is deliberately absent: on every local variant it produced loops that no
`repeat_penalty` fixed, so Rhapsode routes Hindi to a server the reader runs.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RHAPSODE = Path(os.environ.get("RHAPSODE_ROOT", r"C:\Apps\rhapsode"))
OUT = ROOT / "docs" / "translation-demo.json"

sys.path.insert(0, str(RHAPSODE))

# The console on Windows is cp1252 by default, and Japanese or Chinese output would
# kill the run at a print() after the work is done.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from murmur import localmt  # noqa: E402
from murmur import translate  # noqa: E402

PASSAGE = ("The lantern keeper counted the ships that evening, as she had done every "
           "evening for eleven years.")

# One sentence, translated as the app does for a page. A long Stoic list made two of
# the four languages break agreement ("l jaloux", "Todos estos cosas"), so the demo
# uses the sentence the Rhapsode take itself speaks: plain, concrete, one clause.
SENTENCES = [PASSAGE]

# Declared, not detected. With `source="auto"` the 7B finished the second Japanese
# sentence in Chinese ("...すべて这些事情发生在他们身上"); naming English fixed it on
# the same two sentences, twice. The app knows a book's language, so it can say so.
SOURCE_LANG = "en"

# language tag, label shown on the page
TARGETS = [
    ("es", "Spanish"),
    ("fr", "French"),
    ("ja", "Japanese"),
    ("zh", "Chinese"),
]


def wait_for_download(timeout: float = 3600.0) -> None:
    state = localmt.state()
    if state.get("done") and localmt.installed():
        return
    if not state.get("running"):
        print("downloading the translation model ...", flush=True)
        localmt.start_download()
    started = time.time()
    last = ""
    while time.time() - started < timeout:
        state = localmt.state()
        progress = state.get("progress") or {}
        line = "%s %s%%" % (progress.get("label", ""), progress.get("percent", ""))
        if line != last:
            print("  ", line, flush=True)
            last = line
        if state.get("error"):
            raise SystemExit("download failed: " + str(state["error"]))
        if state.get("done") and localmt.installed():
            return
        time.sleep(5)
    raise SystemExit("download did not finish in time")


def main() -> int:
    parser = argparse.ArgumentParser(description="render the translation demo")
    parser.add_argument("--variant", default="7b", choices=sorted(localmt.VARIANTS))
    parser.add_argument("--timeout", type=float, default=240.0)
    args = parser.parse_args()

    os.environ["MURMUR_LOCALMT_VARIANT"] = args.variant
    wait_for_download()

    print("starting the translator ...", flush=True)
    url = localmt.ensure_server()
    model = localmt.VARIANTS[args.variant]
    print("server:", url, "| variant:", model["label"], flush=True)

    results = []
    try:
        for tag, label in TARGETS:
            if not localmt.supports(tag):
                print("skip", tag, "- not in this variant's measured languages")
                continue
            started = time.time()
            # One sentence at a time, the way the app translates a page: a whole
            # paragraph in one request invites agreement errors and drift.
            pieces = []
            for sentence in SENTENCES:
                reply = translate.translator.translate(sentence, tag, SOURCE_LANG)
                pieces.append(reply["text"].strip())
            took = time.time() - started
            text = " ".join(pieces) if tag not in ("ja", "zh") else "".join(pieces)
            results.append({
                "lang": tag,
                "label": label,
                "text": text,
                "seconds": round(took, 2),
            })
            print("%-9s %5.1fs  %d chars" % (label, took, len(text)), flush=True)
    finally:
        localmt.stop()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source": PASSAGE,
        "variant": args.variant,
        "model_label": model["label"],
        "model_repo": model["repo"],
        "note": model["note"],
        "results": results,
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
