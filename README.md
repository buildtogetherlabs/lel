# LEL

White-base Wojak PFP collection — target **6,666**.

Repo: [buildtogetherlabs/lel](https://github.com/buildtogetherlabs/lel)

## Clean layout

```
layers/
  base/                 # master white body + workbench (draw here)
  face/                 # white faces (mass gen) — 53
  face_special_1of1/    # gray/devil/etc. — later 1-of-1s — 31
  clothing/             # production redraws (empty until drawn)
  hat/
  accessory/
  background/           # solid BGs — ready
  mask/

style_ref/              # ORIGINAL trait art — style reference for redraw only
template/               # docs, queue, skeleton, master copies
scripts/                # build / preview / generate
config/
```

**Production rule:** clothing, hats, and accessories are drawn **on** the white master body (`layers/base/`), exported as transparent 1000×1000 layers into `layers/{category}/`.

## Start redrawing

1. Open workbench: `layers/base/workbench_draw_here.png`  
2. Checklist: `template/TRAIT_QUEUE.md`  
3. Style refs: `style_ref/clothing`, `style_ref/hats`, `style_ref/accessories`, …  
4. Export finished traits → `layers/clothing/`, `layers/hat/`, `layers/accessory/`  
5. Full instructions: `template/FLAWLESS_PRODUCTION.md`

```bash
cd ~/Projects/wojak-collection   # → Lacie
source .venv/bin/activate

python scripts/build_catalog.py
python scripts/preview_trait.py --face wojak_neutral_calm --clothing YOUR_ID
python scripts/generate_collection.py --count 24
```

## Layer stack

Background → Face → Clothing → Mask → Accessory → Hat

## Policy

| Pool | Use |
|---|---|
| White faces | Majority collection |
| Special faces | 1-of-1 later only |
| style_ref | Look at for design — do not mint as-is |
