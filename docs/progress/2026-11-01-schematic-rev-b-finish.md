# 2026-11-01 — Schematic rev B finished

Claude Code (Opus 5.5). Follows the external design review logged in `2026-10-20-electronics-plan-and-schematic.md`.

## Changes

- **XIAO battery pads:** rev A used made-up pad numbers. Seeed's KiCad symbol and footprint show VBAT is pad 23 and GND is pad 24, on the module's underside. Pins 1–14 were already right.
- **XIAO footprint:** Seeed's `XIAO-ESP32-S3-SMD` copied into `electronics/kicad/MKBrace.pretty/` (CC BY-SA 4.0, from Seeed-Studio/OPL_Kicad_Library).
- **Battery plug:** added J4 so the cell can be unplugged.
- **ERC:** swapped the MCP server's embedded R, C and 2-pin connector symbols for KiCad 10's stock copies. ERC is now 0 errors and 6 intended warnings.
- **Sheet:** title block (rev B), shorter notes, overlaps removed.
- **Docs:** part numbers and the review's checklist with a status per item in `electronics/README.md`.

## Findings

- **The XIAO's charger is too slow for this cell.** It is an SGM40567, listed at about 50 mA on Seeed's wiki for this board (the table is ambiguous; resellers say 50 or 100 mA). That is roughly 10–20+ hours for 1000 mAh. Decided the same day: the cell unplugs at J4 and charges off the brace with a 500 mA charger.
- **The magnet axis must sit within 0.25 mm of the AS5600 package centre** (datasheet).

## Checks

`kicad-cli` ERC and netlist export. The final netlist matches the one checked by hand, net for net (18 nets).

A tidy script of mine damaged the schematic during this session by matching too much text. KiCad refused to load it, so it was caught immediately and restored from a backup, then the steps were replayed.

## Still open

- Check the LSM6DSOX pinout against ST's DS12814. st.com blocks scripted access, and the mirrors tried either failed or held a different part. It has only been checked against the sister LSM6DSO (AN5192).
- Choose the exact PTC, cell and charger.
- Split the sheet into separate boards for the full build.
