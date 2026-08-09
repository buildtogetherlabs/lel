# LEL — Trait Redraw / Register Brief

**Strategy:** Hybrid template (recommended path)  
**Master face:** `wojak_neutral_calm`  
**Canvas:** 1000 × 1000 px, PNG RGBA, transparent background  
**Guides:** `template/master_template_guides.png` + `template/master_template_blank_guides.png`  
**Skeleton numbers:** `template/skeleton.json` / `config/template_skeleton.json`

---

## Goal

Every production trait must look like it belongs on the **same body**.  
If a layer is dropped on `master_base.png` with zero offset, it should fit — no “floating hat,” no collar through the chin.

Do **not** freehand off-canvas. Always draw against the master base + guide lines.

---

## Locked skeleton (do not freestyle)

| Guide | y (fraction) | ~px | Use for |
|---|---|---|---|
| head_top | 0.08 | 80 | Top of skull |
| hat_brim | 0.18 | 176 | Bottom edge of caps / brim sit |
| brow | 0.26 | 256 | Eyebrow band |
| **eye_line** | **0.34** | **336** | **Glasses / pupils** |
| nose | 0.46 | 464 | Nose tip band |
| mouth | 0.54 | 544 | Mouth / smoke |
| **chin** | **0.64** | **640** | Chin bottom |
| **collar** | **0.70** | **704** | **Top of all clothing** |
| shoulder | 0.84 | 840 | Shoulder seam |

- Center line x = 0.50  
- Head width ≈ 0.64 of canvas  
- Glasses width ≈ 0.36 of canvas (eye span box on guide)

Exact values live in `skeleton.json` — if they ever change, update art *and* the JSON together.

---

## Layer stack (bottom → top)

1. Background (solid, full canvas)  
2. Face (includes neck + upper chest white fill)  
3. Clothing (sits on chest; collar at `collar` line)  
4. Mask (optional epic)  
5. Accessory (glasses on `eye_line`; smoke near mouth)  
6. Hat (brim on `hat_brim`)

---

## Category briefs

### 1. Faces — *register, don’t invent a new head*

**Keep pool:** ~75 core + ~10 NPC rare → see `faces_keep.txt`  
**Kill:** `faces_kill.txt` (bad framing, junk, side profile, etc.)  
**Special / later 1-of-1:** `faces_special.txt`

**Process for each keep face:**
1. Open `master_base.png` as bottom reference (locked, 50% opacity).  
2. Scale/position the expression so:
   - Eyes sit on `eye_line`
   - Chin sits on `chin`
   - Neck width matches master
   - Head outline roughly matches master oval  
3. Export **only the face layer** (transparent bg) as `layers_template/face/{id}.png` at 1000×1000.  
4. Spot-check: composite face alone on mid-gray — no crop cut-off, no tiny floating head.

**Quality bar:** Swap any two registered faces with the same clothing — collars and hats still work.

**NPC gray faces:** Keep as rare tier; still register to the same skeleton (gray fill ok).

**Do not use for v1 production:** side profiles, female ponytail, extreme aspect outliers, tiny icons, outline-only bases.

---

### 2. Clothing — *redraw or heavy rebuild* (critical path)

Existing clothing is **not** template-compatible (aspect 1.2–5.8). Treat old files as **style reference only**, not layers to paste.

**Target count:** 40–50 pieces for v1.

**Process:**
1. Put `master_base.png` under a new layer.  
2. Draw clothing so:
   - **Top of collar / neckline = `collar` guide (y≈0.70)**  
   - Shoulders follow `shoulder` guide  
   - Width fills ~90–96% of canvas at shoulders  
   - Bottom can run off canvas (crop at y=1000)  
3. **Neck hole must reveal the master’s neck** — transparent where skin shows.  
4. No head, no face, no hat in the clothing file.  
5. Export `layers_template/clothing/{id}.png`.

**Suggested v1 wardrobe mix:**

| Tier | Count | Examples |
|---|---|---|
| Common | 18–22 | Solid tees, polos, hoodies, basic flannel |
| Uncommon | 12–15 | Suits, jackets, military shirts |
| Rare | 6–8 | Tactical, tuxedo, dress uniform |
| Epic | 2–4 | Armor / ultra meme (optional) |

**Style notes:**
- Match master line weight (chunky black outline, flat fills).  
- 3/4 view consistent with master (not pure front, not pure side).  
- Prefer clean silhouettes over tiny logos that fight the face.

**Drop for v1 (or defer):** full-body pieces, victorian dress+hat combos, anything that includes a head.

---

### 3. Hats — *redraw to brim line*

Old hats are style refs only.

**Target count:** 35–45 + **None** (~35–40% of tokens).

**Process:**
1. Master base visible.  
2. Hat **bottom / brim sits on `hat_brim` (y≈0.18)** and wraps the skull.  
3. Scale so hat width is ~55–70% of canvas (wider for cowboy/fedora).  
4. Transparent everywhere else.  
5. Export `layers_template/hat/{id}.png`.

**Buckets:**
- Baseball caps (high volume)  
- Beanies / bandanas  
- Buckets / boonies  
- Fedoras / wide brim (fewer)  
- Military / specialty (rare)

**Test:** On master + one tee, hat must touch the head with no sky gap and no buried eyes (unless intentional ski-mask style — those are masks, not hats).

---

### 4. Accessories — glasses first

**Glasses / sunglasses — target 12–18**

1. Master base visible.  
2. Lens centers on `eye_line`; width ≈ eye span box (~0.36 canvas).  
3. Arms may go back along the temple; keep stroke readable at thumbnail size.  
4. Export `layers_template/accessory/{id}.png`.

**Smoke / chains — target 8–12 (phase 2 ok)**  
- Cig / pipe: near `mouth`, slightly off-center (character’s right).  
- Chains: below `collar`, above chest art.

**Gas mask / full face:** treat as **mask** category, not glasses.

---

### 5. Masks — optional for v1

If included: 6–10 epic pieces, registered like faces (cover head, leave collar free).  
Else ship v1 with `mask = None` only.

---

### 6. Backgrounds — keep current approach

Solid colors from `config/backgrounds.json` are fine (already full-canvas). No redraw needed.

---

## Delivery checklist (per trait)

- [ ] 1000×1000 PNG RGBA  
- [ ] Transparent background (no black plate)  
- [ ] Snaps to correct guide(s) on master  
- [ ] Looks correct at 200×200 thumbnail  
- [ ] Filename = stable id (`black_hoodie.png`, not `IMG_1234.png`)  
- [ ] Composited once over master + default tee (or default face) and saved to local QA only  

---

## Folder layout (new production art)

```
layers_template/          # ONLY template-registered production assets
  face/
  clothing/
  hat/
  accessory/
  mask/                   # optional
  background/             # can symlink/copy from layers_normalized/background
```

Pipeline later reads **`layers_template/`** instead of auto-normalized raw dumps.

Raw archives stay in `layers_raw/` as reference only.

---

## AI-assisted regen (if not hand-drawing)

Use the same rules:

1. **Control image:** `master_base.png` + guide overlay.  
2. **Reference:** old trait for style/color only.  
3. **Prompt constraints:** “same head position, transparent background, no extra limbs, collar at neck line, flat cel-shaded wojak, black outline.”  
4. **Always** re-register output onto 1000×1000 against guides before accept.  
5. Reject anything that moves the skull.

Recommended loop: generate 4 candidates → pick 1 → manual cleanup of collar/brim → export.

---

## Definition of done (pipeline gate)

Before generating another 50 for “real”:

1. ≥ **20 faces** registered in `layers_template/face/`  
2. ≥ **15 clothing** redrawn  
3. ≥ **12 hats** redrawn  
4. ≥ **8 glasses** redrawn  
5. Local proof of 20 random combos: **no floating hats, no collar-through-face**  
6. Only then run `generate_collection.py --count 50` and consider committing a proof snapshot  

Until that gate, **do not** commit sample dumps to git.

---

## What we stop doing

- Auto-centering raw WebP crops as production  
- Shipping mixed face batches with different neck geometry  
- Treating clothing2 alts / v2 glasses as free extra supply without registration  
- Accumulating failed `preview_50` sets in the repo  
