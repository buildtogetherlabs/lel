# LEL

Generative Wojak PFP collection — target **6,666** (ERC-721 / Robinhood-compatible metadata).

Repo: [buildtogetherlabs/lel](https://github.com/buildtogetherlabs/lel)

## Strategy (current)

**Hybrid template path** — auto-align of raw mixed crops was abandoned (geometry incompatible).

1. Lock **one master body** (`wojak_neutral_calm`)
2. **Register** best faces to that skeleton  
3. **Redraw** clothing / hats / glasses against the master  
4. Only then generate proof → 6,666  

See **`template/REDRAW_BRIEF.md`** for the full art brief.

## Status

| Phase | State |
|---|---|
| Master template + guides | Done → `template/` |
| Face keep/kill curation | Done → `template/faces_*.txt` |
| First-pass face register | Done → `layers_template/face/` (~84) |
| Clothing / hat / glasses redraw | **Not started** (critical path) |
| Proof 50 / full 6666 | Blocked on redraw gate |

## Layout

| Path | What |
|---|---|
| `template/` | Master base, guides, skeleton, redraw brief, keep/kill lists |
| `layers_template/` | **Production** traits (template-registered / redrawn) |
| `layers_raw/` | Archive / style reference only |
| `layers_normalized/` | Legacy auto-align experiment (do not use for mint) |
| `config/` | Rules, backgrounds, skeleton copy |
| `scripts/` | Curate, register, generate, QA |
| `output/`, `reports/` | Local generates only (gitignored) |

## Quick start

```bash
git clone https://github.com/buildtogetherlabs/lel.git
cd lel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Inspect master template
open template/master_template_guides.png
open template/REDRAW_BRIEF.md

# Re-register faces to template (optional)
python scripts/register_face.py --all-keep

# After clothing/hats/glasses exist under layers_template/:
# (generator switch to layers_template comes next when art is ready)
```

## Quality gate (before another proof set)

From `template/REDRAW_BRIEF.md`:

- ≥ 20 faces in `layers_template/face/` (registered + QA’d)  
- ≥ 15 clothing **redrawn** to collar line  
- ≥ 12 hats **redrawn** to brim line  
- ≥ 8 glasses **redrawn** to eye line  
- Local spot-check: no floating hats / collar-through-face  

Until then, **do not** commit sample PNGs.

## Layer order

Background → Face → Clothing → Mask → Accessory → Hat
