#!/usr/bin/env python3
"""
Automated alignment QA — no manual per-image review required.

Measures content bboxes of normalized layers + a sample of composites,
flags outliers, writes a report, and builds a diagnostic contact sheet.
"""
from __future__ import annotations

import json
import random
import statistics as stats
from pathlib import Path

from PIL import Image, ImageDraw

from paths import CONFIG, LAYERS_NORM, REPORTS
from composite import composite_token


def content_bbox(im: Image.Image, thr: int = 10):
    a = im.convert("RGBA").split()[-1]
    mask = a.point(lambda p: 255 if p > thr else 0)
    return mask.getbbox()


def frac_bbox(bb, w=1000, h=1000):
    x0, y0, x1, y1 = bb
    return {
        "top": y0 / h,
        "bot": y1 / h,
        "left": x0 / w,
        "right": x1 / w,
        "cx": (x0 + x1) / 2 / w,
        "cy": (y0 + y1) / 2 / h,
        "width": (x1 - x0) / w,
        "height": (y1 - y0) / h,
    }


# Expected ranges (fractions) after skeleton placement
EXPECTED = {
    "face": {"top": (0.03, 0.12), "bot": (0.80, 0.95), "cx": (0.45, 0.55), "height": (0.72, 0.88)},
    "clothing": {"top": (0.48, 0.62), "bot": (0.90, 1.01), "cx": (0.45, 0.55), "width": (0.70, 1.0)},
    "hat": {"bot": (0.14, 0.30), "cx": (0.42, 0.58), "width": (0.40, 0.85)},
    "accessory": {"cx": (0.40, 0.70), "cy": (0.28, 0.65)},
    "mask": {"top": (0.04, 0.14), "bot": (0.70, 0.90), "cx": (0.45, 0.55)},
}


def check_category(category: str) -> dict:
    folder = LAYERS_NORM / category
    if not folder.exists():
        return {"category": category, "n": 0, "flags": []}

    flags = []
    metrics = []
    for p in sorted(folder.glob("*.png")):
        if p.stem == "none":
            continue
        im = Image.open(p)
        bb = content_bbox(im)
        if not bb:
            flags.append({"id": p.stem, "issue": "empty"})
            continue
        m = frac_bbox(bb)
        m["id"] = p.stem
        metrics.append(m)
        exp = EXPECTED.get(category, {})
        for key, (lo, hi) in exp.items():
            val = m.get(key)
            if val is None:
                continue
            if val < lo or val > hi:
                flags.append(
                    {
                        "id": p.stem,
                        "issue": f"{key}={val:.3f} outside [{lo:.2f},{hi:.2f}]",
                    }
                )

    summary = {"category": category, "n": len(metrics), "flags": flags}
    if metrics:
        for key in ("top", "bot", "cx", "cy", "width", "height"):
            vals = [m[key] for m in metrics if key in m]
            if vals:
                summary[f"{key}_mean"] = round(stats.mean(vals), 3)
                summary[f"{key}_med"] = round(stats.median(vals), 3)
    return summary


def diagnostic_sheet(path: Path, combos: list[dict], cols: int = 5) -> None:
    thumbs = []
    for c in combos:
        img = composite_token(c)
        img.thumbnail((220, 220), Image.Resampling.LANCZOS)
        thumbs.append((img, c))

    pad = 8
    label_h = 36
    tw = 220
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (tw + pad + label_h) + pad), (28, 28, 32))
    draw = ImageDraw.Draw(sheet)
    for i, (img, c) in enumerate(thumbs):
        r, col = divmod(i, cols)
        x = pad + col * (tw + pad)
        y = pad + r * (tw + pad + label_h)
        bg = Image.new("RGB", (tw, tw), (40, 40, 46))
        ox = (tw - img.width) // 2
        oy = (tw - img.height) // 2
        bg.paste(img.convert("RGB"), (ox, oy), img if img.mode == "RGBA" else None)
        sheet.paste(bg, (x, y))
        label = f"{c['face'][:18]}\n{c['clothing'][:18]}\n{c.get('hat','none')[:18]}"
        draw.multiline_text((x + 2, y + tw + 2), label, fill=(200, 200, 200), spacing=1)
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, format="PNG")


def main() -> None:
    catalog = json.loads((CONFIG / "traits.json").read_text())
    report = {"categories": []}
    total_flags = 0

    for cat in ["face", "clothing", "hat", "accessory", "mask"]:
        s = check_category(cat)
        report["categories"].append(s)
        total_flags += len(s["flags"])
        print(f"{cat}: n={s['n']} flags={len(s['flags'])}")
        if s.get("top_med") is not None:
            print(f"  top_med={s.get('top_med')} bot_med={s.get('bot_med')} "
                  f"cx_med={s.get('cx_med')} h_med={s.get('height_med')} w_med={s.get('width_med')}")
        for f in s["flags"][:8]:
            print(f"  ! {f['id']}: {f['issue']}")
        if len(s["flags"]) > 8:
            print(f"  … +{len(s['flags'])-8} more")

    # Build diagnostic combos: fixed face + varied clothing/hats/glasses
    faces = [t["id"] for t in catalog["traits"]["face"]]
    clothes = [t["id"] for t in catalog["traits"]["clothing"]]
    hats = [t["id"] for t in catalog["traits"]["hat"] if t["id"] != "none"]
    glasses = [
        t["id"]
        for t in catalog["traits"]["accessory"]
        if any(k in t["id"] for k in ("glasses", "sunglasses"))
    ]
    bgs = [t["id"] for t in catalog["traits"]["background"]]

    random.seed(42)
    master_face = "neutral_calm" if "neutral_calm" in faces else faces[0]
    combos = []
    # 1) master face × several clothes (no hat)
    for cl in clothes[:6]:
        combos.append(
            {
                "background": "void_black",
                "face": master_face,
                "clothing": cl,
                "hat": "none",
                "accessory": "none",
                "mask": "none",
            }
        )
    # 2) master face × several hats
    for ht in hats[:6]:
        combos.append(
            {
                "background": "paper_white",
                "face": master_face,
                "clothing": clothes[0],
                "hat": ht,
                "accessory": "none",
                "mask": "none",
            }
        )
    # 3) glasses
    for gl in glasses[:4]:
        combos.append(
            {
                "background": "muted_blue",
                "face": master_face,
                "clothing": clothes[1] if len(clothes) > 1 else clothes[0],
                "hat": "none",
                "accessory": gl,
                "mask": "none",
            }
        )
    # 4) random full combos
    for _ in range(8):
        combos.append(
            {
                "background": random.choice(bgs),
                "face": random.choice(faces),
                "clothing": random.choice(clothes),
                "hat": random.choice(hats + ["none", "none"]),
                "accessory": random.choice(glasses + ["none", "none", "none"]),
                "mask": "none",
            }
        )

    sheet_path = REPORTS / "qa_diagnostic.png"
    diagnostic_sheet(sheet_path, combos, cols=6)
    report["diagnostic_sheet"] = str(sheet_path)
    report["total_flags"] = total_flags
    report["pass"] = total_flags < 40  # soft budget; refine over time

    out = REPORTS / "qa_alignment.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nTotal flags: {total_flags}")
    print(f"Diagnostic sheet → {sheet_path}")
    print(f"Report → {out}")
    print("PASS" if report["pass"] else "NEEDS_WORK")


if __name__ == "__main__":
    main()
