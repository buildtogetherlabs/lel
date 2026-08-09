# LEL

Generative Wojak PFP collection pipeline — target supply **6,666** (ERC-721 / Robinhood-compatible metadata).

Repo: [buildtogetherlabs/lel](https://github.com/buildtogetherlabs/lel)

## Status

Art pipeline: normalize trait layers → local proof samples → scale to 6,666 → mint packaging.

**Generated renders are local-only** (gitignored). Nothing under `output/` or `reports/*.png` is committed until a quality-gated release snapshot is intentional.

| Piece | Location | In git? |
|---|---|---|
| Raw trait layers | `layers_raw/wojak_pfp_project/` | yes |
| Normalized 1000×1000 PNGs | `layers_normalized/` | yes |
| Trait catalog / rules | `config/` | yes |
| Generator scripts | `scripts/` | yes |
| Renders / proof / QA sheets | `output/`, `reports/` | **no** (local) |

## Quick start

```bash
git clone https://github.com/buildtogetherlabs/lel.git
cd lel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Rebuild trait catalog from raw layers
python scripts/curate_traits.py

# Normalize layers onto shared canvas
python scripts/normalize_batch.py

# Preview one combo (writes output/previews/ — local only)
python scripts/preview_trait.py \
  --face neutral_calm \
  --clothing black_hoodie \
  --hat cap_maga_red

# Local proof set (not committed)
python scripts/generate_collection.py --count 50
python scripts/make_contact_sheet.py --out reports/preview_50.png
python scripts/qa_alignment.py

# Full collection when ready (local)
python scripts/generate_collection.py --count 6666
```

## Layer order

Background → Face → Clothing → Mask → Accessory → Hat

## Config

- `config/canvas.json` — canvas size + layer order
- `config/traits.json` — curated production traits (`curate_traits.py`)
- `config/rules.json` — supply, seed, mask rate, compatibility
- `config/placement_overrides.json` — per-trait scale/offset tweaks
- `config/backgrounds.json` — solid background palette

## Housekeeping

- Do **not** commit proof runs or contact sheets by default.
- Failed / intermediate sample sets should be deleted, not left beside the next attempt.
- Re-run generate anytime; combos are deterministic via `config/rules.json` seed.
