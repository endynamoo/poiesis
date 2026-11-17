#!/usr/bin/env python3
"""Render the reader sample with the real Kokoro voice from the Rhapsode checkout.

The page's player is not allowed to fake it: the clip that plays is Kokoro-82M
speaking the passage, and the word highlight is driven by the phoneme timings the
same synthesis returns. This script regenerates both artefacts.

    C:\\Apps\\Rhapsode\\.venv\\Scripts\\python.exe tools/make_reader_audio.py

Writes:
    assets/audio/reader.mp3   the clip (mono, 64 kbps, 44.1 kHz)
    assets/audio/reader.json  duration + per-word start/end, for the highlight

It imports the sibling checkout read-only; nothing in Rhapsode is modified.
Set POIESIS_RHAPSODE_REPO if it lives somewhere else.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "audio"
INDEX = ROOT / "index.html"
BEGIN = "<!-- reader-timings:begin -->"
END = "<!-- reader-timings:end -->"
REPO = Path(os.environ.get("POIESIS_RHAPSODE_REPO", r"C:\Apps\Rhapsode"))
VOICE = os.environ.get("POIESIS_VOICE", "af_heart")

# Must stay word-for-word identical to the `<p id="prose">` passage in index.html
# (which uses a non-breaking hyphen in "busy-body"; the spoken text uses ASCII).
TEXT = (
    "Begin the morning by saying to thyself, I shall meet with the busy-body, "
    "the ungrateful, arrogant, deceitful, envious, unsocial. All these things "
    "happen to them by reason of their ignorance of what is good and evil."
)


def synthesize() -> dict:
    sys.path.insert(0, str(REPO))
    from murmur import engine  # noqa: E402  (needs the path first)

    meta = engine.engine.synthesize(TEXT, VOICE)
    return meta


def encode(wav: Path, mp3: Path) -> None:
    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(wav),
            "-ac", "1", "-ar", "44100", "-b:a", "64k",
            "-map_metadata", "-1", "-fflags", "+bitexact",
            str(mp3),
        ],
        check=True,
    )


def main() -> int:
    if not REPO.exists():
        print("Rhapsode checkout not found at %s" % REPO)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)

    meta = synthesize()
    wav = Path(meta["path"])
    mp3 = OUT / "reader.mp3"
    encode(wav, mp3)

    words = meta.get("words") or []
    payload = {
        "voice": meta.get("voice", VOICE),
        "duration": round(float(meta["duration"]), 3),
        "source": "Kokoro-82M · murmur.engine.synthesize",
        "words": [{"s": w["start"], "e": w["end"]} for w in words],
    }
    (OUT / "reader.json").write_text(json.dumps(payload, indent=1) + "\n", "utf-8")
    write_timings(payload)

    print("clip     %s  %.1f KB" % (mp3, mp3.stat().st_size / 1024))
    print("duration %.2f s over %d words" % (payload["duration"], len(payload["words"])))
    print("json     %s" % (OUT / "reader.json"))
    return 0


def write_timings(payload: dict) -> None:
    """Rewrite the inline timing block in index.html from the fresh synthesis."""
    compact = {
        "duration": payload["duration"],
        "words": [[w["s"], w["e"]] for w in payload["words"]],
    }
    block = (
        BEGIN
        + "\n      <script type=\"application/json\" id=\"reader-timings\">"
        + json.dumps(compact, separators=(",", ":"))
        + "</script>\n      "
        + END
    )
    text = INDEX.read_text("utf-8")
    start = text.index(BEGIN)
    end = text.index(END, start) + len(END)
    if text[start:end] == block:
        print("timings  already current")
        return
    INDEX.write_text(text[:start] + block + text[end:], "utf-8")
    print("timings  %d words written into index.html" % len(compact["words"]))


if __name__ == "__main__":
    raise SystemExit(main())
