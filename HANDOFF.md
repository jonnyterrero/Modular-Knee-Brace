# Handoff — where the MK-Brace work stands

_Last updated 2026-10-20 by Claude Code (Opus 5.5). Session logs: [`docs/progress/`](docs/progress/) (latest: [`2026-10-20-electronics-plan-and-schematic.md`](docs/progress/2026-10-20-electronics-plan-and-schematic.md))._

Read this first when picking the project back up, and update it at the end of every session.

## Current state

- **Phase 1 (mechanical): Fusion rebuild done.** The brace is a 10-part Fusion 360 assembly: two parametric frames plus exact copies of the original connectors and hinges, with fit checked at every joint.
- **Fusion cloud:** project **Knee brace Design** holds the design **Modular Knee Brace** (v2) and the folder **SolidWorks originals** (the 9 converted reference parts). Save new Fusion work in this project, never in *Default Project*.
- **Repo:** exports and scripts in [`cad/fusion/`](cad/fusion/README.md); engineering notes in [`docs/fusion-rebuild.md`](docs/fusion-rebuild.md); the reference SolidWorks set in [`cad/solidworks-final/`](cad/solidworks-final/); drawings in [`docs/drawings/`](docs/drawings/).
- **Print-ready:** `cad/fusion/stl/` (millimetres). Print the Outer Hinge twice.

## Next up: electronics (Phase 2, sensing)

Decided 2026-10-20: **sensing only (no e-stim)**, **~12 h runtime**, **split placement** (MCU, encoder and shin IMU at the lateral hinge; LiPo on the thigh frame), **PETG** prototype. Parts, pin map and power budget are in [`electronics/README.md`](electronics/README.md): XIAO ESP32-S3, AS5600 + Ø6 mm diametric magnet on the hinge axis, 2× LSM6DSOX, 4× FSR 402, 1000 mAh protected 1S LiPo (~43 mA design load, ~18 h expected).

1. ~~Choose parts and write a power budget.~~ Done.
2. ~~Draw the schematic in KiCad.~~ Done: [`electronics/kicad/`](electronics/kicad/), PDF in `electronics/`, ERC 0 errors. Before layout: in KiCad run *Tools → Update Symbols from Library*, check the three project symbols against their datasheets, and assign a XIAO footprint.
   **Rev B (2026-10-20, paused mid-way)** after an external design review:
   - Done:
     - SW1 and a PTC fuse (F1) moved to the cell, so the harness is dead when off.
     - AS5600 DIR tied to GND; D7 is now spare.
     - 1.5 kΩ series resistors (R9–R12) on the FSR lines. Without them a hard press reads above the ADC's 2.9 V range at 12 dB.
     - ERC still 0 errors; netlist re-checked; PDF re-exported.
   - Still to do:
     - Clear the 15 library-mismatch warnings (*Update Symbols from Library*).
     - Verify the LSM6DSOX pinout against ST's DS12814. It was checked only against the pin-compatible LSM6DSO (AN5192 Table 1), because st.com blocks scripted downloads.
     - Confirm the XIAO battery pads, charge current (Seeed lists 50 or 100 mA) and footprint.
     - Write the review's pre-fabrication checklist into `electronics/README.md`.
     - Then start the full-build schematics.
   - Datasheet facts confirmed so far:
     - AS5600 (Infineon-hosted ams datasheet): in 3.3 V mode tie VDD5V and VDD3V3 together with 100 nF. 10 µF is needed only for OTP programming. Airgap 0.5–3 mm. **Magnet axis within 0.25 mm of package centre** (drives the Fusion mount tolerance). STATUS register 0x0B holds MD/ML/MH.
     - ESP32-S3: default GPIO drive 20 mA. ADC range at 12 dB is 0–2.9 V. GPIO3's strap only matters with JTAG eFuses set.
3. Design the mounts in Fusion: magnet pocket in the Inner Hinge boss tip, a thin-floor sensor pocket in the Outer Hinge cap (≤ 0.03 in floor), the lateral hinge enclosure, and a curved battery holder on the thigh frame that stays clear of the strap recess.
4. Bench-measure the ESP32-S3 + BLE current; the 35 mA figure is an estimate.
5. Update this file, add a `docs/progress/` entry, and commit to `main`.

## Resume on the desktop

1. Pull this repo (Git LFS required) and open it in Claude Code.
2. Start Fusion. Its MCP server must be on port **47182** (Preferences → General → API); [`AGENTS.md`](AGENTS.md#fusion-360-via-mcp) explains why.
3. Open **Knee brace Design / Modular Knee Brace** and confirm the Fusion tools respond.

## Known issues

- The frames lack the originals' small edge rounds and end-block draft (cosmetic).
- Connectors and hinges don't follow the frame parameters (copied geometry).
- About 0.003 in press fit on one side of each hinge seat, inherited from the originals.
