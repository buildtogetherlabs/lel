# Template system (hybrid path)

This folder is the **source of truth** for collection geometry.

## Files

| File | Purpose |
|---|---|
| `master_base.png` | Locked wojak body (`wojak_neutral_calm` on 1000×1000) |
| `master_template_guides.png` | Master + colored guide lines |
| `master_template_blank_guides.png` | Guides only (for artists) |
| `skeleton.json` | Numeric guide positions |
| `production_plan.json` | Counts, phases, face lists summary |
| `faces_keep.txt` | Faces to register to template |
| `faces_kill.txt` | Do not use in v1 |
| `faces_special.txt` | Possible 1/1 later (wrong frame for mass gen) |
| `face_candidates_sheet.png` | Visual grid of keep-cluster faces |
| `REDRAW_BRIEF.md` | Full redraw / register instructions |

## Workflow

1. Read `REDRAW_BRIEF.md`  
2. Draw or register traits into `../layers_template/{category}/`  
3. When gate counts are met, point generator at `layers_template/`  
4. Proof locally — only commit renders when quality-gated  

## Master choice

**`wojak_neutral_calm`** (faces2) — clean 3/4 bust, consistent aspect with the largest face cluster (~0.83), readable neck/shoulder for clothing.
