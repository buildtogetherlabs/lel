# LEL

White-base Wojak PFP collection — target **6,666**.

## Architecture (flawless alignment)

```
background
    + body_base          ← blank white head/neck/shoulders (NO face)
    + face               ← eyes / expression / features (own files)
    + clothing           ← drawn to fit body
    + accessory          ← glasses etc.
    + hat
```

**Body and face are separate.** Clothing and hats align to the body outline; glasses align to the face on that body.

## Layout

```
layers/
  base/body_base.png       # blank body (canonical)
  base/workbench_draw_here.png
  face/                    # white face layers
  face_special_1of1/       # later 1-of-1s
  clothing/ hat/ accessory/  # empty → redraw here
  background/
style_ref/                 # originals for design reference
template/                  # docs + eye style reference
```

## Open these

| File | Why |
|---|---|
| `layers/base/body_base.png` | Blank body to align everything to |
| `layers/base/workbench_draw_here.png` | Draw clothing/hats/faces on this |
| `template/face_eye_reference.jpg` | Correct eye style for face redraws |
| `template/TRAIT_QUEUE.md` | What to redraw |
| `template/FLAWLESS_PRODUCTION.md` | How |

## Commands

```bash
cd ~/Projects/wojak-collection
source .venv/bin/activate

# body only
python scripts/preview_trait.py --face none --background void_black

# body + a face
python scripts/preview_trait.py --face wojak_neutral_calm --background paper_white

python scripts/build_catalog.py
python scripts/generate_collection.py --count 24   # after clothing exists
```

## Policy

- Mass gen: white body + white faces only  
- Special skins (gray, devil, etc.): 1-of-1 later  
- `style_ref/`: look only — do not mint as-is  
