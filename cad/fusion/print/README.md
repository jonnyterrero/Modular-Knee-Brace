# MK-Brace print package

Send this whole folder to the printer or lab. Each STL is in **millimetres** and already sits on its print face at Z = 0, so slice it as loaded: no rotating, and no supports needed.

**Status:** prototype for a fit check, not a finished or load-bearing brace, and not a medical device. The geometry is checked (closed, outward-facing meshes; no part overlaps in the assembly; hinge motion −1° to 115°). **Nothing has been printed yet**, so print the hinge test pair first.

## Step 1: hinge test pair (about 2 hours, small)

Print `right-inner-hinge.stl` and one `outer-hinge.stl`. Push the outer onto the inner's snap post until it clicks, then rotate it.

- **Good:** it clicks in with firm thumb pressure, turns smoothly, stops just past straight and at about 115°.
- **Too tight, or a finger cracks:** report it. The design changes `hinge_clearance` or `snap_interference`; don't sand the fingers.
- **Loose or wobbly:** report it too.

## Step 2: the rest

| File | Qty | Bed size (mm) | Height (mm) | Layers at 0.2 / 0.3 mm | On the bed |
| --- | --- | --- | --- | --- | --- |
| `top-frame.stl` | 1 | 177.8 × 111.1 | 76.2 | 381 / 254 | Band end down, socket mouths up |
| `bottom-frame.stl` | 1 | 146.1 × 95.2 | 76.2 | 381 / 254 | Band end down, socket mouths up |
| `right-inner-hinge.stl` | 1 | 85.5 × 50.8 | 15.6 | 79 / 53 | Base down, snap post up |
| `left-inner-hinge.stl` | 1 | 50.8 × 85.5 | 15.6 | 79 / 53 | Base down, snap post up |
| `outer-hinge.stl` | **2** | 50.8 × 88.9 | 12.7 | 64 / 43 | Cap down |
| `upper-connector.stl` | **2** | 22.7 × 117.7 | 19.1 | 96 / 64 | On edge |
| `lower-connector.stl` | **2** | 17.1 × 114.3 | 19.1 | 96 / 64 | On edge |

Nine prints in all. Solid volume is about 490 cm³, about 620 g of PETG at 100% infill; real use is far less at normal infill.

## Settings

| Setting | Value | Why |
| --- | --- | --- |
| Material | **PETG** | Chosen for the worn prototype; tougher than PLA |
| Layer height | 0.2 mm (0.3 mm for the frames if the printer has a layer limit) | The frames are the tallest parts |
| Walls | At least 4 perimeters (0.4 mm nozzle) | The snap fingers are 1.8 mm thick and must print solid |
| Infill | Hinges and connectors 50%+; frames 25–35% | The hinges and connectors carry the load |
| Supports | **None** | No unsupported overhangs except the hinge socket roof, a 19.7 mm bridge any PETG profile handles |
| Brim | Yes, for the connectors (narrow on the bed) and the frames (tall) | Adhesion |
| Size compensation | **Off** (no XY or hole compensation) | Clearances are designed in at nominal size. The bed edges already have a 0.5 mm chamfer for elephant's foot |
| Minimum bed | 180 × 115 mm, 77 mm build height | For the Top Frame |

## Questions for the lab

- What's the printer's layer or height limit? If it's under 254 layers, the frames need shortening first. Tell the designer before printing them.
- Do they stock PETG?

## If the files change

These are generated from `cad/fusion/stl/` by `python cad/fusion/scripts/orient_for_print.py`, which also re-checks the meshes. Regenerate after any re-export from Fusion.
