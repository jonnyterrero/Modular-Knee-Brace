# 2026-10-02 to 2026-10-04 — SolidWorks to Fusion 360 rebuild

Claude Code (Opus 5.5). The work started in a session in the `workflows-and-automations` repo and was ported here.

## 1. Fixed the Fusion ↔ Claude connection

The Autodesk Fusion connector kept failing ("Version negotiation failed … server/discover probe", `ECONNRESET`). Root cause: MATLAB's MathWorks Service Host serves HTTPS on `127.0.0.1:27182`, the same default port as Fusion's MCP server, and starts at every login. Fusion moved to port 47182 and every client now points there (details in `AGENTS.md`). Verified across a full restart.

## 2. Recovered the real geometry

- Extracted the text and 23 figures from the final report; the six dimensioned drawings are in `docs/drawings/`.
- Uploaded the final SolidWorks parts to Fusion (*Knee brace Design / SolidWorks originals*) and measured every face.
- Findings: the drawing diameters are outside diameters (bores 5.75 and 4.50 in); the bands are 2.00 in tall; the sockets flare to seat the connectors' R0.5 tab roots; the connectors are lofted with a 7.5° / 10° twist; the hinge is a recess-and-spigot snap-fit pivot.

## 3. Built the model

- Native parametric frames (`build_frames`): band, end blocks, sockets with flared mouths, strap recess, R1.00 gussets, strap bridges and slots, all driven by user parameters.
- Exact copies of the original connectors and hinges (`place_original_parts`), positioned around the knee axis.
- Fit verified at every joint (see `docs/fusion-rebuild.md`).
- Decisions: the Bottom Frame wraps 80° because the original `Lower.SLDPRT` (82.5°) would jam the 10° lower connectors; the 0.014 in hinge tab-spacing mismatch is split between both seats; connectors and hinges stay as copies for now.

## 4. Saved and exported

- Fusion: *Knee brace Design / Modular Knee Brace* v2, with the converted originals moved into the same project.
- Repo: `cad/fusion/` (`.f3d`, `.step`, 9 STLs in mm, scripts), `cad/solidworks-final/`, renders, drawings and these notes.
- The repo scripts rebuilt the saved design exactly in a fresh document (all 10 parts, volume and bounding box).

## Next

Electronics; see `HANDOFF.md`.
