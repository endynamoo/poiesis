"""Render one Opsis scene in several art styles, with everything else fixed.

The style demo on the page claims the look is a field the director edits, so
this must be reproducible rather than four pictures that happen to differ. It
runs the product's own keyframe composition — `identity + style + SCENE: beat`,
from `opsis/pipeline/keyframes.py` — and changes only the style string. Identity,
beat text, seed, steps and size are identical across every look, so the
difference in the picture is the style and nothing else.

    set OPSIS_ROOT=C:\\Apps\\Opsis
    set KLEIN_GGUF=C:\\Apps\\FaradayFilm\\models\\klein\\flux-2-klein-4b-Q4_K_M.gguf
    <comfy venv python> tools/make_style_variants.py

It needs a torch with ROCm or CUDA, diffusers >= 0.42 and the FLUX.2 klein
weights: the transformer as a GGUF, plus the text encoder, VAE, tokenizer and
scheduler from `black-forest-labs/FLUX.2-klein-4B` (the transformer subfolder of
that repo is *not* used — the GGUF replaces it). On this box each look takes
about five seconds after the 17-second load.
"""
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "style-variants"
OPSIS = os.environ.get("OPSIS_ROOT", r"C:\Apps\Opsis")
GGUF = os.environ.get("KLEIN_GGUF", r"C:\Apps\FaradayFilm\models\klein\flux-2-klein-4b-Q4_K_M.gguf")
SEED, WIDTH, HEIGHT, STEPS = 42, 832, 464, 4

sys.path.insert(0, OPSIS)
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import torch  # noqa: E402
from opsis.pipeline import keyframes as K  # noqa: E402

# One beat of chapter one, from the FaradayFilm shots.json for shot 03.
BEAT = ("Michael Faraday watches a copper disc rotate near a flat spiral coil, "
        "sparks flickering between them.")

# slug, label, note, the style string the director's look field would hold
STYLES = [
    ("warm-cel", "Warm cel", "shipped default",
     "hand-painted cel animation, gouache painting style, warm amber tones, "
     "subtle film grain, no text, no watermark"),
    ("woodcut", "Woodcut", "ink on cream",
     "black ink woodcut engraving on cream paper, dense hatching for shadow, "
     "two values only, no colour, no text, no watermark"),
    ("ukiyoe", "Ukiyo-e", "indigo & vermilion",
     "Japanese ukiyo-e woodblock print, indigo and vermilion, flat colour areas, "
     "bold contour lines, paper texture, no text, no watermark"),
    ("noir", "Neo-noir", "charcoal & teal",
     "1990s neo-noir animation, charcoal blacks and cold teal, single hard rim "
     "light, deep shadows, no text, no watermark"),
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(SEED)
    started = time.time()
    pipe = K.load_pipeline(GGUF)
    print(f"pipeline ready in {time.time() - started:.0f}s", flush=True)

    for slug, label, note, style in STYLES:
        dst = OUT / f"{slug}.png"
        if dst.exists():
            print(f"skip {dst.name}", flush=True)
            continue
        prompt = f"{K.DEFAULT_IDENTITY} {style} SCENE: {BEAT}"
        t0 = time.time()
        image = pipe(
            prompt=prompt,
            image=None,
            height=HEIGHT,
            width=WIDTH,
            num_inference_steps=STEPS,
            guidance_scale=1.0,
            generator=torch.Generator("cpu").manual_seed(SEED),
        ).images[0]
        image.save(dst)
        print(f"{label:9s} {dst.name}  {time.time() - t0:.0f}s", flush=True)

    (OUT / "styles.json").write_text(
        json.dumps(
            [{"slug": s, "label": l, "note": n, "style": st} for s, l, n, st in STYLES],
            indent=1, ensure_ascii=False),
        encoding="utf-8")
    print("STYLE VARIANTS DONE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
