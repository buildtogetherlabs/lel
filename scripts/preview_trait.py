#!/usr/bin/env python3
"""Preview a composite: body + face + optional traits."""
from __future__ import annotations

import argparse
from pathlib import Path

from paths import PREVIEWS
from composite import composite_token


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--background", default="void_black")
    p.add_argument("--body", default="body_base")
    p.add_argument("--face", default="none")
    p.add_argument("--clothing", default="none")
    p.add_argument("--hat", default="none")
    p.add_argument("--accessory", default="none")
    p.add_argument("--mask", default="none")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    combo = {
        "background": args.background,
        "body": args.body,
        "face": args.face,
        "clothing": args.clothing,
        "hat": args.hat,
        "accessory": args.accessory,
        "mask": args.mask,
    }
    img = composite_token(combo)

    PREVIEWS.mkdir(parents=True, exist_ok=True)
    out = Path(args.out) if args.out else PREVIEWS / (
        f"preview_{args.face}_{args.clothing}_{args.hat}.png"
    )
    img.save(out, format="PNG")
    print("Wrote", out)


if __name__ == "__main__":
    main()
