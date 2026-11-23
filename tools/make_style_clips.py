"""Animate the four style keyframes with Opsis's own motion path.

The style demo on the page claims the look is a field the director edits. Four
still frames prove it paints differently; four clips prove the *film* comes back
differently, which is what the product actually delivers. This takes the four
keyframes rendered by `make_style_variants.py` and runs them through
`opsis.pipeline.a14b` (Wan 2.2 I2V A14B, the Lightning 4-step LoRA) using
`a14b.motion_prompt` with each look's own style string — the same code path the
app's `motion` job uses.

    <python with the Opsis deps> tools/make_style_clips.py

ComfyUI is started by Opsis's own supervisor and stopped again at the end.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STILLS = ROOT / "docs" / "style-variants"
OUT = ROOT / "docs" / "style-variants" / "clips"
OPSIS = os.environ.get("OPSIS_ROOT", r"C:\Apps\Opsis")
SEED = 42
FRAMES = 81          # 4n+1 at 16 fps -> 5.06 s; enough motion for a tile
SECONDS_KEEP = None  # transcode keeps the whole clip

sys.path.insert(0, OPSIS)

from opsis import comfy as comfy_service  # noqa: E402
from opsis import config as config_mod  # noqa: E402
from opsis.pipeline import a14b  # noqa: E402

# The beat and the four looks, identical to make_style_variants.py.
BEAT = ("Michael Faraday watches a copper disc rotate near a flat spiral coil, "
        "sparks flickering between them.")
LOOKS = {
    "warm-cel": "hand-painted cel animation, gouache painting style, warm amber tones, "
                "subtle film grain, no text, no watermark",
    "woodcut": "black ink woodcut engraving on cream paper, dense hatching for shadow, "
               "two values only, no colour, no text, no watermark",
    "ukiyoe": "Japanese ukiyo-e woodblock print, indigo and vermilion, flat colour areas, "
              "bold contour lines, paper texture, no text, no watermark",
    "noir": "1990s neo-noir animation, charcoal blacks and cold teal, single hard rim "
            "light, deep shadows, no text, no watermark",
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = config_mod.load()
    app_dir = comfy_service.client(cfg).app_dir
    if app_dir is None:
        print("ComfyUI not found at", cfg.paths.get("comfy_root"))
        return 1

    client = comfy_service.client(cfg, log_path=OUT / "comfy.log")
    if not client.up():
        print("starting ComfyUI ...", flush=True)
    client.ensure()
    print("ComfyUI up at", client.base_url, flush=True)

    try:
        for slug, style in LOOKS.items():
            still = STILLS / f"{slug}.png"
            dst = OUT / f"{slug}.mp4"
            if not still.exists():
                print(f"missing keyframe {still}")
                return 1
            if dst.exists():
                print(f"skip {dst.name}", flush=True)
                continue

            image_name = f"poiesis_style_{slug}.png"
            shutil.copyfile(still, app_dir / "input" / image_name)

            prompt = a14b.motion_prompt(style, "Michael Faraday", BEAT)
            from dataclasses import replace

            motion_cfg = a14b.MotionConfig(frames=FRAMES, steps=4,
                                           blocks_to_swap=30, width=832, height=480)
            high, low = a14b.models_for("Q3_K_M")     # the box's default quant
            motion_cfg = replace(motion_cfg, high_model=high, low_model=low)
            graph = a14b.build(motion_cfg, image=image_name, prompt=prompt,
                               seed=SEED, prefix=f"poiesis_style_{slug}")

            t0 = time.time()
            prompt_id = client.submit(graph)
            produced = client.wait(prompt_id, timeout=3600.0)
            print(f"{slug}: rendered in {time.time() - t0:.0f}s -> {produced}", flush=True)

            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-i", str(produced),
                 "-an", "-c:v", "libx264", "-crf", "28", "-preset", "slow",
                 "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dst)],
                check=True)
            print(f"{slug}: {round(dst.stat().st_size / 1024)} KB", flush=True)

            (OUT / "clips.json").write_text(json.dumps(
                {"beat": BEAT, "seed": SEED, "frames": FRAMES, "looks": LOOKS},
                indent=1, ensure_ascii=False), encoding="utf-8")
    finally:
        client.stop()
        print("ComfyUI stopped", flush=True)

    print("STYLE CLIPS DONE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
