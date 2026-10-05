# Fusion 360 model

Parametric Fusion 360 rebuild of the MK-Brace (October 2026). The live design is **Modular Knee Brace** in the Fusion project **Knee brace Design**; the files here are exports of it plus the scripts that build it.

![Fusion 360 assembly](../../docs/images/fusion/assembly-iso.png)

## Files

| Path | What it is |
| --- | --- |
| `Modular-Knee-Brace.f3d` | Fusion archive with the full timeline, user parameters and all 10 parts (*File → Open → Open from my computer*) |
| `Modular-Knee-Brace.step` | Neutral STEP of the whole assembly in its assembled position |
| `stl/` | One binary STL per part, in **millimetres**, ready to slice |
| `scripts/` | Fusion API scripts that rebuild, measure and export the design |

### Parts and print quantities

| Part | STL | Qty | Source |
| --- | --- | --- | --- |
| Top Frame (thigh) | `top-frame.stl` | 1 | Native parametric (`build_frames`) |
| Bottom Frame (calf) | `bottom-frame.stl` | 1 | Native parametric (`build_frames`) |
| Upper Connector | `left-upper-connector.stl`, `right-upper-connector.stl` | 1 each | Original SolidWorks geometry |
| Lower Connector | `left-lower-connector.stl`, `right-lower-connector.stl` | 1 each | Original SolidWorks geometry |
| Inner Hinge | `left-inner-hinge.stl`, `right-inner-hinge.stl` | 1 each | Original SolidWorks geometry |
| Outer Hinge | `outer-hinge.stl` | **2** | Original SolidWorks geometry |

## Coordinates and units

- Model units are inches. Y is the leg axis (up), Z points to the front, X is lateral.
- The Top Frame is the assembly origin; the knee (hinge) axis is at (0, −6.0, −0.5) in.

## Frame parameters

Change them in *Modify → Change Parameters*; both frames, their sockets, gussets and strap paths follow.

| Parameter | Default | Meaning |
| --- | --- | --- |
| `top_frame_id` | 5.75 in | Top frame bore (thigh fit) |
| `bottom_frame_id` | 4.50 in | Bottom frame bore (calf fit) |
| `top_frame_half_angle` | 82.5° | Half the top frame's wrap |
| `bottom_frame_half_angle` | 80° | Half the bottom frame's wrap (matches the lower connectors' 10° tabs) |
| `frame_height` | 2.00 in | Band height |
| `frame_wall` | 0.50 in | Band thickness |
| `block_length`, `block_drop` | 1.00 in, 1.00 in | End block length; how far it drops toward the knee (also the gusset radius) |
| `tab_width`, `tab_thickness`, `tab_length` | 0.75, 0.25, 1.00 in | Connector tab |
| `fit_clearance` | 0.01 in | Per side, tab to socket |
| `socket_flare_depth` | 0.319 in | Flared socket mouth that seats the tab's R0.5 root |
| `strap_recess_height`, `strap_recess_depth` | 1.50 in, 0.125 in | Strap recess and strap slot |
| `lip_thickness` | 0.125 in | Strap bridge over each end-block slot |

The connectors and hinges are exact copies of the SolidWorks parts, so they do **not** follow these parameters (see [`docs/fusion-rebuild.md`](../../docs/fusion-rebuild.md)).

## Scripts

| Script | Does |
| --- | --- |
| `build_frames` | Creates the parameters and both parametric frames in the active design |
| `place_original_parts` | Copies the original connectors and hinges from *Knee brace Design / SolidWorks originals* and places them around the knee |
| `measure_part` | Prints size, volume, cylinder diameters and planar-face offsets of every body |
| `export_brace` | Writes the `.f3d`, `.step`, `stl/` and the `docs/images/fusion/` renders back into this repo |

Run one from Fusion: *Utilities → Add-Ins → Scripts and Add-Ins → + (Script) → select its folder → Run*.

Rebuild from scratch: new design → `build_frames` → `place_original_parts`. On 2026-10-04 this reproduced the saved design exactly (all 10 parts, volume and bounding box).

From Claude Code with the Fusion MCP connected, run a repo script by loading the file, so the committed code is what runs:

```python
import importlib.util


def run(_context: str):
    path = r'<repo>\cad\fusion\scripts\build_frames\build_frames.py'
    spec = importlib.util.spec_from_file_location('build_frames', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.run('')
```
