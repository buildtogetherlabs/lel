# Flawless production

## Layer model

| Layer | What it is |
|---|---|
| **Body** (`layers/base/body_base.png`) | Blank white head + neck + shoulders. **No eyes, nose, mouth, brows.** |
| **Face** (`layers/face/*.png`) | Facial features / expressions only, aligned to the blank head. |
| **Clothing / hat / accessory** | Drawn to fit the **body** outline (and face for glasses). |

Everything else aligns to the body. Faces swap without moving the body or clothes.

## Eye style

Use `template/face_eye_reference.jpg` as the target for how eyes should look when redrawing face layers.  
Different faces can have different expressions; they should share the same head placement as `body_base`.

## Draw clothing / hat / accessory

1. Open `layers/base/workbench_draw_here.png` (body + guides).  
2. Style ref from `style_ref/` if needed.  
3. Draw trait fitted to body (collar / shoulders / head for hats).  
4. Export 1000×1000 transparent PNG → `layers/{category}/{id}.png`.

## Draw / fix face layers

1. Body base locked underneath.  
2. Draw features on the blank face area (eyes like the reference, or other expressions).  
3. Prefer **features on transparent** over a second full head if possible.  
4. Save to `layers/face/{id}.png`.  

Existing face files may still include a full head; they work as overlays if the silhouette matches the body. Ideal long-term: features-only faces.

## QA

```bash
# blank body
python scripts/preview_trait.py --face none --background void_black --out output/previews/body_only.png

# body + face
python scripts/preview_trait.py --face wojak_slight_smile --background paper_white
```

No floating clothes, no shoulder gaps, glasses on eyes, hat on skull.
