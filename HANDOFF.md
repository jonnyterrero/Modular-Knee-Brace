# Handoff — where the MK-Brace work stands

_Last updated 2026-10-04 by Claude Code (Opus 5.5). Full session log: [`docs/progress/2026-10-04-fusion-rebuild.md`](docs/progress/2026-10-04-fusion-rebuild.md)._

Read this first when picking the project back up, and update it at the end of every session.

## Current state

- **Phase 1 (mechanical): Fusion rebuild done.** The brace is a 10-part Fusion 360 assembly: two parametric frames plus exact copies of the original connectors and hinges, with fit checked at every joint.
- **Fusion cloud:** project **Knee brace Design** holds the design **Modular Knee Brace** (v2) and the folder **SolidWorks originals** (the 9 converted reference parts). Save new Fusion work in this project, never in *Default Project*.
- **Repo:** exports and scripts in [`cad/fusion/`](cad/fusion/README.md); engineering notes in [`docs/fusion-rebuild.md`](docs/fusion-rebuild.md); the reference SolidWorks set in [`cad/solidworks-final/`](cad/solidworks-final/); drawings in [`docs/drawings/`](docs/drawings/).
- **Print-ready:** `cad/fusion/stl/` (millimetres). Print the Outer Hinge twice.

## Next up (week of 2026-10-05): electronics

The README's Phase 2/3 plan: ESP32, a magnetic rotary encoder at the hinge (knee angle), dual IMUs (thigh + shin), pressure sensors (fit and load), a LiPo battery, BLE/USB.

1. Choose parts and write a power budget (target runtime → battery capacity).
2. Draw the schematics in KiCad (an MCP server is configured on the dev machine) or Fusion Electronics, under a new `electronics/` folder.
3. Design the mounts in Fusion. The report puts add-ons at the hinges first, so start with the encoder on the hinge axis and an enclosure for the MCU and battery.
4. Update this file, add a `docs/progress/` entry, and commit to `main`.

Open questions:

- Is electrical-stimulation (e-stim) therapy in scope? The report mentions an e-stim battery pack. Anything patient-connected is safety-critical: keep it a separate, isolated module and decide before designing the power system.
- Target runtime per charge, and where the battery and MCU should sit (thigh frame or hinge).
- Material for the first printed prototype (README: PLA/PETG now, nylon or carbon fibre later).

## Resume on the desktop

1. Pull this repo (Git LFS required) and open it in Claude Code.
2. Start Fusion. Its MCP server must be on port **47182** (Preferences → General → API); [`AGENTS.md`](AGENTS.md#fusion-360-via-mcp) explains why.
3. Open **Knee brace Design / Modular Knee Brace** and confirm the Fusion tools respond.

## Known issues

- The frames lack the originals' small edge rounds and end-block draft (cosmetic).
- Connectors and hinges don't follow the frame parameters (copied geometry).
- About 0.003 in press fit on one side of each hinge seat, inherited from the originals.
