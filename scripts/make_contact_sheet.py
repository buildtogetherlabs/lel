#!/usr/bin/env python3
"""Build a contact sheet grid from generated images for QA."""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from paths import IMAGES, REPORTS


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=IMAGES)
    p.add_argument("--out", type=Path, default=REPORTS / "preview_contact.png")
    p.add_argument("--thumb", type=int, default=200)
    p.add_argument("--cols", type=int, default=10)
    p.add_argument("--limit", type=int, default=50)
    args = p.parse_args()

    files = sorted(
        args.input.glob("*.png"),
        key=lambda x: int(x.stem) if x.stem.isdigit() else x.stem,
    )[: args.limit]
    if not files:
        raise SystemExit(f"No images in {args.input}")

    cols = args.cols
    rows = math.ceil(len(files) / cols)
    thumb = args.thumb
    pad = 8
    label_h = 18
    cell_w = thumb + pad
    cell_h = thumb + pad + label_h
    sheet = Image.new(
        "RGB",
        (cols * cell_w + pad, rows * cell_h + pad),
        (30, 30, 34),
    )
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for i, path in enumerate(files):
        r, c = divmod(i, cols)
        x = pad + c * cell_w
        y = pad + r * cell_h
        im = Image.open(path).convert("RGBA")
        im.thumbnail((thumb, thumb), Image.Resampling.LANCZOS)
        # center in cell
        ox = x + (thumb - im.width) // 2
        oy = y + (thumb - im.height) // 2
        bg = Image.new("RGBA", (thumb, thumb), (40, 40, 46, 255))
        bg.paste(im, ((thumb - im.width) // 2, (thumb - im.height) // 2), im)
        sheet.paste(bg.convert("RGB"), (x, y))
        label = path.stem
        draw.text((x + 4, y + thumb + 2), label, fill=(200, 200, 200), font=font)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out, format="PNG")
    print("Wrote", args.out, f"({len(files)} images)")


if __name__ == "__main__":
    main()
