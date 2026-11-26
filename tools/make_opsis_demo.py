r"""Cut the Opsis montage from the pipeline's own per-shot clips.

Source: `$FARADAY_ROOT\batch\ch01_1-13\clips_ch01_1-13\cNN.mp4` (1024x576, 24 fps,
h264 + aac) - the clips Opsis assembled for chapter one. Each shot is one
paragraph of Faraday read straight through, so a fixed six-second slice chops
sentences in half. The boundaries below are the pauses
`silencedetect=noise=-30dB:d=0.35` found in each clip; each segment runs from the
clip's first word to the *start* of a pause, so the last sentence finishes and the
next shot begins clean.

    c03  silence 6.82-7.55, 11.67-12.36, 16.76-17.17, 18.61-19.48
    c07  silence 2.48-3.23, 12.85-13.40, 14.13-14.48, 16.22-16.61, 23.43-24.28
    c12  silence 3.74-4.25, 7.37-8.03, 9.08-9.54, 11.81-12.63, 17.43-18.20
    c17  silence 3.18-3.67, 6.92-7.33, 8.37-8.76, 11.40-12.28

Three of those pauses sit inside a sentence (a semicolon or a comma), so only the
long ones are used: c07 at 2.48 is "I lately arrived at positive results;" and
cutting there was exactly the disjointed join this fixes.

    set FARADAY_ROOT=C:\\Apps\\FaradayFilm
    python tools/make_opsis_demo.py

Writes `assets/video/opsis-demo.mp4` and `assets/img/opsis-demo-poster.webp`.
Frames are hard-cut: the audio seam already sits in a pause, and fading both ends
to black put a dead black frame between every shot. Only the last segment fades
out, so the piece ends rather than stops. The narration is the pipeline's own
Chatterbox Turbo voice, not Rhapsode's Kokoro.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FARADAY = Path(os.environ.get("FARADAY_ROOT", r"C:\Apps\FaradayFilm"))
SRC = FARADAY / "batch" / "ch01_1-13" / "clips_ch01_1-13"
WORK = ROOT / "docs" / "opsis-demo"
FINAL = ROOT / "assets" / "video" / "opsis-demo.mp4"
POSTER = ROOT / "assets" / "img" / "opsis-demo-poster.webp"

# (clip, start, end) - ends sit 0.15 s inside the detected pause, before the
# next sentence starts speaking.
SEGMENTS = [
    ("c03", 0.0, 6.97),
    ("c07", 0.0, 13.00),
    ("c12", 0.0, 7.52),
    ("c17", 0.0, 7.10),
]
POSTER_AT = 2.0        # seconds into the montage: the chamber beat
FADE_OUT = 0.6


def run(args: list[str]) -> None:
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        print("FAILED:", " ".join(args))
        print(proc.stderr[-2500:])
        sys.exit(1)


def main() -> int:
    if not SRC.is_dir():
        print("no clips at", SRC, "- set FARADAY_ROOT")
        return 1
    WORK.mkdir(parents=True, exist_ok=True)
    FINAL.parent.mkdir(parents=True, exist_ok=True)

    pieces = []
    for index, (clip, start, end) in enumerate(SEGMENTS, 1):
        length = round(end - start, 3)
        dst = WORK / ("s%d.mp4" % index)
        filters = ["scale=1024:576", "fps=24"]
        if index == len(SEGMENTS):
            filters.append("fade=t=out:st=%s:d=%s" % (round(length - FADE_OUT, 3), FADE_OUT))
        run([
            "ffmpeg", "-y", "-ss", str(start), "-t", str(length),
            "-i", str(SRC / (clip + ".mp4")),
            "-vf", ",".join(filters),
            # the seam is already inside a pause, so the audio only needs a guard
            "-af", "afade=t=in:st=0:d=0.04,afade=t=out:st=%s:d=0.06"
                   % round(length - 0.06, 3),
            "-c:v", "libx264", "-crf", "26", "-preset", "slow", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "96k", "-ar", "44100", "-ac", "1",
            str(dst),
        ])
        pieces.append(dst)

    listing = WORK / "list.txt"
    listing.write_text(
        "".join("file '%s'\n" % p.as_posix() for p in pieces), encoding="utf-8")
    joined = WORK / "joined.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-c", "copy", str(joined)])

    run([
        "ffmpeg", "-y", "-i", str(joined),
        "-c:v", "libx264", "-crf", "30", "-preset", "slow", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "80k", "-ac", "1", "-movflags", "+faststart",
        str(FINAL),
    ])

    run(["ffmpeg", "-y", "-ss", str(POSTER_AT), "-i", str(FINAL), "-frames:v", "1",
         "-c:v", "libwebp", "-quality", "84", str(POSTER)])

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration,size",
         "-show_entries", "stream=codec_name,width,height", "-of", "default=nw=1",
         str(FINAL)],
        capture_output=True, text=True)
    print(probe.stdout.strip())
    print("demo: %d KB | poster: %d KB"
          % (round(FINAL.stat().st_size / 1024), round(POSTER.stat().st_size / 1024)))
    print("seams:", [round(sum(s[2] - s[1] for s in SEGMENTS[:i]), 3)
                     for i in range(1, len(SEGMENTS))])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
