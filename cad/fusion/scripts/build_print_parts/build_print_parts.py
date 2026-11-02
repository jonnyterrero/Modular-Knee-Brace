"""Builds the FDM-printable connectors and hinges of the Modular Knee Brace in the active Fusion design; run after build_frames.

Connectors are prismatic profiles that print on edge with no supports. Hinges are a flat-printing cup and spigot with
FDM clearances and a slit six-finger snap post. They rely on the frames' 90 deg half-angles, which square the sockets
to the hinge plane and centre them on the knee axis in Z.

Hinge geometry is read from the user parameters at build time, so re-run after changing them.
"""

import math

import adsk.core
import adsk.fusion

CM_PER_IN = 2.54

PARAMETERS = (
    ('hinge_clearance', '0.016 in', 'in', 'Running clearance between hinge parts, radial and axial'),
    ('hinge_socket_clearance', '0.012 in', 'in', 'Clearance per side, connector tab to hinge socket'),
    ('hinge_stop_gap', '0.02 in', 'in', 'Gap from the outer hinge arm to the extension stop at full extension'),
    ('hinge_arm_root_width', '0.85 in', 'in', 'Hinge arm width at the hub; narrower allows more flexion'),
    ('snap_post_radius', '0.25 in', 'in', 'Snap post journal radius'),
    ('snap_wall', '0.07 in', 'in', 'Snap finger wall thickness'),
    ('snap_interference', '0.03 in', 'in', 'Radial barb-to-mouth interference each snap finger must deflect past'),
    ('snap_slit', '0.05 in', 'in', 'Width of the slits between snap fingers'),
    ('connector_body_thickness', '0.40 in', 'in', 'Connector body thickness between the tabs'),
)

# Knee axis and hinge stack, inches. Stack positions (s) are measured along the axis from the leg-side base face.
AXIS_Y, AXIS_Z = -6.0, -0.5
STACK_ORIGIN_X = 2.382
HUB_RADIUS = 1.0
BASE_THICKNESS = 0.125
INNER_TOP = 0.5
RECESS_RADIUS = 0.8125
CAP_THICKNESS = 0.125
INNER_ARM_END = 2.366
OUTER_ARM_END = 2.5
ARM_WIDTH = 1.0
ARM_TAPER_START, ARM_TAPER_END = 1.1, 1.37
TAB_CHAMFER = 0.03
BED_CHAMFER = 0.02

FRAME_MOUTH_UPPER_Y, FRAME_END_UPPER_Y = -1.0, 0.0
FRAME_MOUTH_LOWER_Y, FRAME_END_LOWER_Y = -11.0, -12.0
BODY_BEND_LENGTH = 0.3
BEND_RADIUS = 0.5


def cm(inches: float) -> float:
    return inches * CM_PER_IN


def point(x: float, y: float, z: float) -> adsk.core.Point3D:
    return adsk.core.Point3D.create(cm(x), cm(y), cm(z))


def real(inches: float) -> adsk.core.ValueInput:
    return adsk.core.ValueInput.createByReal(cm(inches))


def ensure_parameters(design: adsk.fusion.Design) -> None:
    params = design.userParameters
    for name, expression, units, comment in PARAMETERS:
        if params.itemByName(name) is None:
            params.add(name, adsk.core.ValueInput.createByString(expression), units, comment)


def param_in(design: adsk.fusion.Design, name: str) -> float:
    return design.userParameters.itemByName(name).value / CM_PER_IN


def plane_at(comp: adsk.fusion.Component, base: adsk.fusion.ConstructionPlane, offset: float, name: str):
    planes = comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(base, real(offset))
    plane = planes.add(plane_input)
    plane.name = name
    return plane


def polygon(sketch: adsk.fusion.Sketch, points) -> None:
    lines = sketch.sketchCurves.sketchLines
    model = [sketch.modelToSketchSpace(p) for p in points]
    first = lines.addByTwoPoints(model[0], model[1])
    previous = first
    for p in model[2:]:
        previous = lines.addByTwoPoints(previous.endSketchPoint, p)
    lines.addByTwoPoints(previous.endSketchPoint, first.startSketchPoint)


def largest_profile(sketch: adsk.fusion.Sketch) -> adsk.fusion.Profile:
    return max((sketch.profiles.item(i) for i in range(sketch.profiles.count)), key=lambda p: p.areaProperties().area)


class HingeBuilder:
    """Builds one hinge part directly in assembly coordinates on the side given by `sign` (+1 = +X)."""

    def __init__(self, comp: adsk.fusion.Component, sign: int):
        self.comp = comp
        self.sign = sign
        self.features = comp.features
        self.body = None

    def x(self, s: float) -> float:
        return self.sign * (STACK_ORIGIN_X + s)

    def at(self, s: float, front: float, along: float) -> adsk.core.Point3D:
        return point(self.x(s), AXIS_Y + along, AXIS_Z + front)

    def sketch_at(self, s: float, name: str) -> adsk.fusion.Sketch:
        plane = plane_at(self.comp, self.comp.yZConstructionPlane, self.x(s), f'{name} plane')
        sketch = self.comp.sketches.add(plane)
        sketch.name = name
        return sketch

    def extrude(self, profile, s_from: float, s_to: float, operation, name: str):
        extrudes = self.features.extrudeFeatures
        ext_input = extrudes.createInput(profile, operation)
        ext_input.setDistanceExtent(False, real(self.sign * (s_to - s_from)))
        if operation != adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
            ext_input.participantBodies = [self.body]
        feature = extrudes.add(ext_input)
        feature.name = name
        if self.body is None:
            self.body = feature.bodies.item(0)
            self.body.name = self.comp.name
        return feature

    def circle(self, s_from: float, s_to: float, radius: float, operation, name: str):
        sketch = self.sketch_at(s_from, name)
        center = sketch.modelToSketchSpace(self.at(s_from, 0, 0))
        sketch.sketchCurves.sketchCircles.addByCenterRadius(center, cm(radius))
        return self.extrude(sketch.profiles.item(0), s_from, s_to, operation, name)

    def prism(self, s_from: float, s_to: float, outline, operation, name: str):
        sketch = self.sketch_at(s_from, name)
        polygon(sketch, [self.at(s_from, f, a) for f, a in outline])
        return self.extrude(largest_profile(sketch), s_from, s_to, operation, name)

    def revolve(self, outline, operation, name: str):
        """Revolves (radius, s) outline points about the knee axis."""
        plane = plane_at(self.comp, self.comp.xYConstructionPlane, AXIS_Z, f'{name} plane')
        sketch = self.comp.sketches.add(plane)
        sketch.name = name
        polygon(sketch, [self.at(s, 0, r) for r, s in outline])
        axis = sketch.sketchCurves.sketchLines.addByTwoPoints(
            sketch.modelToSketchSpace(self.at(-0.2, 0, 0)), sketch.modelToSketchSpace(self.at(1.0, 0, 0)))
        axis.isConstruction = True
        revolves = self.features.revolveFeatures
        rev_input = revolves.createInput(largest_profile(sketch), axis, operation)
        rev_input.setAngleExtent(False, adsk.core.ValueInput.createByString('360 deg'))
        rev_input.participantBodies = [self.body]
        feature = revolves.add(rev_input)
        feature.name = name
        return feature

    def socket(self, s_center: float, along_end: float, depth: float, half_width: float, half_thickness: float,
               name: str) -> None:
        y = AXIS_Y + along_end
        plane = plane_at(self.comp, self.comp.xZConstructionPlane, y, f'{name} plane')
        sketch = self.comp.sketches.add(plane)
        sketch.name = name
        low, high = self.x(s_center - half_thickness), self.x(s_center + half_thickness)
        polygon(sketch, [point(low, y, AXIS_Z - half_width), point(high, y, AXIS_Z - half_width),
                         point(high, y, AXIS_Z + half_width), point(low, y, AXIS_Z + half_width)])
        extrudes = self.features.extrudeFeatures
        ext_input = extrudes.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        direction = -1 if along_end > 0 else 1
        ext_input.setDistanceExtent(False, real(direction * depth))
        ext_input.participantBodies = [self.body]
        extrudes.add(ext_input).name = name

    def bed_chamfer(self, s_face: float) -> None:
        """Elephant's-foot relief around the face that sits on the print bed."""
        target = cm(self.x(s_face))
        for face in self.body.faces:
            if face.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType \
                    and abs(face.pointOnFace.x - target) < 1e-4 and face.area > 1.0:
                edges = adsk.core.ObjectCollection.create()
                for edge in face.edges:
                    edges.add(edge)
                chamfers = self.features.chamferFeatures
                chamfer_input = chamfers.createInput2()
                chamfer_input.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges, real(BED_CHAMFER), False)
                chamfers.add(chamfer_input).name = 'Bed chamfer'
                return
        raise RuntimeError(f'{self.comp.name}: bed face not found')


def arm_outline(root_half: float, direction: int, end: float):
    half = ARM_WIDTH / 2
    return [(-root_half, 0), (root_half, 0), (root_half, direction * ARM_TAPER_START), (half, direction * ARM_TAPER_END),
            (half, direction * end), (-half, direction * end), (-half, direction * ARM_TAPER_END),
            (-root_half, direction * ARM_TAPER_START)]


def build_inner_hinge(design: adsk.fusion.Design, comp: adsk.fusion.Component, sign: int) -> float:
    """Thigh-side hinge: base plate, partial rim as the extension stop, slit snap post. Prints base down."""
    ops = adsk.fusion.FeatureOperations
    clearance = param_in(design, 'hinge_clearance')
    socket_clearance = param_in(design, 'hinge_socket_clearance')
    root_half = param_in(design, 'hinge_arm_root_width') / 2
    stop = root_half + param_in(design, 'hinge_stop_gap')
    post = param_in(design, 'snap_post_radius')
    wall = param_in(design, 'snap_wall')
    barb = param_in(design, 'snap_interference') + clearance  # the mouth already clears the post by one clearance
    slit = param_in(design, 'snap_slit')
    tab_width = param_in(design, 'tab_width')
    tab_thickness = param_in(design, 'tab_thickness')
    tab_length = param_in(design, 'tab_length')

    builder = HingeBuilder(comp, sign)
    builder.circle(0, INNER_TOP, HUB_RADIUS, ops.NewBodyFeatureOperation, 'Hub')
    builder.prism(0, INNER_TOP, arm_outline(root_half, 1, INNER_ARM_END), ops.JoinFeatureOperation, 'Arm')
    builder.circle(BASE_THICKNESS, INNER_TOP, RECESS_RADIUS, ops.CutFeatureOperation, 'Recess')

    # Everything behind the stop face opens up so the outer arm can swing through flexion; the front rim stays.
    opening = [(stop, -1.2), (stop, 0), (-root_half, 0), (-root_half, 1.05), (-1.2, 1.05), (-1.2, -1.2)]
    builder.prism(BASE_THICKNESS, INNER_TOP, opening, ops.CutFeatureOperation, 'Flexion opening')

    # Snap seat is defined by the outer hinge's bore; the barb sits one running clearance past it.
    seat = INNER_TOP
    post_top = seat + clearance + barb + 0.054
    barb_back = seat + clearance
    bore = post - wall
    builder.revolve([(bore, BASE_THICKNESS), (post, BASE_THICKNESS), (post, barb_back),
                     (post + barb, barb_back + barb), (post + barb, barb_back + barb + 0.014),
                     (post - 0.01, post_top), (bore, post_top)], ops.JoinFeatureOperation, 'Snap post')

    for index in range(3):
        angle = math.radians(60 * index)
        ux, uy = math.cos(angle), math.sin(angle)
        half_length, half_slit = post + barb + 0.05, slit / 2
        corners = [(ux * half_length - uy * half_slit, uy * half_length + ux * half_slit),
                   (ux * half_length + uy * half_slit, uy * half_length - ux * half_slit),
                   (-ux * half_length + uy * half_slit, -uy * half_length - ux * half_slit),
                   (-ux * half_length - uy * half_slit, -uy * half_length + ux * half_slit)]
        builder.prism(BASE_THICKNESS, post_top + 0.01, corners, ops.CutFeatureOperation, f'Snap slit {index + 1}')

    socket_center = INNER_TOP / 2
    builder.socket(socket_center, INNER_ARM_END, tab_length + socket_clearance, tab_width / 2 + socket_clearance,
                   tab_thickness / 2 + socket_clearance, 'Tab socket')
    builder.bed_chamfer(0)
    return socket_center


def build_outer_hinge(design: adsk.fusion.Design, comp: adsk.fusion.Component) -> float:
    """Shin-side hinge: cap and solid spigot with a through bore. Prints cap down, so the barb seat narrows at 45 deg."""
    ops = adsk.fusion.FeatureOperations
    clearance = param_in(design, 'hinge_clearance')
    socket_clearance = param_in(design, 'hinge_socket_clearance')
    root_half = param_in(design, 'hinge_arm_root_width') / 2
    post = param_in(design, 'snap_post_radius')
    barb = param_in(design, 'snap_interference') + clearance
    tab_width = param_in(design, 'tab_width')
    tab_thickness = param_in(design, 'tab_thickness')
    tab_length = param_in(design, 'tab_length')

    start = BASE_THICKNESS + clearance
    cap_under = INNER_TOP + clearance
    cap_top = cap_under + CAP_THICKNESS
    spigot = RECESS_RADIUS - clearance

    builder = HingeBuilder(comp, 1)
    builder.circle(cap_under, cap_top, HUB_RADIUS, ops.NewBodyFeatureOperation, 'Cap')
    builder.circle(start, cap_under, spigot, ops.JoinFeatureOperation, 'Spigot')
    builder.prism(start, cap_top, arm_outline(root_half, -1, OUTER_ARM_END), ops.JoinFeatureOperation, 'Arm')

    mouth = post + clearance
    seat_radius = post + barb + clearance
    lead_in = 0.03
    builder.revolve([(0, start - 0.01), (mouth + lead_in, start - 0.01), (mouth + lead_in, start), (mouth, start + lead_in),
                     (mouth, INNER_TOP), (seat_radius, INNER_TOP + (seat_radius - mouth)), (seat_radius, cap_top + 0.01),
                     (0, cap_top + 0.01)], ops.CutFeatureOperation, 'Bore and barb seat')

    socket_center = (start + cap_top) / 2
    builder.socket(socket_center, -OUTER_ARM_END, tab_length + socket_clearance, tab_width / 2 + socket_clearance,
                   tab_thickness / 2 + socket_clearance, 'Tab socket')
    builder.bed_chamfer(cap_top)
    return socket_center


def connector_outline(x_frame: float, x_hinge: float, y_frame_end: float, y_frame_mouth: float, y_hinge_mouth: float,
                      y_hinge_end: float, thickness: float, tab: float):
    """Prismatic outline in (x, y): frame tab, body with a straight jog between the frame and hinge lines, hinge tab."""
    direction = 1 if y_frame_mouth < y_frame_end else -1  # y increases toward the frame end when +1
    t, b, c = tab / 2, thickness / 2, TAB_CHAMFER
    bend_a = y_frame_mouth - direction * BODY_BEND_LENGTH
    bend_b = y_hinge_mouth + direction * BODY_BEND_LENGTH
    return [
        (x_frame - t + c, y_frame_end), (x_frame + t - c, y_frame_end), (x_frame + t, y_frame_end - direction * c),
        (x_frame + t, y_frame_mouth), (x_frame + b, y_frame_mouth), (x_frame + b, bend_a), (x_hinge + b, bend_b),
        (x_hinge + b, y_hinge_mouth), (x_hinge + t, y_hinge_mouth), (x_hinge + t, y_hinge_end + direction * c),
        (x_hinge + t - c, y_hinge_end), (x_hinge - t + c, y_hinge_end), (x_hinge - t, y_hinge_end + direction * c),
        (x_hinge - t, y_hinge_mouth), (x_hinge - b, y_hinge_mouth), (x_hinge - b, bend_b), (x_frame - b, bend_a),
        (x_frame - b, y_frame_mouth), (x_frame - t, y_frame_mouth), (x_frame - t, y_frame_end - direction * c),
    ], [(x_frame + b, bend_a), (x_hinge + b, bend_b), (x_hinge - b, bend_b), (x_frame - b, bend_a)]


def build_connector(design: adsk.fusion.Design, comp: adsk.fusion.Component, outline, bends) -> None:
    """Extrudes the outline across the tab width, rounds the jog, and chamfers both edge faces for on-edge printing."""
    tab_width = param_in(design, 'tab_width')
    plane = plane_at(comp, comp.xYConstructionPlane, AXIS_Z, 'Centre plane')
    sketch = comp.sketches.add(plane)
    sketch.name = 'Connector profile'
    polygon(sketch, [point(x, y, AXIS_Z) for x, y in outline])

    extrudes = comp.features.extrudeFeatures
    ext_input = extrudes.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_input.setSymmetricExtent(real(tab_width), True)
    feature = extrudes.add(ext_input)
    feature.name = 'Body'
    body = feature.bodies.item(0)
    body.name = comp.name

    edges = adsk.core.ObjectCollection.create()
    for edge in body.edges:
        mid = edge.pointOnEdge
        if any(abs(mid.x - cm(x)) < 1e-3 and abs(mid.y - cm(y)) < 1e-3 for x, y in bends):
            edges.add(edge)
    if edges.count != len(bends):
        raise RuntimeError(f'{comp.name}: expected {len(bends)} bend edges, found {edges.count}')
    fillets = comp.features.filletFeatures
    fillet_input = fillets.createInput()
    fillet_input.edgeSetInputs.addConstantRadiusEdgeSet(edges, real(BEND_RADIUS), False)
    fillets.add(fillet_input).name = 'Jog radii'

    body = comp.bRepBodies.item(0)
    edges = adsk.core.ObjectCollection.create()
    for face in body.faces:
        if face.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType \
                and abs(abs(face.pointOnFace.z - cm(AXIS_Z)) - cm(tab_width / 2)) < 1e-4:
            for edge in face.edges:
                edges.add(edge)
    chamfers = comp.features.chamferFeatures
    chamfer_input = chamfers.createInput2()
    chamfer_input.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges, real(BED_CHAMFER), False)
    chamfers.add(chamfer_input).name = 'Edge chamfers'


def add_part(root: adsk.fusion.Component, name: str) -> adsk.fusion.Occurrence:
    occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occurrence.component.name = name
    return occurrence


def mirror_side_transform() -> adsk.core.Matrix3D:
    """Half turn about the leg axis through the knee, which carries a +X part to the -X side."""
    matrix = adsk.core.Matrix3D.create()
    matrix.setToRotation(math.pi, adsk.core.Vector3D.create(0, 1, 0), point(0, 0, AXIS_Z))
    return matrix


def run(_context: str) -> None:
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    ensure_parameters(design)

    inner_center = build_inner_hinge(design, add_part(root, 'Right Inner Hinge').component, 1)
    build_inner_hinge(design, add_part(root, 'Left Inner Hinge').component, -1)
    outer = add_part(root, 'Outer Hinge')
    outer_center = build_outer_hinge(design, outer.component)

    thickness = param_in(design, 'connector_body_thickness')
    tab = param_in(design, 'tab_thickness')
    wall = param_in(design, 'frame_wall')
    x_top = param_in(design, 'top_frame_id') / 2 + wall / 2
    x_bottom = param_in(design, 'bottom_frame_id') / 2 + wall / 2
    tab_length = param_in(design, 'tab_length')

    upper = add_part(root, 'Upper Connector')
    y_mouth = AXIS_Y + INNER_ARM_END
    outline, bends = connector_outline(x_top, STACK_ORIGIN_X + inner_center, FRAME_END_UPPER_Y, FRAME_MOUTH_UPPER_Y,
                                       y_mouth, y_mouth - tab_length, thickness, tab)
    build_connector(design, upper.component, outline, bends)

    lower = add_part(root, 'Lower Connector')
    y_mouth = AXIS_Y - OUTER_ARM_END
    outline, bends = connector_outline(x_bottom, STACK_ORIGIN_X + outer_center, FRAME_END_LOWER_Y, FRAME_MOUTH_LOWER_Y,
                                       y_mouth, y_mouth + tab_length, thickness, tab)
    build_connector(design, lower.component, outline, bends)

    for occurrence in (outer, upper, lower):
        root.occurrences.addExistingComponent(occurrence.component, mirror_side_transform())
    print('Print parts built')
