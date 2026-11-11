# Handoff — where the MK-Brace work stands

_Last updated 2026-11-11 by Claude Code (Opus 5.5). Engineering notes: [`docs/progress/`](docs/progress/). The 2026-10-20 to 11-02 session's log, decisions, tooling notes and open items: [`docs/sessions/`](docs/sessions/README.md); start with [`open-items.md`](docs/sessions/open-items.md)._

Read this first when picking the project back up, and update it at the end of every session.

## Current state

- **Phase 1 (mechanical): Fusion rebuild done.** The brace is a 10-part Fusion 360 assembly built from scripts: two frames, four connectors and four hinge parts, redesigned for FDM printing on 2026-11-01.
- **Fusion cloud:** project **Knee brace Design** holds the design **Modular Knee Brace** (v3) and the folder **SolidWorks originals** (the 9 converted reference parts). Save new Fusion work in this project, never in *Default Project*.
- **Repo:** exports and scripts in [`cad/fusion/`](cad/fusion/README.md); engineering notes in [`docs/fusion-rebuild.md`](docs/fusion-rebuild.md); the reference SolidWorks set in [`cad/solidworks-final/`](cad/solidworks-final/); drawings in [`docs/drawings/`](docs/drawings/).
- **Print files:** `cad/fusion/stl/` (millimetres); quantities and orientations are in `cad/fusion/README.md`.

## Printability rework (2026-11-01, awaiting a test print)

The original hinges could not be printed and assembled: a 1.3 mm per-side snap interference through a solid ring, and near-zero gaps. The connectors, hinges and frame sockets were redesigned; see [`docs/progress/2026-11-01-printable-hinges-and-connectors.md`](docs/progress/2026-11-01-printable-hinges-and-connectors.md) and [`cad/fusion/README.md`](cad/fusion/README.md). 3D printing is a prototype stage; real parts come later.

Open:

- The printer's layer cap and model are still unknown. Frames are 381 layers at 0.2 mm (254 at 0.3), the tallest parts by far.
- There is no slicer on the dev machine, so nothing has been sliced or printed. Print one hinge pair first.
- The 180° frame wrap has not been checked on the wearer.

Electronics continues in parallel; the mount design waits on a printed hinge pair.

## Next up: electronics (Phase 2, sensing)

Decided 2026-10-20: **sensing only (no e-stim)**, **~12 h runtime**, **split placement** (MCU, encoder and shin IMU at the lateral hinge; LiPo on the thigh frame), **PETG** prototype. Parts, pin map and power budget are in [`electronics/README.md`](electronics/README.md): XIAO ESP32-S3, AS5600 + Ø6 mm diametric magnet on the hinge axis, 2× LSM6DSOX, 4× FSR 402, 1000 mAh protected 1S LiPo (~43 mA design load, ~18 h expected).

1. ~~Choose parts and write a power budget.~~ Done.
2. ~~Draw the schematics in KiCad.~~ Done: two boards in [`electronics/kicad/`](electronics/kicad/), PDFs in `electronics/`, ERC 0 errors. Run `python electronics/check_harness.py` after changing either one.
   **Rev B (2026-10-20, finished 2026-11-01 apart from the items below)** after an external design review:
   - Done:
     - SW1 and a PTC fuse (F1) moved to the cell, so the harness is dead when off.
     - AS5600 DIR tied to GND; D7 is now spare.
     - 1.5 kΩ series resistors (R9–R12) on the FSR lines. Without them a hard press reads above the ADC's 2.9 V range at 12 dB.
     - ERC still 0 errors; netlist re-checked; PDF re-exported.
   - Still to do:
     - Verify the LSM6DSOX pinout against ST's DS12814 (a person needs to download it; st.com blocks scripted access). It has only been checked against the LSM6DSO's AN5192 Table 1.
     - Parts chosen 2026-11-02: Adafruit 258 cell, Littelfuse 1206L050YR fuse, C&K PCM12SMTR switch, Adafruit 4410 charger. **Firmware must limit BLE TX to 9 dBm or less** (`electronics/README.md`, *Peak current*).
     - Done 2026-11-02: split into hinge and thigh board projects under `electronics/kicad/`. Scope confirmed as sensing only. Next: lay out the boards once the hinge test print settles the mounting.
     - Also done since: XIAO battery pads corrected to 23/24 with Seeed's footprint, ERC down to the 6 intended warnings, checklist in `electronics/README.md`.
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
- Hinge and connector dimensions are read when `build_print_parts` runs, so they need a re-run after a parameter change.
- Changing the frame half-angles in place breaks the strap bridge references; rebuild with the scripts.
