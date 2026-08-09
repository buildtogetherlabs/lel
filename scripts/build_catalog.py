#!/usr/bin/env python3
"""Build config/traits.json from production layers/ (white-base set)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from paths import CONFIG, LAYERS, MANIFESTS


def display_name(stem: str) -> str:
    s = re.sub(r"^wojak_", "", stem)
    s = re.sub(r"^accessory_", "", s)
    s = re.sub(r"^mask_", "", s)
    return s.replace("_", " ").strip().title()


def list_traits(category: str, folder: Path, weight: float = 5.0, tier: str = "common") -> list[dict]:
    if not folder.is_dir():
        return []
    items = []
    for p in sorted(folder.glob("*.png")):
        items.append(
            {
                "id": p.stem,
                "category": category,
                "name": display_name(p.stem),
                "source_rel": str(p.relative_to(LAYERS)),
                "weight": weight,
                "tier": tier,
            }
        )
    return items


def main() -> None:
    bgs_cfg = json.loads((CONFIG / "backgrounds.json").read_text())
    backgrounds = [
        {
            "id": b["id"],
            "category": "background",
            "name": b["name"],
            "color": b["color"],
            "weight": float(b["weight"]),
            "tier": b["tier"],
            "source_rel": f"background/{b['id']}.png",
        }
        for b in bgs_cfg["backgrounds"]
    ]

    faces = list_traits("face", LAYERS / "face", weight=8.0)
    clothing = list_traits("clothing", LAYERS / "clothing", weight=6.0)
    hats = list_traits("hat", LAYERS / "hat", weight=4.0)
    accessories = list_traits("accessory", LAYERS / "accessory", weight=3.0)

    hats.append(
        {
            "id": "none",
            "category": "hat",
            "name": "None",
            "source_rel": None,
            "weight": 40.0,
            "tier": "common",
        }
    )
    accessories.append(
        {
            "id": "none",
            "category": "accessory",
            "name": "None",
            "source_rel": None,
            "weight": 38.0,
            "tier": "common",
        }
    )
    masks = [
        {
            "id": "none",
            "category": "mask",
            "name": "None",
            "source_rel": None,
            "weight": 100.0,
            "tier": "common",
        }
    ]

    special_dir = LAYERS / "face_special_1of1"
    specials = [p.stem for p in sorted(special_dir.glob("*.png"))] if special_dir.is_dir() else []

    catalog = {
        "version": 3,
        "base_policy": "white_only_majority",
        "layers_root": str(LAYERS),
        "counts": {
            "background": len(backgrounds),
            "face_white": len(faces),
            "face_special_1of1": len(specials),
            "clothing": len(clothing),
            "hat": len([h for h in hats if h["id"] != "none"]),
            "accessory": len([a for a in accessories if a["id"] != "none"]),
        },
        "special_1of1_faces": specials,
        "traits": {
            "background": backgrounds,
            "face": faces,
            "clothing": clothing,
            "hat": hats,
            "accessory": accessories,
            "mask": masks,
        },
    }

    out = CONFIG / "traits.json"
    out.write_text(json.dumps(catalog, indent=2))
    MANIFESTS.mkdir(exist_ok=True)
    (MANIFESTS / "catalog_counts.json").write_text(json.dumps(catalog["counts"], indent=2))
    print("Wrote", out)
    for k, v in catalog["counts"].items():
        print(f"  {k}: {v}")
    if catalog["counts"]["clothing"] == 0:
        print("NOTE: clothing/hat/accessory empty — redraw onto master, save into layers/")


if __name__ == "__main__":
    main()
