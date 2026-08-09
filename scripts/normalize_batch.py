#!/usr/bin/env python3
"""
Normalize raw trait layers onto a shared 1000x1000 canvas as true PNG RGBA.

Placement is anchor-based (not naive center-scale) so faces, clothing, hats,
and glasses share a consistent skeleton.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

from paths import CONFIG, LAYERS_NORM, LAYERS_RAW

# ── Canvas skeleton (fractions of canvas size) ─────────────────────────────
# Face fills most of the bust frame; clothing collar sits under the chin;
# hat brim rests on the crown; glasses sit on the eye line.
SKELETON = {
    "face": {
        # Scale face so content height ≈ this fraction of canvas
        "content_height": 0.80,
        # Top of face content lands here (leave room for hats)
        "content_top": 0.10,
        "center_x": 0.50,
    },
    "mask": {
        "content_height": 0.70,
        "content_top": 0.12,
        "center_x": 0.50,
    },
    "clothing": {
        # Scale to this width, then pin TOP of clothing to neck line
        "content_width": 0.96,
        "content_top": 0.56,  # collar under chin
        "center_x": 0.50,
        "max_content_height": 0.48,
    },
    "hat": {
        # Default baseball-cap style: brim sits on forehead
        "content_width": 0.62,
        "content_bottom": 0.30,
        "center_x": 0.50,
        "max_content_height": 0.36,
    },
    "accessory": {
        "content_width": 0.50,
        "center_y": 0.38,
        "center_x": 0.50,
    },
}

ACCESSORY_SUBTYPES = {
    "glasses": {
        "keywords": ["glasses", "sunglasses", "goggles", "aviator"],
        "content_width": 0.50,
        "center_y": 0.38,
    },
    "smoke": {
        "keywords": ["cigar", "cigarette", "pipe"],
        "content_width": 0.30,
        "center_y": 0.54,
        "center_x": 0.62,
    },
    "neck": {
        "keywords": ["necklace", "chain", "collar", "bowtie", "scarf"],
        "content_width": 0.44,
        "center_y": 0.60,
    },
    "cape": {
        "keywords": ["cape"],
        "content_width": 0.92,
        "content_top": 0.30,
        "mode": "top",
    },
    "gas_mask": {
        "keywords": ["gas_mask"],
        "content_width": 0.55,
        "center_y": 0.44,
    },
}

HAT_SUBTYPES = {
    "tall": {
        "keywords": ["helmet", "top_hat", "chef", "hardhat", "pith", "bicorne", "turban"],
        "content_width": 0.60,
        "content_bottom": 0.32,
        "max_content_height": 0.42,
    },
    "flat": {
        # Sit lower on the skull; keep width generous
        "keywords": ["bandana", "beanie", "stocking", "beret"],
        "content_width": 0.58,
        "content_bottom": 0.28,
        "max_content_height": 0.30,
    },
    "wide": {
        "keywords": ["cowboy", "gambler", "fedora", "boonie", "bucket", "campaign", "ranger"],
        "content_width": 0.78,
        "content_bottom": 0.30,
        "max_content_height": 0.34,
    },
}


def load_json(path: Path):
    return json.loads(path.read_text())


def open_rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def trim_transparent(im: Image.Image, alpha_threshold: int = 8) -> Image.Image:
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    alpha = im.split()[-1]
    mask = alpha.point(lambda a: 255 if a > alpha_threshold else 0)
    bbox = mask.getbbox()
    if not bbox:
        return im
    return im.crop(bbox)


def match_subtype(stem: str, table: dict) -> dict | None:
    low = stem.lower()
    for _name, cfg in table.items():
        if any(k in low for k in cfg.get("keywords", [])):
            return cfg
    return None


def place(
    subject: Image.Image,
    canvas_w: int,
    canvas_h: int,
    *,
    content_width: float | None = None,
    content_height: float | None = None,
    max_content_height: float | None = None,
    content_top: float | None = None,
    content_bottom: float | None = None,
    center_x: float = 0.5,
    center_y: float | None = None,
    mode: str = "auto",
    dx: int = 0,
    dy: int = 0,
    scale_mul: float = 1.0,
) -> Image.Image:
    """Place trimmed subject onto transparent canvas using skeleton anchors."""
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    sw, sh = subject.size
    if sw == 0 or sh == 0:
        return canvas

    # Determine scale
    scale = 1.0
    if content_height is not None:
        scale = (canvas_h * content_height) / sh
    elif content_width is not None:
        scale = (canvas_w * content_width) / sw

    scale *= scale_mul

    new_w = max(1, int(round(sw * scale)))
    new_h = max(1, int(round(sh * scale)))

    # Cap height if needed (re-scale proportionally)
    if max_content_height is not None and new_h > canvas_h * max_content_height:
        scale2 = (canvas_h * max_content_height) / sh
        scale2 *= scale_mul
        new_w = max(1, int(round(sw * scale2)))
        new_h = max(1, int(round(sh * scale2)))

    subject = subject.resize((new_w, new_h), Image.Resampling.LANCZOS)

    cx = center_x * canvas_w
    x = int(round(cx - new_w / 2)) + dx

    if content_top is not None and (mode in ("auto", "top") or center_y is None):
        y = int(round(content_top * canvas_h)) + dy
    elif content_bottom is not None and (mode in ("auto", "bottom") or center_y is None):
        y = int(round(content_bottom * canvas_h - new_h)) + dy
    elif center_y is not None:
        y = int(round(center_y * canvas_h - new_h / 2)) + dy
    else:
        y = int(round(canvas_h / 2 - new_h / 2)) + dy

    # Soft clamp: keep some content on canvas but allow slight overflow
    # (overflow is fine — alpha composite will clip to canvas when pasting via crop)
    # Pillow paste requires position; if y negative, paste with offset crop
    _paste_safe(canvas, subject, x, y)
    return canvas


def _paste_safe(canvas: Image.Image, layer: Image.Image, x: int, y: int) -> None:
    """Alpha-composite layer onto canvas allowing negative offsets / overflow."""
    cw, ch = canvas.size
    lw, lh = layer.size

    # Intersection of layer rect with canvas
    src_x0 = max(0, -x)
    src_y0 = max(0, -y)
    src_x1 = min(lw, cw - x)
    src_y1 = min(lh, ch - y)
    if src_x1 <= src_x0 or src_y1 <= src_y0:
        return

    cropped = layer.crop((src_x0, src_y0, src_x1, src_y1))
    dst_x = x + src_x0
    dst_y = y + src_y0

    # Composite only the overlapping region
    region = canvas.crop((dst_x, dst_y, dst_x + cropped.width, dst_y + cropped.height))
    region = Image.alpha_composite(region, cropped)
    canvas.paste(region, (dst_x, dst_y))


def place_for_category(
    subject: Image.Image,
    category: str,
    trait_id: str,
    canvas_w: int,
    canvas_h: int,
    override: dict | None = None,
) -> Image.Image:
    override = override or {}
    cfg = dict(SKELETON.get(category, {}))

    if category == "accessory":
        sub = match_subtype(trait_id, ACCESSORY_SUBTYPES)
        if sub:
            cfg.update({k: v for k, v in sub.items() if k != "keywords"})
    elif category == "hat":
        sub = match_subtype(trait_id, HAT_SUBTYPES)
        if sub:
            cfg.update({k: v for k, v in sub.items() if k != "keywords"})

    # Apply per-trait overrides (scale_mul, dx, dy, and any skeleton keys)
    for k in (
        "content_width",
        "content_height",
        "max_content_height",
        "content_top",
        "content_bottom",
        "center_x",
        "center_y",
        "mode",
        "dx",
        "dy",
        "scale_mul",
    ):
        if k in override:
            cfg[k] = override[k]

    return place(
        subject,
        canvas_w,
        canvas_h,
        content_width=cfg.get("content_width"),
        content_height=cfg.get("content_height"),
        max_content_height=cfg.get("max_content_height"),
        content_top=cfg.get("content_top"),
        content_bottom=cfg.get("content_bottom"),
        center_x=float(cfg.get("center_x", 0.5)),
        center_y=cfg.get("center_y"),
        mode=str(cfg.get("mode", "auto")),
        dx=int(cfg.get("dx", 0)),
        dy=int(cfg.get("dy", 0)),
        scale_mul=float(cfg.get("scale_mul", 1.0)),
    )


def normalize_one(
    trait: dict,
    canvas_cfg: dict,
    overrides: dict,
) -> Path | None:
    category = trait["category"]
    tid = trait["id"]
    if tid == "none" or trait.get("source_rel") is None:
        return None

    src = LAYERS_RAW / trait["source_rel"]
    if not src.exists():
        src = Path(trait.get("source") or "")
    if not src.exists():
        print(f"  MISSING: {tid}", file=sys.stderr)
        return None

    ov = overrides.get("traits", {}).get(tid, {})
    im = open_rgba(src)
    im = trim_transparent(im)

    out_im = place_for_category(
        im,
        category,
        tid,
        canvas_cfg["width"],
        canvas_cfg["height"],
        ov,
    )

    out_dir = LAYERS_NORM / category
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{tid}.png"
    out_im.save(out_path, format="PNG", optimize=True)
    return out_path


def make_backgrounds(canvas_cfg: dict, traits_bg: list[dict]) -> None:
    out_dir = LAYERS_NORM / "background"
    out_dir.mkdir(parents=True, exist_ok=True)
    w, h = canvas_cfg["width"], canvas_cfg["height"]
    for t in traits_bg:
        color = tuple(t["color"])
        Image.new("RGBA", (w, h), color).save(out_dir / f"{t['id']}.png", format="PNG")


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize trait layers to shared canvas")
    parser.add_argument(
        "--category",
        choices=["face", "clothing", "hat", "accessory", "mask", "all"],
        default="all",
    )
    parser.add_argument("--ids", nargs="*", help="Only normalize these trait ids")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    traits_path = CONFIG / "traits.json"
    if not traits_path.exists():
        raise SystemExit("Run scripts/curate_traits.py first")

    catalog = load_json(traits_path)
    canvas_cfg = load_json(CONFIG / "canvas.json")
    overrides = load_json(CONFIG / "placement_overrides.json")

    categories = (
        ["face", "clothing", "hat", "accessory", "mask"]
        if args.category == "all"
        else [args.category]
    )

    make_backgrounds(canvas_cfg, catalog["traits"]["background"])
    print(f"Backgrounds: {len(catalog['traits']['background'])}")

    total = 0
    for cat in categories:
        items = catalog["traits"][cat]
        if args.ids:
            items = [t for t in items if t["id"] in args.ids]
        if args.limit:
            items = [t for t in items if t["id"] != "none"][: args.limit]

        n = len([t for t in items if t["id"] != "none"])
        print(f"Normalizing {cat}: {n} traits…")
        for t in items:
            if t["id"] == "none":
                continue
            if normalize_one(t, canvas_cfg, overrides):
                total += 1

    print(f"Done. Wrote {total} normalized layers under {LAYERS_NORM}")


if __name__ == "__main__":
    main()
