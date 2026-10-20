# 2026-10-20 — Electronics plan and first schematic

Claude Code (Opus 5.5).

## 1. Picked the project back up

Fusion's MCP connection worked on port 47182. *Knee brace Design / Modular Knee Brace* v2 was open and healthy: 10 parts, 56 timeline items, no errors, user parameters as saved.

## 2. Scope decisions

Sensing only (e-stim out of scope), ~12 h per charge, split placement (MCU, encoder and shin IMU at the lateral hinge; LiPo on the thigh frame), PETG for the first print.

## 3. Hinge measurements for the encoder

Read from the Fusion bodies. The hinge axis is lateral. The Inner Hinge (thigh side) has a solid boss on the axis, which takes the magnet. The Outer Hinge (shin side) closes over it with a solid Ø2.00 in cap about 0.125 in thick. That is too thick for the AS5600's 0.5–3 mm gap, so the sensor mount needs a thin-floor pocket in the cap.

## 4. Parts and power budget

`electronics/README.md`: XIAO ESP32-S3, AS5600, 2× LSM6DSOX, 4× FSR 402, 1000 mAh protected LiPo. Design load ≈ 43 mA, about 18 h expected. The MCU + BLE figure is an estimate to bench-measure.

## 5. Schematic

- KiCad 10 project in `electronics/kicad/`, PDF in `electronics/`. One sheet: hinge board, thigh end of the 8-way harness, calf FSRs.
- Project symbols for the XIAO, AS5600 and LSM6DSOX (none in KiCad's stock library).
- Design choices made while drawing:
  - The thigh IMU's interrupt is not routed, which keeps the harness at 8 conductors. D9 is spare.
  - D7 drives the AS5600's DIR pin.
  - The power switch sits on the hinge board, after the harness.
  - The battery-sense divider sits after the switch, so it draws nothing when the brace is off.
- Checks:
  - ERC: 0 errors, 21 warnings, all expected; see `electronics/README.md`.
  - Netlist from `kicad-cli`: every net's members match the design.
- The KiCad MCP server's library search doesn't work on KiCad 10 (no 10.0 path, and URIs are cut at spaces). Placing parts by name still works.

## Next

Fusion mounts (magnet pocket, cap pocket, hinge enclosure, battery holder), bench current measurement, then PCB layout. See `HANDOFF.md`.
