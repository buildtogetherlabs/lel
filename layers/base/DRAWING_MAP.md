# Drawing map (source of truth for placement)

All production traits align to **`layers/base/body_base.png`** using this map.

## Open

| File | Use |
|---|---|
| `layers/base/drawing_map.png` | Full map + zones (primary) |
| `layers/base/drawing_map_clean.png` | Key lines only |
| `layers/base/drawing_map_with_face_check.png` | Body + sample face + lines (sanity check) |
| `layers/base/workbench_draw_here.png` | Same as full map — draw on this |

Numbers: `layers/base/skeleton.json` / `config/template_skeleton.json`

## Key guides (y = fraction of 1000px)

| Guide | y | Purpose |
|---|---|---|
| hat_brim | **0.19** | Bottom edge of hats / caps |
| eye_line | **0.39** | Pupils + glasses center |
| mouth | **0.56** | Mouth |
| chin | **0.64** | Bottom of face oval |
| collar | **0.69** | **Top of all clothing** |
| shoulder | **0.78** | Shoulder line |

## Key guides (x)

| Guide | x | Purpose |
|---|---|---|
| head_center_x | **0.55** | Head midline (3/4 view, not canvas center) |
| accessory_center_x | **0.53** | Glasses / eyes box center |
| eye_span | **0.38** | Width of glasses / eyes box |

## Zones

1. **HAT** (blue) — top of head → brow; brim on cyan line  
2. **FACE** (green) — features only on blank head; eyes in green box  
3. **CLOTHING** (pink) — from pink collar line to bottom of canvas  

## Layer stack

`background → body → face → clothing → mask → accessory → hat`

## How this was dialed

Measured from `body_base` silhouette width profile (head width peaks at eyes, neck narrows, shoulders expand), then adjusted with a sample face overlay so pupils land in the eyes box.

When redrawing: **trust the map, not the old style_ref placement.**
