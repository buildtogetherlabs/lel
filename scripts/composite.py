#!/usr/bin/env python3
"""Composite normalized layers into a single token image + metadata."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image

from paths import CONFIG, IMAGES, LAYERS_NORM, METADATA


def load_json(path: Path):
    return json.loads(path.read_text())


def layer_path(category: str, trait_id: str) -> Path | None:
    if not trait_id or trait_id == "none":
        return None
    p = LAYERS_NORM / category / f"{trait_id}.png"
    return p if p.exists() else None


def alpha_paste(base: Image.Image, overlay_path: Path | None) -> Image.Image:
    if overlay_path is None:
        return base
    overlay = Image.open(overlay_path).convert("RGBA")
    if overlay.size != base.size:
        overlay = overlay.resize(base.size, Image.Resampling.LANCZOS)
    return Image.alpha_composite(base, overlay)


def composite_token(combo: dict[str, Any], canvas: dict | None = None) -> Image.Image:
    canvas = canvas or load_json(CONFIG / "canvas.json")
    w, h = canvas["width"], canvas["height"]
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    order = canvas.get(
        "layer_order",
        ["background", "clothing", "face", "mask", "accessory", "hat"],
    )
    for cat in order:
        tid = combo.get(cat)
        img = alpha_paste(img, layer_path(cat, tid))
    return img


def metadata_for(
    token_id: int,
    combo: dict[str, Any],
    catalog: dict,
    rules: dict,
    image_uri: str | None = None,
) -> dict:
    def resolve_name(category: str, tid: str) -> str:
        if tid == "none" or not tid:
            return "None"
        for t in catalog["traits"].get(category, []):
            if t["id"] == tid:
                return t["name"]
        return tid.replace("_", " ").title()

    attrs = []
    for cat, label in [
        ("background", "Background"),
        ("face", "Face"),
        ("clothing", "Clothing"),
        ("hat", "Hat"),
        ("accessory", "Accessory"),
        ("mask", "Mask"),
    ]:
        attrs.append(
            {
                "trait_type": label,
                "value": resolve_name(cat, combo.get(cat, "none")),
            }
        )

    meta = rules.get("metadata", {})
    prefix = meta.get("name_prefix", "Wojak")
    out = {
        "name": f"{prefix} #{token_id}",
        "description": meta.get(
            "description", "Wojak PFP Collection — 6,666 unique wojaks."
        ),
        "attributes": attrs,
    }
    if image_uri:
        out["image"] = image_uri
    else:
        out["image"] = f"images/{token_id}.png"
    if meta.get("external_url"):
        out["external_url"] = meta["external_url"]
    return out


def render_and_save(
    token_id: int,
    combo: dict[str, Any],
    catalog: dict,
    rules: dict,
    canvas: dict | None = None,
) -> tuple[Path, Path]:
    IMAGES.mkdir(parents=True, exist_ok=True)
    METADATA.mkdir(parents=True, exist_ok=True)

    img = composite_token(combo, canvas)
    img_path = IMAGES / f"{token_id}.png"
    img.save(img_path, format="PNG", optimize=True)

    meta = metadata_for(token_id, combo, catalog, rules)
    meta_path = METADATA / f"{token_id}.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    return img_path, meta_path
