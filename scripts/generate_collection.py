#!/usr/bin/env python3
"""
Generate unique trait combinations and render tokens.

Usage:
  python scripts/generate_collection.py --count 50
  python scripts/generate_collection.py --count 6666
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

from paths import CONFIG, LAYERS, MANIFESTS
from composite import render_and_save


def load_json(path: Path):
    return json.loads(path.read_text())


def weighted_pick(items: list[dict]) -> dict:
    weights = [float(t.get("weight", 1.0)) for t in items]
    return random.choices(items, weights=weights, k=1)[0]


def combo_key(c: dict) -> str:
    return "|".join(
        [
            c["background"],
            c["face"],
            c["clothing"],
            c["hat"],
            c["accessory"],
            c["mask"],
        ]
    )


def is_valid(c: dict, rules: dict) -> bool:
    compat = rules.get("compatibility", {})
    mask = (c.get("mask") or "none").lower()
    acc = (c.get("accessory") or "none").lower()
    face = (c.get("face") or "").lower()
    hat = (c.get("hat") or "none").lower()

    if mask != "none" and compat.get("mask_blocks_glasses", True):
        heavy = compat.get("heavy_mask_keywords", [])
        glasses = compat.get("glasses_keywords", [])
        if any(k in mask for k in heavy) and any(k in acc for k in glasses):
            return False
        # also block any glasses with any mask by default for cleaner PFPs
        if any(k in acc for k in glasses):
            return False

    for rule in compat.get("face_hat_conflicts", []):
        if any(k in face for k in rule.get("face_contains", [])):
            if hat != "none" and any(k in hat for k in rule.get("hat_contains", [])):
                return False
    return True


def generate_combos(catalog: dict, rules: dict, count: int, seed: int) -> list[dict]:
    random.seed(seed)
    seen: set[str] = set()
    out: list[dict] = []

    bgs = catalog["traits"]["background"]
    faces = catalog["traits"]["face"]
    clothing = catalog["traits"]["clothing"]
    hats = catalog["traits"]["hat"]
    accessories = catalog["traits"]["accessory"]
    masks = catalog["traits"]["mask"]

    # Re-weight mask none using rules mask_rate approximately:
    # mask_none_weight is high; actual items keep their weights.
    # Soft-adjust: if mask_rate set, scale non-none down.
    mask_rate = float(rules.get("mask_rate", 0.09))
    # Build effective mask pool (white-base v1 may have mask=None only)
    mask_pool = []
    others = sum(float(x["weight"]) for x in masks if x["id"] != "none")
    for m in masks:
        if m["id"] == "none":
            if others <= 0:
                none_w = 1.0  # only None available
            else:
                # P(none) ≈ 1 - mask_rate
                none_w = others * (1 - mask_rate) / max(mask_rate, 1e-6)
            mask_pool.append({**m, "weight": none_w})
        else:
            mask_pool.append(m)

    attempts = 0
    max_attempts = count * 200
    while len(out) < count and attempts < max_attempts:
        attempts += 1
        c = {
            "background": weighted_pick(bgs)["id"],
            "face": weighted_pick(faces)["id"],
            "clothing": weighted_pick(clothing)["id"],
            "hat": weighted_pick(hats)["id"],
            "accessory": weighted_pick(accessories)["id"],
            "mask": weighted_pick(mask_pool)["id"],
        }
        if not is_valid(c, rules):
            continue
        k = combo_key(c)
        h = hashlib.sha256(k.encode()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        c["token_id"] = len(out) + 1
        c["combo_hash"] = h
        out.append(c)

    if len(out) < count:
        raise RuntimeError(f"Only generated {len(out)}/{count} unique valid combos")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=None, help="Number of tokens (default: proof_size from rules)")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Combos only, no render")
    parser.add_argument("--start-id", type=int, default=1)
    args = parser.parse_args()

    catalog = load_json(CONFIG / "traits.json")
    rules = load_json(CONFIG / "rules.json")
    canvas = load_json(CONFIG / "canvas.json")

    count = args.count or int(rules.get("proof_size", 50))
    seed = args.seed if args.seed is not None else int(rules.get("seed", 6666))

    print(f"Generating {count} combos (seed={seed})…")
    combos = generate_combos(catalog, rules, count, seed)

    MANIFESTS.mkdir(parents=True, exist_ok=True)
    manifest_path = MANIFESTS / f"combos_{count}.json"
    manifest_path.write_text(json.dumps(combos, indent=2))

    csv_path = MANIFESTS / f"combos_{count}.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "token_id",
                "background",
                "face",
                "clothing",
                "hat",
                "accessory",
                "mask",
                "combo_hash",
            ],
        )
        w.writeheader()
        for c in combos:
            w.writerow({k: c.get(k) for k in w.fieldnames})

    print("Manifest →", manifest_path)

    if args.dry_run:
        print("Dry run: skip render")
        return

    # Verify template layers exist (white-base production path)
    missing = []
    for c in combos:
        for cat in ("background", "face", "clothing", "hat", "accessory", "mask"):
            tid = c[cat]
            if tid == "none":
                continue
            if not (LAYERS / cat / f"{tid}.png").exists():
                missing.append(f"{cat}/{tid}")
    if missing:
        uniq = sorted(set(missing))
        print(
            f"ERROR: {len(uniq)} template layers missing. "
            "Run align_traits.py + ensure white faces in layers_template/face/.",
            file=sys.stderr,
        )
        for m in uniq[:30]:
            print(" ", m, file=sys.stderr)
        raise SystemExit(1)

    print(f"Rendering {count} images…")
    for c in combos:
        tid = c["token_id"]
        # re-number if start-id
        token_id = args.start_id + tid - 1
        render_and_save(token_id, c, catalog, rules, canvas)
        if tid % 10 == 0 or tid == count:
            print(f"  {tid}/{count}")

    print("Done.")
    print("  images → output/images/")
    print("  metadata → output/metadata/")


if __name__ == "__main__":
    main()
