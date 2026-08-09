#!/usr/bin/env python3
"""Curate production traits from raw wojak_pfp_project layers."""
from __future__ import annotations

import json
import re
from pathlib import Path

from paths import CONFIG, LAYERS_RAW, MANIFESTS

# Source folder → category
FACE_DIRS = ["faces", "faces2", "faces3"]
CLOTHING_DIRS = ["clothing", "clothing2", "hoodies"]
HAT_DIRS = ["hats"]
ACCESSORY_DIRS = ["accessories"]
MASK_DIRS = ["masks"]

# Filename stems / patterns to drop entirely
DROP_EXACT = {
    "blank_outline",
    "mask_blank_template",
    "small_simple_icon",
    "wojak_black_green_outline",  # outline base, not a face trait
    "simple_outline",
    "npc_gray_head",  # clothing2 misfile
    "npc_gray_head_alt",
    "HAT_CATALOG",
}

DROP_SUBSTRINGS = [
    "_v2",
    "_v3",
    "_alt",
]

# Extra-safe drops for broken / non-bust assets
DROP_PREFIXES = []

# special/ full-body kept out of production by not scanning that folder

TIER_HINTS = {
    "legendary": ["skeleton", "female_wojak", "devil", "vampire", "boomer_beard"],
    "epic": ["npc_gray", "bloody", "horror", "balaclava", "gas_mask", "medieval", "napoleonic"],
    "rare": ["crying", "beaten", "tuxedo", "military", "tactical", "cigar", "pipe", "cape"],
    "uncommon": ["smug", "angry", "flannel", "hoodie", "suit", "sunglasses", "glasses"],
}


def display_name(stem: str) -> str:
    s = stem
    s = re.sub(r"^wojak_", "", s)
    s = re.sub(r"^accessory_", "", s)
    s = re.sub(r"^mask_", "", s)
    s = s.replace("_", " ").strip()
    return s.title()


def should_drop(stem: str, name: str) -> bool:
    if stem in DROP_EXACT or name in DROP_EXACT:
        return True
    low = stem.lower()
    if any(x in low for x in DROP_SUBSTRINGS):
        return True
    if name.startswith("._"):
        return True
    if not name.lower().endswith((".png", ".webp", ".jpg", ".jpeg")):
        return True
    return False


def tier_for(stem: str, category: str) -> str:
    low = stem.lower()
    for tier, keys in TIER_HINTS.items():
        if any(k in low for k in keys):
            return tier
    if category == "mask":
        return "epic"
    return "common"


def weight_for(tier: str, category: str) -> float:
    base = {
        "common": 10.0,
        "uncommon": 6.0,
        "rare": 3.0,
        "epic": 1.5,
        "legendary": 0.5,
    }.get(tier, 5.0)
    # Faces should not be ultra-rare by default unless hinted
    if category == "face" and tier == "common":
        return 8.0
    return base


def collect_category(category: str, dirs: list[str]) -> list[dict]:
    items: list[dict] = []
    seen_stems: set[str] = set()
    for d in dirs:
        folder = LAYERS_RAW / d
        if not folder.is_dir():
            continue
        for path in sorted(folder.iterdir()):
            if not path.is_file():
                continue
            stem = path.stem
            if should_drop(stem, path.name):
                continue
            # de-dupe same stem across face folders (keep first)
            key = stem.lower()
            if key in seen_stems:
                continue
            seen_stems.add(key)
            tier = tier_for(stem, category)
            items.append(
                {
                    "id": stem,
                    "category": category,
                    "name": display_name(stem),
                    "source": str(path.resolve()),
                    "source_rel": str(path.relative_to(LAYERS_RAW)),
                    "weight": weight_for(tier, category),
                    "tier": tier,
                }
            )
    return items


def main() -> None:
    if not LAYERS_RAW.is_dir():
        raise SystemExit(f"Raw layers not found: {LAYERS_RAW}")

    faces = collect_category("face", FACE_DIRS)
    clothing = collect_category("clothing", CLOTHING_DIRS)
    hats = collect_category("hat", HAT_DIRS)
    accessories = collect_category("accessory", ACCESSORY_DIRS)
    masks = collect_category("mask", MASK_DIRS)

    # Load backgrounds
    bg_path = CONFIG / "backgrounds.json"
    backgrounds = json.loads(bg_path.read_text())["backgrounds"]
    bg_traits = [
        {
            "id": b["id"],
            "category": "background",
            "name": b["name"],
            "source": None,
            "source_rel": None,
            "color": b["color"],
            "weight": float(b["weight"]),
            "tier": b["tier"],
        }
        for b in backgrounds
    ]

    # None options for optional layers
    none_hat = {
        "id": "none",
        "category": "hat",
        "name": "None",
        "source": None,
        "source_rel": None,
        "weight": 40.0,
        "tier": "common",
    }
    none_acc = {
        "id": "none",
        "category": "accessory",
        "name": "None",
        "source": None,
        "source_rel": None,
        "weight": 38.0,
        "tier": "common",
    }
    none_mask = {
        "id": "none",
        "category": "mask",
        "name": "None",
        "source": None,
        "source_rel": None,
        "weight": 100.0,
        "tier": "common",
    }

    catalog = {
        "version": 1,
        "raw_root": str(LAYERS_RAW),
        "counts": {
            "background": len(bg_traits),
            "face": len(faces),
            "clothing": len(clothing),
            "hat": len(hats),
            "hat_with_none": len(hats) + 1,
            "accessory": len(accessories),
            "accessory_with_none": len(accessories) + 1,
            "mask": len(masks),
            "mask_with_none": len(masks) + 1,
            "total_renderable": len(faces)
            + len(clothing)
            + len(hats)
            + len(accessories)
            + len(masks),
        },
        "traits": {
            "background": bg_traits,
            "face": faces,
            "clothing": clothing,
            "hat": hats + [none_hat],
            "accessory": accessories + [none_acc],
            "mask": masks + [none_mask],
        },
    }

    out = CONFIG / "traits.json"
    out.write_text(json.dumps(catalog, indent=2))
    summary = CONFIG / "traits_summary.json"
    summary.write_text(json.dumps(catalog["counts"], indent=2))

    # Human-readable drop report
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    report = {
        "kept": catalog["counts"],
        "notes": [
            "Dropped *_v2, *_v3, *_alt near-duplicates",
            "Dropped blank/outline templates and tiny icons",
            "Excluded special/ full-body assets from production set",
            "Merged faces/faces2/faces3 and clothing/clothing2/hoodies",
        ],
    }
    (MANIFESTS / "curation_report.json").write_text(json.dumps(report, indent=2))

    print("Curated trait catalog →", out)
    for k, v in catalog["counts"].items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
