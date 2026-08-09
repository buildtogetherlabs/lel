# LEL — Flawless production path

**Goal:** Mint-ready PFPs that look intentional, not collage-shifted.

Auto-align of old tight-crop traits will **never** be flawless.  
For flawless, every production trait is a **new 1000×1000 RGBA PNG** drawn (or carefully registered) against the master base.

---

## Non-negotiables

1. **Canvas:** exactly `1000 × 1000` px, PNG, RGBA, transparent background  
2. **Master body:** `template/master_base.png` (white wojak, locked)  
3. **Guides:** `template/master_template_guides.png` / numbers in `skeleton.json`  
4. **White faces only** in mass gen (`layers_template/face/`)  
5. **Specials** (gray, devil, pepe, etc.) stay in `face_special_1of1/` for later 1-of-1s  
6. **No black plate** behind art — true alpha only  

If a layer is dropped on `master_base.png` with **zero** X/Y offset, it must fit.

---

## Folder roles

| Path | Role |
|---|---|
| `template/master_base.png` | Locked body — never change scale |
| `layers_template/face/` | White faces already on canvas (QA, tweak if needed) |
| `layers_template/clothing/` | **Replace** with redrawn 1000×1000 files |
| `layers_template/hat/` | **Replace** with redrawn files |
| `layers_template/accessory/` | **Replace** with redrawn files |
| `layers_raw/` | Style reference only — do not mint from here |
| `layers_template/*` auto-aligned | Draft / reference until redrawn |

Auto-aligned clothing/hats/accessories are **drafts**. Overwrite them with true redraws when ready.

---

## How to redraw one trait (Procreate / PS / AI)

1. Open a **1000×1000** document.  
2. Place `master_base.png` on a locked bottom layer (opacity ~40%).  
3. Optionally place guide overlay.  
4. Draw the trait on a new layer:
   - **Clothing:** collar under chin; cover white chest; shoulders full width; bottom may clip at y=1000  
   - **Hat:** brim sits on skull; no sky gap; no covering both eyes unless intentional  
   - **Glasses:** sit on eyes of the 3/4 face (slightly right of center is normal)  
5. Hide master + guides.  
6. Export **only the trait layer** →  
   `layers_template/{category}/{id}.png`  
7. QA:

```bash
python scripts/preview_trait.py \
  --face wojak_neutral_calm \
  --clothing YOUR_ID \
  --hat none \
  --background void_black
```

---

## Minimum set for a “flawless” proof (before 6,666)

| Category | Min count | Notes |
|---|---|---|
| Face (white) | 20–40 | Curate best of current 53; fix outliers |
| Clothing | 25–40 | All redrawn |
| Hat | 20–30 + None | All redrawn |
| Glasses | 10–15 + None | All redrawn |
| Background | 10–12 | Already OK |

**Gate:** 24 random combos with **zero** floating hats, zero collar-through-jaw, zero glasses not on eyes. Then scale supply.

---

## AI-assisted redraw (optional)

1. Control / reference: `master_base.png` + guide lines  
2. Style ref: old trait from `layers_raw/`  
3. Output must be cleaned and **re-placed** on 1000×1000 by hand  
4. Reject anything that moves the skull or changes neck width  

---

## What we stop doing

- Shipping mass gen from pure auto-offset of raw crops as “final”  
- Accumulating failed sample sets in git  
- Mixing special bases into the majority collection  

---

## Status language

- **Draft composite** = generator + auto-aligned layers (iteration)  
- **Production trait** = hand-verified 1000×1000 on master  
- **Mint set** = only production traits  

Flawless = production traits only.
