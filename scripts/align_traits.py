#!/usr/bin/env python3
"""
Align clothing / hat / accessory raw layers onto the master template skeleton
and write them into layers_template/ for compositing with white faces.

Uses config/template_skeleton.json guide lines:
  - clothing: top of content pinned to collar_y
  - hat: bottom of content pinned to hat_brim
  - glasses: centered on eye_line with eye_span width
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image

from paths import CONFIG, LAYERS_RAW, ROOT

TEMPLATE_LAYERS = ROOT / "layers_template"
SKELETON_PATH = CONFIG / "template_skeleton.json"

# Skip near-dupes and specials from mass trait pool
DROP_SUBSTR = ("_v2", "_v3", "_alt")
DROP_IDS = {
    "npc_gray_head",
    "npc_gray_head_alt",
    "mask_blank_template",
    "blank_outline",
}
# Style refs only / 1of1 adjacent (green pepe tee etc.)
SPECIAL_CLOTHING = {
    "green_pol_pepe_tee",
    "green_pol_pepe_tee_alt",
    "mcdonalds_uniform",
    "mcdonalds_uniform_alt",
}


def load_skeleton() -> dict:
    return json.loads(SKELETON_PATH.read_text())


def trim(im: Image.Image, thr: int = 8) -> Image.Image:
    im = im.convert("RGBA")
    a = im.split()[-1]
    bb = a.point(lambda v: 255 if v > thr else 0).getbbox()
    return im.crop(bb) if bb else im


def paste_safe(canvas: Image.Image, layer: Image.Image, x: int, y: int) -> None:
    cw, ch = canvas.size
    lw, lh = layer.size
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(lw, cw - x), min(lh, ch - y)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    cropped = layer.crop((sx0, sy0, sx1, sy1))
    dx, dy = x + sx0, y + sy0
    region = canvas.crop((dx, dy, dx + cropped.width, dy + cropped.height))
    canvas.paste(Image.alpha_composite(region, cropped), (dx, dy))


def place_clothing(im: Image.Image, sk: dict) -> Image.Image:
    W, H = sk["canvas"]["width"], sk["canvas"]["height"]
    collar_y = sk["guides_y"]["collar"]
    im = trim(im)
    # width ~ full shoulders; allow taller so white chest is covered
    target_w = int(W * 0.98)
    scale = target_w / im.width
    nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    # allow clothing to reach near bottom of canvas from collar
    max_h = int(H * (1.0 - collar_y + 0.02))
    if nh > max_h:
        scale = max_h / im.height
        nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = (W - nw) // 2
    y = int(H * collar_y)  # pin top of clothing to collar (covers face torso)
    paste_safe(canvas, im, x, y)
    return canvas


def place_hat(im: Image.Image, sk: dict, stem: str) -> Image.Image:
    W, H = sk["canvas"]["width"], sk["canvas"]["height"]
    brim = sk["guides_y"]["hat_brim"]
    im = trim(im)
    # subtype widths
    low = stem.lower()
    if any(k in low for k in ("cowboy", "gambler", "fedora", "boonie", "bucket", "campaign", "ranger")):
        tw = 0.78
    elif any(k in low for k in ("helmet", "top_hat", "chef", "hardhat", "pith", "bicorne")):
        tw = 0.60
    else:
        tw = 0.62
    scale = (W * tw) / im.width
    nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    max_h = int(H * 0.38)
    if nh > max_h:
        scale = max_h / im.height
        nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = (W - nw) // 2
    y = int(H * brim) - nh  # bottom of hat on brim line
    paste_safe(canvas, im, x, y)
    return canvas


def place_accessory(im: Image.Image, sk: dict, stem: str) -> Image.Image:
    W, H = sk["canvas"]["width"], sk["canvas"]["height"]
    im = trim(im)
    low = stem.lower()
    if any(k in low for k in ("glasses", "sunglasses", "goggles", "aviator")):
        tw = sk["guides_x"]["eye_span"] + 0.12  # slightly wider than eye span
        cy = sk["guides_y"]["eye_line"]
        cx = 0.50
    elif any(k in low for k in ("cigar", "cigarette", "pipe")):
        tw, cy, cx = 0.30, sk["guides_y"]["mouth"], 0.62
    elif any(k in low for k in ("necklace", "chain", "collar", "bowtie", "scarf")):
        tw, cy, cx = 0.44, sk["guides_y"]["collar"] - 0.04, 0.50
    elif "cape" in low:
        tw, cy, cx = 0.92, 0.45, 0.50
        # top-pin cape
        scale = (W * tw) / im.width
        nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
        im = im.resize((nw, nh), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        paste_safe(canvas, im, (W - nw) // 2, int(H * 0.30))
        return canvas
    elif "gas_mask" in low:
        tw, cy, cx = 0.55, sk["guides_y"]["nose"], 0.50
    else:
        tw, cy, cx = 0.40, sk["guides_y"]["eye_line"], 0.50

    scale = (W * tw) / im.width
    nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = int(W * cx - nw / 2)
    y = int(H * cy - nh / 2)
    paste_safe(canvas, im, x, y)
    return canvas


def should_drop(stem: str, category: str) -> bool:
    if stem in DROP_IDS or stem.startswith("._"):
        return True
    if any(s in stem for s in DROP_SUBSTR):
        return True
    if category == "clothing" and stem in SPECIAL_CLOTHING:
        return True
    if category == "hat" and stem.lower() == "hat_catalog":
        return True
    return False


def collect_raw(category: str) -> list[Path]:
    mapping = {
        "clothing": ["clothing", "clothing2", "hoodies"],
        "hat": ["hats"],
        "accessory": ["accessories"],
    }
    out = []
    seen = set()
    for d in mapping[category]:
        folder = LAYERS_RAW / d
        if not folder.is_dir():
            continue
        for p in sorted(folder.glob("*.png")):
            if should_drop(p.stem, category):
                continue
            if p.stem.lower() in seen:
                continue
            seen.add(p.stem.lower())
            out.append(p)
    return out


def align_category(category: str, sk: dict, limit: int = 0) -> int:
    placer = {
        "clothing": place_clothing,
        "hat": lambda im, sk, stem=None: place_hat(im, sk, stem or ""),
        "accessory": lambda im, sk, stem=None: place_accessory(im, sk, stem or ""),
    }[category]
    paths = collect_raw(category)
    if limit:
        paths = paths[:limit]
    out_dir = TEMPLATE_LAYERS / category
    out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for p in paths:
        im = Image.open(p)
        if category == "clothing":
            out = place_clothing(im, sk)
        elif category == "hat":
            out = place_hat(im, sk, p.stem)
        else:
            out = place_accessory(im, sk, p.stem)
        out.save(out_dir / f"{p.stem}.png", format="PNG", optimize=True)
        n += 1
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--category",
        choices=["clothing", "hat", "accessory", "all"],
        default="all",
    )
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    sk = load_skeleton()
    cats = ["clothing", "hat", "accessory"] if args.category == "all" else [args.category]
    for c in cats:
        n = align_category(c, sk, limit=args.limit)
        print(f"{c}: aligned {n} → layers_template/{c}/")


if __name__ == "__main__":
    main()
