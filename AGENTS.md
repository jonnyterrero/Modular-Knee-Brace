# Agent guide — Modular Knee Brace

Instructions for AI agents (Claude Code, Codex, Cursor and others) working in this repo. Start with [`HANDOFF.md`](HANDOFF.md) for the current state and next steps.

## The project

MK-Brace is a modular, 3D-printed, parametric knee brace (EGN 3433C course project, now being developed further), custom-fit to one wearer's left knee. Mechanical CAD lives in Fusion 360. This repo is the record of everything: code, schematics, drawings, assemblies, exports and progress notes.

## Ground rules

- Commit finished work to `main` and push; this repo is the project showcase.
- At the end of a session, update `HANDOFF.md` and add `docs/progress/YYYY-MM-DD-<topic>.md`.
- CAD binaries (`.f3d`, `.step`, `.stl`, SolidWorks files, `.docx`, `.pdf`) go through Git LFS; check `.gitattributes` before adding a new file type.
- Units: inches in CAD, millimetres in STL exports. Coordinates: Y up the leg, Z to the front, X lateral; Top Frame at the origin, knee axis at (0, −6.0, −0.5) in.
- Keep the wearer's personal and medical details out of new docs.
- This is not a certified medical device. Flag anything patient-connected (for example e-stim) as safety-critical.

## Repo map

| Path | Contents |
| --- | --- |
| `cad/fusion/` | Fusion archive, STEP, per-part STLs and Fusion API scripts (`scripts/`); see its README |
| `cad/solidworks-final/` | Final SolidWorks parts, assemblies and drawings the Fusion model was rebuilt from |
| `modular-knee-brace-package/` | Earlier SolidWorks Pack-and-Go hand-off (different part versions) |
| `docs/fusion-rebuild.md` | Measured dimensions, assembly layout, fit check, corrections |
| `docs/drawings/` | Dimensioned drawings and design sketches from the course report |
| `docs/progress/` | Dated session logs |

## Fusion 360 via MCP

- Fusion project: **Knee brace Design** (design *Modular Knee Brace*, folder *SolidWorks originals*). Save there, never in *Default Project*.
- Fusion's MCP server runs on **port 47182**, not the default 27182. On the dev machine, MATLAB's *MathWorks Service Host* serves HTTPS on 27182 from every login, which made the connector fail with `ECONNRESET` or "connection closed during the server/discover probe". The port is set in four places that must match:
  1. Fusion: Preferences → General → API → Fusion MCP Server Port = 47182
  2. Claude Desktop: Settings → Extensions → Autodesk Fusion → Port = 47182
  3. User environment variable `FUSION_MCP_URL=http://127.0.0.1:47182/mcp`, read by Claude Code projects that define a `fusion` server
  4. Any `.mcp.json` fallback URL
- Health check: `Get-NetTCPConnection -LocalPort 47182 -State Listen` should be owned by `Fusion360`. Fusion only restarts its server when the preference actually changes or Fusion restarts.
- A third-party add-in on port 9876 can print `[MCP] Server listening on localhost:9876` into script output right after Fusion starts, breaking one JSON response. Retry the call.
- Run repo scripts by loading the file (see `cad/fusion/README.md`) so the committed code is what runs.

### Fusion API gotchas seen here

- `design.snapshots.add()` snapped the first-created occurrence back to the origin. Place components with `addNewComponent(transform)` and keep the first component fixed.
- Build sketches while their occurrence is at the identity transform; `modelToSketchSpace` is used as if component space were model space.
- `design.analyzeInterference` returned `None`, and temporary-BRep intersections fail (`ASM_EDGECOIN`) on flush mating faces.
- `doc.save()` reports the previous version number until the upload finishes.

## Electronics (next)

Planned: ESP32, hinge-axis magnetic encoder, thigh and shin IMUs, pressure sensors, LiPo battery, BLE/USB. Put schematics, BOM and firmware under a new `electronics/` folder. A KiCad MCP server is configured on the dev machine.
