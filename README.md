# LEL

Generative Wojak PFP collection — target **6,666** (ERC-721 / Robinhood-compatible metadata).

Repo: [buildtogetherlabs/lel](https://github.com/buildtogetherlabs/lel)

## Base policy

**Majority = classic white wojak faces only.**

| Pool | Role |
|---|---|
| `layers_template/face/` (~53) | Mass collection faces (white) |
| `layers_template/face_special_1of1/` (~31) | Gray NPC, red devil, pink, skeleton, clown, soy, etc. — **1-of-1 later** |

See `template/base_policy.json`, `template/faces_white.txt`, `template/faces_special_1of1.txt`.

## Status

| Piece | State |
|---|---|
| Master template + skeleton | Locked |
| White faces registered | ~53 in `layers_template/face/` |
| Clothing / hats / accessories aligned to skeleton | Yes (`align_traits.py`) |
| Special faces parked for 1-of-1 | Yes |
| Generator reads `layers_template/` | Yes |
| Proof samples | Local only (gitignored) |

Alignment is **good enough to iterate**; full mint quality may still need per-trait redraws on clothing/hats. Special bases stay out of mass gen.

## Layout

| Path | What |
|---|---|
| `template/` | Master base, guides, policy, briefs |
| `layers_template/` | **Production** layers (white path) |
| `layers_raw/` | Archive / style reference |
| `layers_normalized/` | Legacy experiment (ignore for mint) |
| `scripts/` | align / catalog / generate / composite |
| `output/`, `reports/` | Local generates only |

## Commands

```bash
cd ~/Projects/wojak-collection   # or clone from GitHub
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Align clothing/hats/accessories to master skeleton
python scripts/align_traits.py

# Rebuild trait catalog from layers_template (white faces only)
python scripts/build_catalog.py

# Local completed samples
python scripts/generate_collection.py --count 36
python scripts/make_contact_sheet.py --limit 36 --out reports/samples_completed_36.png
open reports/samples_completed_36.png
```

## Layer order

Background → Face → Clothing → Mask → Accessory → Hat

## Flawless quality

Auto-align is for **draft** composites only. Mint-ready traits must be **redrawn as 1000×1000** layers against `template/master_base.png`.

See **`template/FLAWLESS_PRODUCTION.md`**.

Draft boards (master + trait): `python scripts/export_redraw_boards.py --category clothing --limit 12`

## Notes

- Generated renders are **not** committed (keeps the repo clean).
- Pepe tee / McDonald’s uniform excluded from mass clothing pool for now.
- Next quality step: redraw worst clothing/hats against `template/master_base.png` when auto-align isn’t enough.
