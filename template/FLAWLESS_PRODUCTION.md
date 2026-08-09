# Flawless production — draw ON the white base

## Rule

Every clothing / hat / accessory file must fit `layers/base/master_base.png` with no offset hacks.

## Files

| Path | Role |
|---|---|
| `layers/base/master_base.png` | Locked white body |
| `layers/base/workbench_draw_here.png` | **Open this to draw** |
| `layers/base/blank_1000.png` | Empty canvas |
| `style_ref/` | Original designs (reference only) |
| `layers/face/` | White faces (ready) |
| `layers/clothing|hat|accessory/` | Save finished redraws here |

## Steps

1. Open `layers/base/workbench_draw_here.png` (locked).  
2. Optional: view matching file under `style_ref/` for colors/design.  
3. Draw trait on new layer fitted to guides (collar / eyes / hat brim).  
4. Hide workbench. Export **trait only**, 1000×1000 PNG RGBA.  
5. Save to `layers/{category}/{id}.png`.  
6. Check off `template/TRAIT_QUEUE.md`.  
7. QA: `python scripts/preview_trait.py --face wojak_neutral_calm --clothing ID`

## Do not

- Use `style_ref` files as final layers  
- Commit test composites into the repo  
- Put special faces into mass gen  
