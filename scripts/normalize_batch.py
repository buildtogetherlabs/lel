#!/usr/bin/env python3
"""
Normalize raw trait layers onto a shared 1000x1000 canvas as true PNG RGBA.

- Decodes WebP-masquerading-as-PNG
- Trims near-empty borders
- Places by category defaults + per-trait overrides
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

from paths import CONFIG, LAYERS_NORM, LAYERS_RAW, ROOT


def load_json(path: Path):
    return json.loads(path.read_text())


def open_rgba(path: Path) -> Image.Image:
    im = Image.open(path)
    # Ensure full decode for WebP/PNG
    im = im.convert("RGBA")
    return im


def trim_transparent(im: Image.Image, alpha_threshold: int = 8) -> Image.Image:
    """Trim pixels with alpha below threshold."""
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    alpha = im.split()[-1]
    # Binarize alpha for bbox
    mask = alpha.point(lambda a: 255 if a > alpha_threshold else 0)
    bbox = mask.getbbox()
    if not bbox:
        return im
    return im.crop(bbox)


def maybe_key_black_bg(im: Image.Image, enable: bool = True) -> Image.Image:
    """
    If image is mostly opaque with pure black backdrop corners, punch black to alpha.
    Conservative: only pixels that are near-black AND near the image edge clusters.
    Disabled by default for line-art safety — enable with --key-black for stubborn assets.
    """
    if not enable:
        return im
    im = im.convert("RGBA")
    pixels = im.load()
    w, h = im.size
    # Only process if corner samples are black-ish (backdrop heuristic)
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    black_corners = 0
    for x, y in corners:
        r, g, b, a = pixels[x, y]
        if a > 200 and r < 20 and g < 20 and b < 20:
            black_corners += 1
    if black_corners < 3:
        return im

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a > 0 and r < 18 and g < 18 and b < 18:
                # Keep dark gray line art that isn't pure black if nearby non-black?
                # Simple pure-black key:
                if r + g + b < 30:
                    pixels[x, y] = (0, 0, 0, 0)
    return im


def place_on_canvas(
    subject: Image.Image,
    canvas_w: int,
    canvas_h: int,
    defaults: dict,
    override: dict | None = None,
) -> Image.Image:
    """Scale and position subject onto transparent canvas."""
    override = override or {}
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

    if defaults.get("fill"):
        # backgrounds handled elsewhere
        return subject.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)

    sw, sh = subject.size
    if sw == 0 or sh == 0:
        return canvas

    # Scale
    if "scale" in override:
        scale = float(override["scale"])
        new_w = max(1, int(sw * scale))
        new_h = max(1, int(sh * scale))
    elif "target_height_ratio" in defaults:
        target_h = canvas_h * float(defaults["target_height_ratio"])
        scale = target_h / sh
        new_w = max(1, int(sw * scale))
        new_h = max(1, int(sh * scale))
    elif "target_width_ratio" in defaults:
        target_w = canvas_w * float(defaults["target_width_ratio"])
        scale = target_w / sw
        new_w = max(1, int(sw * scale))
        new_h = max(1, int(sh * scale))
    else:
        new_w, new_h = sw, sh

    subject = subject.resize((new_w, new_h), Image.Resampling.LANCZOS)

    cx = float(override.get("center_x", defaults.get("center_x", 0.5))) * canvas_w
    ay = float(override.get("anchor_y", defaults.get("anchor_y", 0.5))) * canvas_h
    anchor = override.get("anchor", defaults.get("anchor", "center"))

    if anchor == "bottom_center":
        x = int(cx - new_w / 2)
        y = int(ay - new_h)
    else:  # center
        x = int(cx - new_w / 2)
        y = int(ay - new_h / 2)

    # Fine pixel offsets
    x += int(override.get("dx", 0))
    y += int(override.get("dy", 0))

    canvas.alpha_composite(subject, (x, y))
    return canvas


def normalize_one(
    trait: dict,
    canvas_cfg: dict,
    overrides: dict,
    key_black: bool,
) -> Path | None:
    category = trait["category"]
    tid = trait["id"]
    if tid == "none" or trait.get("source_rel") is None:
        return None

    src = LAYERS_RAW / trait["source_rel"]
    if not src.exists():
        # try absolute source
        src = Path(trait.get("source") or "")
    if not src.exists():
        print(f"  MISSING: {tid} ({trait.get('source_rel')})", file=sys.stderr)
        return None

    defaults = canvas_cfg["category_defaults"].get(category, {})
    ov = overrides.get("traits", {}).get(tid, {})

    im = open_rgba(src)
    im = maybe_key_black_bg(im, enable=key_black)
    im = trim_transparent(im)

    out_im = place_on_canvas(
        im,
        canvas_cfg["width"],
        canvas_cfg["height"],
        defaults,
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
        im = Image.new("RGBA", (w, h), color)
        im.save(out_dir / f"{t['id']}.png", format="PNG")


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize trait layers to shared canvas")
    parser.add_argument("--category", choices=["face", "clothing", "hat", "accessory", "mask", "all"], default="all")
    parser.add_argument("--ids", nargs="*", help="Only normalize these trait ids")
    parser.add_argument("--key-black", action="store_true", help="Aggressive pure-black backdrop keying")
    parser.add_argument("--limit", type=int, default=0, help="Limit count per category (debug)")
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

    # Always rebuild solid backgrounds
    make_backgrounds(canvas_cfg, catalog["traits"]["background"])
    print(f"Backgrounds: {len(catalog['traits']['background'])}")

    total = 0
    for cat in categories:
        items = catalog["traits"][cat]
        if args.ids:
            items = [t for t in items if t["id"] in args.ids]
        if args.limit:
            items = [t for t in items if t["id"] != "none"][: args.limit]

        print(f"Normalizing {cat}: {len([t for t in items if t['id'] != 'none'])} traits…")
        for t in items:
            if t["id"] == "none":
                continue
            path = normalize_one(t, canvas_cfg, overrides, key_black=args.key_black)
            if path:
                total += 1

    print(f"Done. Wrote {total} normalized layers under {LAYERS_NORM}")


if __name__ == "__main__":
    main()
