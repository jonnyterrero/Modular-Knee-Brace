# 2026-11-02 — Schematic split into hinge and thigh boards

Claude Code (Opus 5.5).

The user confirmed the full build is sensing only, so it comes down to two PCBs. KiCad has one PCB per project, so the single sheet became two projects.

## What changed

- **Projects:** `electronics/kicad/hinge-board/` and `electronics/kicad/thigh-board/`, sharing symbols and the XIAO footprint from `electronics/kicad/lib/`. The combined `mk-brace-sensing` project is gone (it remains in git history).
- **New on the thigh board:** J5, a 3-pin connector for the thigh FSRs, which the single sheet had drawn straight onto the harness. SW1 now has a board-mounted footprint.
- **Off-board parts:** BT1 and S1–S4 are marked not-on-board, so they stay in the schematics and BOM but won't appear on a PCB.
- **`electronics/check_harness.py`:** compares J1 and J3 pin for pin, because KiCad can't link nets across projects.

## Checks

- Combined netlist of both boards against the single-sheet netlist: 18 nets, and the only difference is J5 joining the thigh FSR nets.
- ERC with `kicad-cli`: 0 errors on both boards, and 3 intended warnings each (IMU pins tied off on purpose).
- `check_harness.py` passes on the real boards; its compare function fails correctly on swapped and missing pins.

## Not done

- No PCB layout yet. Board sizes depend on the battery cell and the printed hinge.
- Parts still to choose: cell, PTC, charger, and the exact switch.
- The LSM6DSOX pinout is still checked only against the sister LSM6DSO.
