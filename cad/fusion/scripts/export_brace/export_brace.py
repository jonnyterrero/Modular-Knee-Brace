"""Exports the Modular Knee Brace design: Fusion archive, STEP assembly, one STL per part (mm) and preview renders."""

import os

import adsk.core
import adsk.fusion

BASENAME = 'Modular-Knee-Brace'
RENDER_SIZE = (1600, 2000)
RENDERS = (
    ('assembly-iso.png', adsk.core.ViewOrientations.IsoTopRightViewOrientation),
    ('assembly-front.png', adsk.core.ViewOrientations.FrontViewOrientation),
    ('assembly-right.png', adsk.core.ViewOrientations.RightViewOrientation),
)


def repo_root() -> str:
    # scripts/export_brace/export_brace.py -> scripts -> fusion -> cad -> repository root
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))


def export_cad(design: adsk.fusion.Design, out_dir: str) -> list:
    manager = design.exportManager
    root = design.rootComponent
    archive = os.path.join(out_dir, f'{BASENAME}.f3d')
    step = os.path.join(out_dir, f'{BASENAME}.step')
    manager.execute(manager.createFusionArchiveExportOptions(archive, root))
    manager.execute(manager.createSTEPExportOptions(step, root))
    return [archive, step]


def export_stls(design: adsk.fusion.Design, out_dir: str) -> list:
    manager = design.exportManager
    stl_dir = os.path.join(out_dir, 'stl')
    os.makedirs(stl_dir, exist_ok=True)
    written, seen = [], set()
    root = design.rootComponent
    for i in range(root.occurrences.count):
        component = root.occurrences.item(i).component
        if component.name in seen or component.bRepBodies.count == 0:
            continue
        seen.add(component.name)
        path = os.path.join(stl_dir, component.name.lower().replace(' ', '-') + '.stl')
        options = manager.createSTLExportOptions(component.bRepBodies.item(0), path)
        options.isBinaryFormat = True
        options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        options.unitType = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        manager.execute(options)
        written.append(path)
    return written


def export_renders(app: adsk.core.Application, out_dir: str) -> list:
    os.makedirs(out_dir, exist_ok=True)
    viewport = app.activeViewport
    written = []
    for file_name, orientation in RENDERS:
        camera = viewport.camera
        camera.viewOrientation = orientation
        camera.isFitView = True
        viewport.camera = camera
        viewport.refresh()
        path = os.path.join(out_dir, file_name)
        viewport.saveAsImageFile(path, *RENDER_SIZE)
        written.append(path)
    return written


def run(_context: str) -> None:
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root_dir = repo_root()
    cad_dir = os.path.join(root_dir, 'cad', 'fusion')
    os.makedirs(cad_dir, exist_ok=True)
    written = export_cad(design, cad_dir) + export_stls(design, cad_dir)
    written += export_renders(app, os.path.join(root_dir, 'docs', 'images', 'fusion'))
    for path in written:
        print(f'{os.path.relpath(path, root_dir)}  {os.path.getsize(path) / 1024:.0f} KB')
