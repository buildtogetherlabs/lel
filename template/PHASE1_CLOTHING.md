# Phase 1 — Clothing (next traits)

Faces are good. **Next: clothing on blank body.**

Workbench: `layers/base/drawing_map.png`  
Collar line: **y = 0.69**  
Export to: `layers/clothing/{id}.png` (1000×1000, transparent, clothing only)

Boards (map + style ref): `reports/clothing_boards/`

- [ ] `black_tee` — ref `style_ref/clothing2/black_tee.png` → `layers/clothing/black_tee.png`
- [ ] `black_hoodie` — ref `style_ref/clothing2/black_hoodie.png` → `layers/clothing/black_hoodie.png`
- [ ] `charcoal_tee` — ref `style_ref/clothing2/charcoal_tee.png` → `layers/clothing/charcoal_tee.png`
- [ ] `blue_plaid_flannel` — ref `style_ref/clothing2/blue_plaid_flannel.png` → `layers/clothing/blue_plaid_flannel.png`
- [ ] `green_tee` — ref `style_ref/clothing2/green_tee.png` → `layers/clothing/green_tee.png`
- [ ] `navy_tee` — ref `style_ref/clothing2/navy_tee.png` → `layers/clothing/navy_tee.png`
- [ ] `ash_gray_tee` — ref `style_ref/clothing2/ash_gray_tee.png` → `layers/clothing/ash_gray_tee.png`
- [ ] `black_suit_black_tie` — ref `style_ref/clothing/black_suit_black_tie.png` → `layers/clothing/black_suit_black_tie.png`
- [ ] `navy_suit_red_tie` — ref `style_ref/clothing/navy_suit_red_tie.png` → `layers/clothing/navy_suit_red_tie.png`
- [ ] `denim_jacket_bandana` — ref `style_ref/clothing/denim_jacket_bandana.png` → `layers/clothing/denim_jacket_bandana.png`
- [ ] `black_blazer_tan_tshirt` — ref `style_ref/clothing/black_blazer_tan_tshirt.png` → `layers/clothing/black_blazer_tan_tshirt.png`
- [ ] `hawaiian_floral_shirt` — ref `style_ref/clothing2/hawaiian_floral_shirt.png` → `layers/clothing/hawaiian_floral_shirt.png`
- [ ] `red_black_flannel` — ref `style_ref/clothing2/red_black_flannel.png` → `layers/clothing/red_black_flannel.png`
- [ ] `white_shirt_black_bow_tie` — ref `style_ref/clothing/white_shirt_black_bow_tie.png` → `layers/clothing/white_shirt_black_bow_tie.png`
- [ ] `black_hoodie_drawstrings` — ref `style_ref/hoodies/black_hoodie_drawstrings.png` → `layers/clothing/black_hoodie_drawstrings.png`

## After first 5 clothes land

```bash
python scripts/build_catalog.py
python scripts/preview_trait.py --face wojak_slight_smile --clothing black_hoodie
```
