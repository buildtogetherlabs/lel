#!/usr/bin/env python3
"""
Register a face trait onto the master template canvas.

Scales the face so its content height matches the master skeleton and
pins the top of the head to face_placement.content_top.

This is a first-pass register — always spot-check against master_base.png.
For production, manually nudge via --dx/--dy/--scale if needed.

Usage:
  python scripts/register_face.py --id wojak_slight_smile
  python scripts/register_face.py --all-keep
  python scripts/register_face.py --id neutral_simple --scale 1.05 --dy 10
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

from paths import ROOT, LAYERS_RAW, CONFIG

TEMPLATE = ROOT / "template"
LAYERS_TEMPLATE = ROOT / "layers_template"
SKELETON = TEMPLATE / "skeleton.json"


def trim(im: Image.Image) -> Image.Image:
    a = im.convert("RGBA").split()[-1]
    bb = a.point(lambda v: 255 if v > 10 else 0).getbbox()
    return im.crop(bb) if bb else im


def register(
    src: Path,
    out: Path,
    skeleton: dict,
    scale_mul: float = 1.0,
    dx: int = 0,
    dy: int = 0,
) -> None:
    W = skeleton["canvas"]["width"]
    H = skeleton["canvas"]["height"]
    place = skeleton["face_placement"]
    content_top = float(place["content_top"])
    content_h = float(place["content_height"]) * scale_mul

    im = trim(Image.open(src).convert("RGBA"))
    target_h = max(1, int(H * content_h))
    scale = target_h / im.height
    nw = max(1, int(im.width * scale))
    nh = max(1, int(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = (W - nw) // 2 + dx
    y = int(H * content_top) + dy

    # safe paste
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tmp.paste(im, (x, y), im)
    canvas = Image.alpha_composite(canvas, tmp)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, format="PNG", optimize=True)


def resolve_source(face_id: str, keep_list: Path) -> Path | None:
    # search keep list paths, then raw tree
    if keep_list.exists():
        for line in keep_list.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            p = LAYERS_RAW / line if not line.startswith("layers_") else ROOT / line
            # keep list paths are relative to wojak_pfp_project
            p = LAYERS_RAW / line
            if p.stem == face_id and p.exists():
                return p
    for folder in ("faces", "faces2", "faces3"):
        for p in (LAYERS_RAW / folder).glob("*.png"):
            if p.stem == face_id:
                return p
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", help="Face trait id (filename stem)")
    ap.add_argument("--all-keep", action="store_true", help="Register all faces in faces_keep.txt")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--dx", type=int, default=0)
    ap.add_argument("--dy", type=int, default=0)
    args = ap.parse_args()

    skeleton = json.loads(SKELETON.read_text())
    keep_list = TEMPLATE / "faces_keep.txt"
    out_dir = LAYERS_TEMPLATE / "face"

    ids: list[str] = []
    if args.all_keep:
        for line in keep_list.read_text().splitlines():
            line = line.strip()
            if line:
                ids.append(Path(line).stem)
    elif args.id:
        ids = [args.id]
    else:
        raise SystemExit("Pass --id STEM or --all-keep")

    ok = 0
    for fid in ids:
        src = resolve_source(fid, keep_list)
        if not src:
            print(f"SKIP missing source: {fid}")
            continue
        out = out_dir / f"{fid}.png"
        register(src, out, skeleton, scale_mul=args.scale, dx=args.dx, dy=args.dy)
        ok += 1
        print(f"OK {fid} → {out.relative_to(ROOT)}")
    print(f"Registered {ok}/{len(ids)} faces")


if __name__ == "__main__":
    main()
