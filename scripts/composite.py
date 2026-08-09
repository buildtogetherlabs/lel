#!/usr/bin/env python3
"""Composite production layers into a token image + metadata."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image

from paths import CONFIG, IMAGES, LAYERS, METADATA


def load_json(path: Path):
    return json.loads(path.read_text())


def layer_path(category: str, trait_id: str) -> Path | None:
    if not trait_id or trait_id == "none":
        return None
    p = LAYERS / category / f"{trait_id}.png"
    return p if p.exists() else None


def alpha_paste(base: Image.Image, overlay_path: Path | None) -> Image.Image:
    if overlay_path is None:
        return base
    overlay = Image.open(overlay_path).convert("RGBA")
    if overlay.size != base.size:
        overlay = overlay.resize(base.size, Image.Resampling.LANCZOS)
    return Image.alpha_composite(base, overlay)


def composite_token(combo: dict[str, Any], canvas: dict | None = None) -> Image.Image:
    sk_path = CONFIG / "template_skeleton.json"
    if canvas is None and sk_path.exists():
        data = load_json(sk_path)
        w, h = data["canvas"]["width"], data["canvas"]["height"]
        order = data.get(
            "layer_order",
            ["background", "face", "clothing", "mask", "accessory", "hat"],
        )
    elif canvas is not None:
        w, h = canvas["width"], canvas["height"]
        order = canvas.get(
            "layer_order",
            ["background", "face", "clothing", "mask", "accessory", "hat"],
        )
    else:
        w = h = 1000
        order = ["background", "face", "clothing", "mask", "accessory", "hat"]

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for cat in order:
        img = alpha_paste(img, layer_path(cat, combo.get(cat)))
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
        attrs.append({"trait_type": label, "value": resolve_name(cat, combo.get(cat, "none"))})

    meta = rules.get("metadata", {})
    out = {
        "name": f"{meta.get('name_prefix', 'LEL')} #{token_id}",
        "description": meta.get(
            "description",
            "LEL — white-base Wojak PFP collection.",
        ),
        "attributes": attrs,
        "image": image_uri or f"images/{token_id}.png",
    }
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
    meta_path = METADATA / f"{token_id}.json"
    meta_path.write_text(json.dumps(metadata_for(token_id, combo, catalog, rules), indent=2))
    return img_path, meta_path
