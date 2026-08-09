#!/usr/bin/env python3
"""
Export redraw workboards: master_base (faded) + current draft trait + guides.

Artists / AI can open these to redraw the trait cleanly onto 1000x1000.

  python scripts/export_redraw_boards.py --category clothing --limit 12
  python scripts/export_redraw_boards.py --category hat --limit 12
  python scripts/export_redraw_boards.py --category accessory --limit 12
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance

from paths import LAYERS_TEMPLATE, REPORTS, TEMPLATE


def board(master: Image.Image, trait: Image.Image, guides: Image.Image | None) -> Image.Image:
    W, H = 1000, 1000
    bg = Image.new("RGBA", (W, H), (50, 50, 58, 255))
    m = master.copy()
    # fade master
    a = m.split()[-1].point(lambda v: int(v * 0.45))
    m.putalpha(a)
    bg = Image.alpha_composite(bg, m)
    if trait.size != (W, H):
        trait = trait.resize((W, H), Image.Resampling.LANCZOS)
    bg = Image.alpha_composite(bg, trait.convert("RGBA"))
    if guides is not None:
        g = guides.convert("RGBA")
        # only keep non-dark guide lines roughly — use low opacity full overlay
        ga = g.split()[-1].point(lambda v: int(v * 0.35) if v > 0 else 0)
        # simpler: skip full guides image if it's already composited; use thin lines only from blank guides
    return bg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", choices=["clothing", "hat", "accessory", "face"], required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    master = Image.open(TEMPLATE / "master_base.png").convert("RGBA")
    guides_path = TEMPLATE / "master_template_blank_guides.png"
    guides = Image.open(guides_path).convert("RGBA") if guides_path.exists() else None

    src_dir = LAYERS_TEMPLATE / args.category
    out_dir = args.out or (REPORTS / "redraw_boards" / args.category)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(src_dir.glob("*.png"))
    if args.limit:
        files = files[: args.limit]

    for p in files:
        trait = Image.open(p).convert("RGBA")
        # checker + faded master + trait
        W = H = 1000
        canvas = Image.new("RGBA", (W, H), (45, 45, 52, 255))
        m = master.copy()
        # reduce master opacity
        r, g, b, a = m.split()
        a = a.point(lambda v: int(v * 0.40))
        m = Image.merge("RGBA", (r, g, b, a))
        canvas = Image.alpha_composite(canvas, m)
        if trait.size != (W, H):
            trait = trait.resize((W, H), Image.Resampling.LANCZOS)
        canvas = Image.alpha_composite(canvas, trait)
        if guides is not None:
            gr, gg, gb, ga = guides.split()
            # keep bright guide pixels only
            ga2 = Image.new("L", (W, H))
            # simple: composite guides at low alpha via point on non-near-bg
            gimg = guides.copy()
            ga = gimg.split()[-1].point(lambda v: min(120, v) if v > 30 else 0)
            gimg.putalpha(ga)
            canvas = Image.alpha_composite(canvas, gimg)
        out = out_dir / f"board_{p.stem}.png"
        canvas.save(out, format="PNG")
        print("wrote", out)

    print(f"Done: {len(files)} boards → {out_dir}")


if __name__ == "__main__":
    main()
