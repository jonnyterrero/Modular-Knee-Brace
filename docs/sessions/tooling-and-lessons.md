# Tooling and lessons

What a new Claude Code session on this machine needs to know before touching Fusion or KiCad.

## Fusion 360 via MCP

- **Port 47182, not the default 27182.** MATLAB's MathWorks Service Host takes 27182 at every login. The port is set in Fusion (Preferences → General → API), in the Claude Desktop extension settings, and in the user environment variable `FUSION_MCP_URL=http://127.0.0.1:47182/mcp`. Health check: `Get-NetTCPConnection -LocalPort 47182 -State Listen` should show `Fusion360`.
- **Save location:** project *Knee brace Design* only, never *Default Project*.
- **Build order:** new design → `build_frames` → `build_print_parts`. Run repo scripts by loading the file with `importlib` (see `cad/fusion/README.md`), so the committed code is what runs.
- **Don't change the frame half-angles in place.** The strap bridge and slot features lose their profile references and fall back to cached geometry. Rebuild the frames from the script instead.
- Fusion appends ` (2)` to new component names when a deleted component's name lingers. `export_brace` strips that from STL filenames.
- Older gotchas (from `AGENTS.md`):
  - `design.snapshots.add()` can snap occurrences back to the origin.
  - `analyzeInterference` returns `None`; use temporary-BRep booleans instead, which work once parts have real clearance.
  - `doc.save()` reports the old version until the upload finishes.
- There's no slicer on this machine, so printability is checked geometrically (layer counts, overhang area), not by slicing.

## KiCad 10 via MCP

- **Library search is broken**; placing parts by `Library:Symbol` name works. The server only knows the KiCad 8/9 install paths, and its URI regex cuts `C:/Program Files/...` at the space. To find stock symbol names, grep `C:\Program Files\KiCad\10.0\share\kicad\symbols\*.kicad_sym`.
- **Labels:** use `add_schematic_net_label` with `componentRef` and `pinNumber`, and orientation 180 / 0 / 90 / 270 for left / right / top / bottom pins. `connect_to_net` draws its wire stub into the symbol body.
- `add_schematic_text` stores `\n` as a literal backslash-n.
- Parts it places embed older symbol copies, which ERC flags as library mismatches. Fix by swapping in KiCad 10's stock copy, after checking the pin geometry matches.
- `run_erc`, `get_schematic_view` and `list_schematic_nets` sometimes time out. Use `kicad-cli` instead:
  - `kicad-cli sch erc --severity-all --format report`
  - `kicad-cli sch export netlist --format kicadxml`
- **Schematic files are single-line S-expressions.** Any scripted edit must:
  - match narrowly, using a quote-aware parser rather than regex across elements;
  - take a backup first;
  - confirm `kicad-cli` still loads the file;
  - compare the netlist before and after.

  A greedy regex wrecked the file once on 2026-11-01.
- Two board projects can't share nets. Run `python electronics/check_harness.py` after changing either schematic.

## Research

- st.com blocks scripted datasheet downloads, and the mirrors tried failed or held the wrong part. The LSM6DSOX datasheet needs a person to download it.
- The Seeed-Studio/OPL_Kicad_Library GitHub repo has readable KiCad sources for the XIAO, which settled pad numbers the schematic PDF couldn't.
- Python's `pypdf` is installed and reads most datasheets; PDF page rendering (`pdftoppm`) is not.

## Process lessons

- **Measure before redesigning.** The hinge problem was diagnosed from the model (interference and clearances), not guessed.
- **Check against the source.** The first schematic used invented XIAO battery pad numbers. Seeed's own files corrected them before layout.
- **Rebuild from scripts, don't patch.** The frames and schematics stayed reproducible because changes went into the build scripts or verified edits.
- A safety check blocks `rm` on paths built from shell variables. Write outputs to fresh filenames instead of deleting.
