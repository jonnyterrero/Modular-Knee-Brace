# 2026-11-01 — Printable hinges and connectors

Claude Code (Opus 5.5).

## Why

The hinges had never printed. Two CSWPs had looked at the part and could not fix it. The goal for this round: a brace that prints, as a prototype stage before real parts.

## What was wrong with the originals

Measured from the Fusion bodies:

- **Mesh quality was fine:** watertight solids, shortest edge 0.64 mm, thinnest wall 2.3 mm. This was a design problem, not a bad model.
- **Snap fit:** a 0.502 in radius bulge had to pass a 0.452 in radius ring with a 0.35 in wall and no relief slits found. That is about 11% hoop stretch.
- **Clearances:** 0.05–0.5 mm radially, and 0–0.025 mm on three axial faces.
- **Connectors:** a 7.5°/10° loft twist. Standing up they are about 590 layers with layer lines across the bending load; lying down they need heavy support.

The reported "too many layers" does not match the hinge alone (63 layers flat at 0.2 mm). How the part was oriented when it failed is not known.

## What changed

- **Frames:** 180° wrap (was 165°/160°), which squares the sockets and centres them on the knee axis in Z, so the twist is gone. Flares removed, leaving a flat shoulder. `build_frames` defaults updated.
- **Connectors:** one prismatic profile per position, printed on edge. It jogs in X to reach the hinge. The same part is used on both sides.
- **Hinges:** cup and spigot with 0.41 mm running clearance, a six-finger slit snap post, a 45° barb seat that prints without support, and a through bore in the cap.

## Checks

Fusion booleans on the rebuilt assembly:

- No overlap between any mating pair at rest.
- Sweep: free from −1° to 115°. The extension stop engages by −2°; the arms touch by 120°. Thigh and shin parts do not otherwise collide across that range.
- Timeline: 150 items, none unhealthy.

Hand estimate of snap finger strain (cantilever, 0.76 mm deflection, 12.5 mm length, about 2.4 mm section depth including curvature): about 1.7%, against about 11% before. Not tested.

## Not done

- Nothing has been sliced or printed. There is no slicer on the dev machine.
- The printer's layer cap and model are unknown.
- The 180° wrap has not been fit-checked on the wearer.
