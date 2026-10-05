"""Copies the original SolidWorks connector and hinge bodies into the active design and places them around the knee axis."""

import adsk.core
import adsk.fusion

CM_PER_IN = 2.54
PROJECT_NAME = 'Knee brace Design'
FOLDER_NAME = 'SolidWorks originals'

# Knee (hinge) axis relative to the Top Frame, which sits at the assembly origin.
KNEE_IN = (0.0, -6.0, -0.5)

# Each placement maps a source file's coordinates into the knee frame: (origin [in], x-axis, y-axis, z-axis).
# The connector files were modelled around the knee, so they only need the knee offset. Hinge files have the
# hub at their origin, the plate in XZ and the arm along +Z; they are turned so the plate lies in the sagittal
# plane. Inner hinges sit at x = +/-2.382 in and the Outer Hinge nests 0.299 in outboard, which splits the
# 0.014 in difference between the original connectors' tab spacing and the hinge stack.
IDENTITY = ((0.0, 0.0, 0.0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
PARTS = (
    ('Right Upper Connector', 'Right_Upper_Connectorfinal', (IDENTITY,)),
    ('Left Upper Connector', 'Left_Upper_Connector', (IDENTITY,)),
    ('Right Lower Connector', 'Right_Lower_Connectorfinal', (IDENTITY,)),
    ('Left Lower Connector', 'Left_Lower_Connector', (IDENTITY,)),
    ('Right Inner Hinge', 'Right_Hinge_Innerfinal', (((2.382, 0.0, 0.0), (0, 0, 1), (1, 0, 0), (0, 1, 0)),)),
    ('Left Inner Hinge', 'Left_Hinge_Innerfinal', (((-2.382, 0.0, 0.0), (0, 0, -1), (-1, 0, 0), (0, 1, 0)),)),
    ('Outer Hinge', 'Hinge_Outerfinal', (((2.681, 0.0, 0.0), (0, 0, -1), (1, 0, 0), (0, -1, 0)),
                                         ((-2.681, 0.0, 0.0), (0, 0, 1), (-1, 0, 0), (0, -1, 0)))),
)


def source_folder(app: adsk.core.Application) -> adsk.core.DataFolder:
    projects = app.data.activeHub.dataProjects
    for i in range(projects.count):
        if projects.item(i).name == PROJECT_NAME:
            folder = projects.item(i).rootFolder.dataFolders.itemByName(FOLDER_NAME)
            if folder:
                return folder
    raise RuntimeError(f'"{PROJECT_NAME} / {FOLDER_NAME}" not found in the active hub')


def placement(spec) -> adsk.core.Matrix3D:
    origin, x_axis, y_axis, z_axis = spec
    matrix = adsk.core.Matrix3D.create()
    matrix.setWithCoordinateSystem(
        adsk.core.Point3D.create(*((o + k) * CM_PER_IN for o, k in zip(origin, KNEE_IN))),
        adsk.core.Vector3D.create(*x_axis),
        adsk.core.Vector3D.create(*y_axis),
        adsk.core.Vector3D.create(*z_axis))
    return matrix


def copy_source_body(app: adsk.core.Application, data_file: adsk.core.DataFile) -> adsk.fusion.BRepBody:
    document = app.documents.open(data_file, False)
    source = adsk.fusion.Design.cast(document.products.itemByProductType('DesignProductType')).rootComponent
    count = source.bRepBodies.count
    body = adsk.fusion.TemporaryBRepManager.get().copy(source.bRepBodies.item(0)) if count == 1 else None
    document.close(False)
    if body is None:
        raise RuntimeError(f'{data_file.name}: expected 1 body, found {count}')
    return body


def run(_context: str) -> None:
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    folder = source_folder(app)
    files = {folder.dataFiles.item(i).name: folder.dataFiles.item(i) for i in range(folder.dataFiles.count)}

    for comp_name, source_name, specs in PARTS:
        body = copy_source_body(app, files[source_name])
        occurrence = root.occurrences.addNewComponent(placement(specs[0]))
        comp = occurrence.component
        comp.name = comp_name
        base = comp.features.baseFeatures.add()
        base.startEdit()
        comp.bRepBodies.add(body, base)
        base.finishEdit()
        base.name = f'Original geometry ({source_name})'
        comp.bRepBodies.item(0).name = comp_name
        for spec in specs[1:]:
            root.occurrences.addExistingComponent(comp, placement(spec))
        print(f'{comp_name}: placed {len(specs)}x from {source_name}')
