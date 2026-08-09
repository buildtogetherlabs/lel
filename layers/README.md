# layers/ — production build

## Stack (bottom → top)

1. **background/** — solid colors  
2. **base/body_base.png** — white body outline only (**no face features**)  
3. **face/** — facial features / expressions (separate files)  
4. **clothing/** — drawn to fit the body  
5. **mask/** — optional  
6. **accessory/** — glasses etc. (align to face/body)  
7. **hat/** — align to head outline  

## Base

| File | Role |
|---|---|
| `base/body_base.png` | Canonical blank white body (head/neck/shoulders) |
| `base/master_base.png` | Same as body_base |
| `base/workbench_draw_here.png` | Body + guides for redrawing traits |
| `base/blank_1000.png` | Empty canvas |

## Faces

`face/` = white expressions for mass gen.  
`face_special_1of1/` = gray/devil/etc. later.  

Face layers should supply **eyes, brows, nose, mouth** (and expression lines) aligned to the blank head.  
Reference for correct eye style: `template/face_eye_reference.jpg`.

## Clothing / hat / accessory

Empty until redrawn onto `body_base`.  
Style refs: `../style_ref/`.
