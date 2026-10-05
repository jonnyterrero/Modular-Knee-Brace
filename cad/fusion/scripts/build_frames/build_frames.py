"""Builds the parametric Top and Bottom frames of the Modular Knee Brace in the active Fusion design."""

import math

import adsk.core
import adsk.fusion

CM_PER_IN = 2.54

PARAMETERS = (
    ('top_frame_id', '5.75 in', 'in', 'Top frame inner diameter (thigh fit)'),
    ('top_frame_half_angle', '82.5 deg', 'deg', 'Half of the top frame wrap angle'),
    ('bottom_frame_id', '4.50 in', 'in', 'Bottom frame inner diameter (calf fit)'),
    ('bottom_frame_half_angle', '80 deg', 'deg', 'Half of the bottom frame wrap angle'),
    ('frame_height', '2.00 in', 'in', 'Frame band height along the leg'),
    ('frame_wall', '0.50 in', 'in', 'Frame band radial thickness'),
    ('strap_recess_height', '1.50 in', 'in', 'Strap recess and strap slot height'),
    ('strap_recess_depth', '0.125 in', 'in', 'Strap recess and strap slot depth'),
    ('block_length', '1.00 in', 'in', 'End block length along the band tangent (= connector width)'),
    ('block_drop', '1.00 in', 'in', 'End block extension past the band toward the knee; also the gusset radius'),
    ('tab_width', '0.75 in', 'in', 'Connector tab width'),
    ('tab_thickness', '0.25 in', 'in', 'Connector tab thickness'),
    ('tab_length', '1.00 in', 'in', 'Connector tab length'),
    ('fit_clearance', '0.01 in', 'in', 'Clearance per side between tabs and sockets'),
    ('socket_flare_depth', '0.319 in', 'in', 'Depth of the flared socket mouth that seats the R0.5 tab root'),
    ('lip_thickness', '0.125 in', 'in', 'Strap bridge (lip) thickness over the end-block strap slot'),
)

FRAMES = (
    ('Top Frame', 'top_frame_id', 'top_frame_half_angle'),
    ('Bottom Frame', 'bottom_frame_id', 'bottom_frame_half_angle'),
)

# The bottom frame is the same design flipped about X, so its band wraps the back of the calf
# and its sockets face up toward the knee. Offset is from the Top Frame (assembly origin).
BOTTOM_FRAME_TRANSLATION_IN = (0.0, -12.0, -1.0)

SOCKET_WALL_TANGENTIAL = '(block_length - tab_width) / 2 - fit_clearance'
SOCKET_WALL_RADIAL = '(frame_wall - tab_thickness) / 2 - fit_clearance'


def value(expression: str) -> adsk.core.ValueInput:
    return adsk.core.ValueInput.createByString(expression)


def distance(expression: str) -> adsk.fusion.DistanceExtentDefinition:
    return adsk.fusion.DistanceExtentDefinition.create(value(expression))


def collection(items) -> adsk.core.ObjectCollection:
    result = adsk.core.ObjectCollection.create()
    for item in items:
        result.add(item)
    return result


def ensure_parameters(design: adsk.fusion.Design) -> None:
    params = design.userParameters
    for name, expression, units, comment in PARAMETERS:
        if params.itemByName(name) is None:
            params.add(name, value(expression), units, comment)


def nearest_endpoint(arc: adsk.fusion.SketchArc, point: adsk.core.Point3D) -> adsk.fusion.SketchPoint:
    start, end = arc.startSketchPoint, arc.endSketchPoint
    return start if start.geometry.distanceTo(point) < end.geometry.distanceTo(point) else end


def add_band_sector(sketch: adsk.fusion.Sketch, r_in: float, r_out: float, half: float,
                    id_expr: str, od_expr: str, angle_expr: str):
    """Fully constrained annular sector centred on the front (+Z) axis; returns (inner, outer, ends)."""
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    constraints = sketch.geometricConstraints
    dims = sketch.sketchDimensions

    def polar(r: float, phi: float) -> adsk.core.Point3D:
        return sketch.modelToSketchSpace(adsk.core.Point3D.create(r * math.cos(phi), 0, r * math.sin(phi)))

    front = math.pi / 2
    sides = {'right': front - half, 'left': front + half}
    inner = arcs.addByThreePoints(polar(r_in, sides['left']), polar(r_in, front), polar(r_in, sides['right']))
    outer = arcs.addByThreePoints(polar(r_out, sides['left']), polar(r_out, front), polar(r_out, sides['right']))
    constraints.addCoincident(inner.centerSketchPoint, sketch.originPoint)
    constraints.addCoincident(outer.centerSketchPoint, sketch.originPoint)
    dims.addDiameterDimension(inner, polar(r_in * 0.6, front + 0.25)).parameter.expression = id_expr
    dims.addDiameterDimension(outer, polar(r_out * 1.2, front - 0.25)).parameter.expression = od_expr

    axis = lines.addByTwoPoints(sketch.originPoint, polar(r_in, front))
    axis.isConstruction = True
    if abs(polar(1.0, front).x) < 1e-9:
        constraints.addVertical(axis)
    else:
        constraints.addHorizontal(axis)
    constraints.addCoincident(axis.endSketchPoint, inner)

    ends = {}
    for side, phi in sides.items():
        a = nearest_endpoint(inner, polar(r_in, phi))
        b = nearest_endpoint(outer, polar(r_out, phi))
        end = lines.addByTwoPoints(a, b)
        constraints.addCoincident(sketch.originPoint, end)
        dims.addAngularDimension(axis, end, polar(r_in * 0.45, (front + phi) / 2)).parameter.expression = angle_expr
        ends[side] = (phi, a, b, end)
    return inner, outer, ends


def add_end_blocks(sketch: adsk.fusion.Sketch, inner, outer, ends, r_in: float, wall: float, length: float,
                   wall_t: float, wall_n: float) -> None:
    """Tangent end blocks at both band ends, each with a constrained socket outline."""
    lines = sketch.sketchCurves.sketchLines
    constraints = sketch.geometricConstraints
    dims = sketch.sketchDimensions
    aligned = adsk.fusion.DimensionOrientations.AlignedDimensionOrientation

    for side, (phi, a_pt, b_pt, end) in ends.items():
        radial = (math.cos(phi), math.sin(phi))
        tangent = (math.sin(phi), -math.cos(phi)) if side == 'right' else (-math.sin(phi), math.cos(phi))

        def at(s_t: float, s_n: float, radial=radial, tangent=tangent) -> adsk.core.Point3D:
            x = (r_in + s_n) * radial[0] + s_t * tangent[0]
            z = (r_in + s_n) * radial[1] + s_t * tangent[1]
            return sketch.modelToSketchSpace(adsk.core.Point3D.create(x, 0, z))

        inner_edge = lines.addByTwoPoints(a_pt, at(length, 0))
        outer_edge = lines.addByTwoPoints(b_pt, at(length, wall))
        cap = lines.addByTwoPoints(inner_edge.endSketchPoint, outer_edge.endSketchPoint)
        constraints.addTangent(inner, inner_edge)
        constraints.addTangent(outer, outer_edge)
        constraints.addPerpendicular(cap, inner_edge)
        dims.addDistanceDimension(inner_edge.startSketchPoint, inner_edge.endSketchPoint, aligned,
                                  at(length / 2, -0.6)).parameter.expression = 'block_length'

        s1 = lines.addByTwoPoints(at(wall_t, wall_n), at(length - wall_t, wall_n))
        s2 = lines.addByTwoPoints(s1.endSketchPoint, at(length - wall_t, wall - wall_n))
        s3 = lines.addByTwoPoints(s2.endSketchPoint, at(wall_t, wall - wall_n))
        s4 = lines.addByTwoPoints(s3.endSketchPoint, s1.startSketchPoint)
        for socket_side, reference in ((s1, inner_edge), (s2, cap), (s3, outer_edge), (s4, end)):
            constraints.addParallel(socket_side, reference)
        dims.addOffsetDimension(inner_edge, s1, at(length / 2, wall_n / 2)).parameter.expression = SOCKET_WALL_RADIAL
        dims.addOffsetDimension(outer_edge, s3, at(length / 2, wall - wall_n / 2)).parameter.expression = SOCKET_WALL_RADIAL
        dims.addOffsetDimension(end, s4, at(wall_t / 2, wall / 2)).parameter.expression = SOCKET_WALL_TANGENTIAL
        dims.addOffsetDimension(cap, s2, at(length - wall_t / 2, wall / 2)).parameter.expression = SOCKET_WALL_TANGENTIAL


def plan_profiles(sketch: adsk.fusion.Sketch):
    band, rings, sockets = None, [], []
    for i in range(sketch.profiles.count):
        profile = sketch.profiles.item(i)
        if profile.profileLoops.count == 2:
            rings.append(profile)
        elif profile.areaProperties().area > 10:
            band = profile
        else:
            sockets.append(profile)
    if band is None or len(rings) != 2 or len(sockets) != 2:
        raise RuntimeError(f'{sketch.name}: expected band + 2 block rings + 2 sockets, '
                           f'got band={band is not None}, rings={len(rings)}, sockets={len(sockets)}')
    return band, rings, sockets


def profiles_by_side(sketch: adsk.fusion.Sketch) -> dict:
    result = {}
    for i in range(sketch.profiles.count):
        profile = sketch.profiles.item(i)
        entity = profile.profileLoops.item(0).profileCurves.item(0).sketchEntity
        side = 1 if sketch.sketchToModelSpace(entity.startSketchPoint.geometry).x > 0 else -1
        result[side] = profile
    if len(result) != 2:
        raise RuntimeError(f'{sketch.name}: expected one profile per side, got {sketch.profiles.count}')
    return result


def add_socket_flares(comp: adsk.fusion.Component, rings, sockets, body: adsk.fusion.BRepBody) -> None:
    """Lofted cut from the block outline at the socket mouth to the bore, seating the connector's R0.5 tab root."""
    planes = comp.constructionPlanes

    def offset_plane(expression: str, name: str) -> adsk.fusion.ConstructionPlane:
        plane_input = planes.createInput()
        plane_input.setByOffset(comp.xZConstructionPlane, value(expression))
        plane = planes.add(plane_input)
        plane.name = name
        return plane

    mouth = comp.sketches.add(offset_plane('-block_drop', 'Socket mouth'))
    mouth.name = 'Socket mouth outline'
    bore = comp.sketches.add(offset_plane('socket_flare_depth - block_drop', 'Socket flare depth'))
    bore.name = 'Socket bore outline'
    for ring in rings:
        outer_loop = next(loop for loop in ring.profileLoops if loop.isOuter)
        for curve in outer_loop.profileCurves:
            mouth.project(curve.sketchEntity)
    for socket in sockets:
        for curve in socket.profileLoops.item(0).profileCurves:
            bore.project(curve.sketchEntity)

    mouth_by_side, bore_by_side = profiles_by_side(mouth), profiles_by_side(bore)
    lofts = comp.features.loftFeatures
    for side in (1, -1):
        loft_input = lofts.createInput(adsk.fusion.FeatureOperations.CutFeatureOperation)
        loft_input.loftSections.add(mouth_by_side[side])
        loft_input.loftSections.add(bore_by_side[side])
        loft_input.participantBodies = [body]
        lofts.add(loft_input).name = 'Socket flare'


def add_gussets(comp: adsk.fusion.Component, r_in: float, r_out: float) -> None:
    """R=block_drop fillet where each end block meets the underside of the band."""
    edges = adsk.core.ObjectCollection.create()
    for edge in comp.bRepBodies.item(0).edges:
        if edge.geometry.curveType != adsk.core.Curve3DTypes.Line3DCurveType:
            continue
        start, end = edge.startVertex.geometry, edge.endVertex.geometry
        if abs(start.y) > 1e-4 or abs(end.y) > 1e-4:
            continue
        radii = sorted((math.hypot(start.x, start.z), math.hypot(end.x, end.z)))
        if abs(radii[0] - r_in) > 1e-3 or abs(radii[1] - r_out) > 1e-3:
            continue
        if abs(start.x * end.z - start.z * end.x) > 1e-3:
            continue
        edges.add(edge)
    if edges.count != 2:
        raise RuntimeError(f'{comp.name}: expected 2 gusset edges, found {edges.count}')
    fillets = comp.features.filletFeatures
    fillet_input = fillets.createInput()
    fillet_input.edgeSetInputs.addConstantRadiusEdgeSet(edges, value('block_drop'), False)
    fillets.add(fillet_input).name = 'Gussets'


def outer_block_lines(rings, r_out: float, length: float) -> list:
    far = math.hypot(r_out, length)
    found = []
    for ring in rings:
        outer_loop = next(loop for loop in ring.profileLoops if loop.isOuter)
        for curve in outer_loop.profileCurves:
            entity = curve.sketchEntity
            radii = sorted(math.hypot(p.geometry.x, p.geometry.y) for p in (entity.startSketchPoint, entity.endSketchPoint))
            if abs(radii[0] - r_out) < 1e-3 and abs(radii[1] - far) < 1e-3:
                found.append(entity)
    if len(found) != 2:
        raise RuntimeError(f'expected 2 outer end-block lines, found {len(found)}')
    return found


def add_strip_sketch(comp: adsk.fusion.Component, block_lines: list, name: str, sign: int,
                     offset: float, expression: str) -> adsk.core.ObjectCollection:
    """Strip of width `expression` along each block's outer line; sign +1 = outward, -1 = into the block."""
    sketch = comp.sketches.add(comp.xZConstructionPlane)
    sketch.name = name
    lines = sketch.sketchCurves.sketchLines
    constraints = sketch.geometricConstraints
    for block_line in block_lines:
        projected = adsk.fusion.SketchLine.cast(sketch.project(block_line).item(0))
        near, far = sorted((projected.startSketchPoint, projected.endSketchPoint),
                           key=lambda p: math.hypot(p.geometry.x, p.geometry.y))
        nx, ny = near.geometry.x, near.geometry.y
        scale = sign / math.hypot(nx, ny)
        ux, uy = nx * scale, ny * scale
        p1 = adsk.core.Point3D.create(nx + offset * ux, ny + offset * uy, 0)
        p2 = adsk.core.Point3D.create(far.geometry.x + offset * ux, far.geometry.y + offset * uy, 0)
        l1 = lines.addByTwoPoints(near, p1)
        l2 = lines.addByTwoPoints(l1.endSketchPoint, p2)
        l3 = lines.addByTwoPoints(l2.endSketchPoint, far)
        constraints.addPerpendicular(l1, projected)
        constraints.addParallel(l2, projected)
        constraints.addPerpendicular(l3, projected)
        midpoint = adsk.core.Point3D.create((p1.x + p2.x) / 2, (p1.y + p2.y) / 2, 0)
        sketch.sketchDimensions.addOffsetDimension(projected, l2, midpoint).parameter.expression = expression
    if sketch.profiles.count != 2:
        raise RuntimeError(f'{name}: expected 2 profiles, got {sketch.profiles.count}')
    return collection(sketch.profiles.item(i) for i in range(sketch.profiles.count))


def add_strap_bridges_and_slots(comp: adsk.fusion.Component, block_lines: list, lip: float, depth: float) -> None:
    """Strap path: a slot through each end block under an outer bridge, continuing the band's strap recess."""
    extrudes = comp.features.extrudeFeatures
    ops = adsk.fusion.FeatureOperations
    up = adsk.fusion.ExtentDirections.PositiveExtentDirection

    bridges = add_strip_sketch(comp, block_lines, 'Strap bridge', 1, lip, 'lip_thickness')
    bridge_input = extrudes.createInput(bridges, ops.JoinFeatureOperation)
    bridge_input.setOneSideExtent(distance('frame_height'), up)
    extrudes.add(bridge_input).name = 'Strap bridges'

    slots = add_strip_sketch(comp, block_lines, 'Strap slot', -1, depth, 'strap_recess_depth')
    slot_input = extrudes.createInput(slots, ops.CutFeatureOperation)
    slot_input.setOneSideExtent(distance('strap_recess_height'), up)
    slot_input.startExtent = adsk.fusion.OffsetStartDefinition.create(value('(frame_height - strap_recess_height) / 2'))
    slot_input.participantBodies = [comp.bRepBodies.item(0)]
    extrudes.add(slot_input).name = 'Strap slots'


def build_frame(design: adsk.fusion.Design, comp: adsk.fusion.Component, id_param: str,
                angle_param: str) -> adsk.fusion.BRepBody:
    params = design.userParameters

    def p(name: str) -> float:
        return params.itemByName(name).value

    r_in = p(id_param) / 2
    wall = p('frame_wall')
    r_out = r_in + wall
    half = p(angle_param)
    length = p('block_length')
    wall_t = (length - p('tab_width')) / 2 - p('fit_clearance')
    wall_n = (wall - p('tab_thickness')) / 2 - p('fit_clearance')

    plan = comp.sketches.add(comp.xZConstructionPlane)
    plan.name = 'Frame plan'
    inner, outer, ends = add_band_sector(plan, r_in, r_out, half, id_param, f'{id_param} + 2 * frame_wall', angle_param)
    add_end_blocks(plan, inner, outer, ends, r_in, wall, length, wall_t, wall_n)
    band, rings, sockets = plan_profiles(plan)

    # Sketches on the component XZ plane have a +Y normal, i.e. positive extents run up the leg.
    up = adsk.fusion.ExtentDirections.PositiveExtentDirection
    ops = adsk.fusion.FeatureOperations
    extrudes = comp.features.extrudeFeatures

    band_input = extrudes.createInput(band, ops.NewBodyFeatureOperation)
    band_input.setOneSideExtent(distance('frame_height'), up)
    band_feature = extrudes.add(band_input)
    band_feature.name = 'Band'
    band_feature.bodies.item(0).name = comp.name

    block_input = extrudes.createInput(collection(rings + sockets), ops.JoinFeatureOperation)
    block_input.setTwoSidesExtent(distance('frame_height'), distance('block_drop'))
    extrudes.add(block_input).name = 'End blocks'
    body = comp.bRepBodies.item(0)

    socket_input = extrudes.createInput(collection(sockets), ops.CutFeatureOperation)
    socket_input.setOneSideExtent(distance('tab_length + fit_clearance'), up)
    socket_input.startExtent = adsk.fusion.OffsetStartDefinition.create(value('-block_drop'))
    socket_input.participantBodies = [body]
    extrudes.add(socket_input).name = 'Sockets'

    recess = comp.sketches.add(comp.xZConstructionPlane)
    recess.name = 'Strap recess'
    add_band_sector(recess, r_out - p('strap_recess_depth'), r_out + 0.25 * CM_PER_IN, half,
                    f'{id_param} + 2 * frame_wall - 2 * strap_recess_depth',
                    f'{id_param} + 2 * frame_wall + 0.5 in', angle_param)
    recess_input = extrudes.createInput(recess.profiles.item(0), ops.CutFeatureOperation)
    recess_input.setOneSideExtent(distance('strap_recess_height'), up)
    recess_input.startExtent = adsk.fusion.OffsetStartDefinition.create(value('(frame_height - strap_recess_height) / 2'))
    recess_input.participantBodies = [body]
    extrudes.add(recess_input).name = 'Strap recess'

    add_socket_flares(comp, rings, sockets, body)
    add_gussets(comp, r_in, r_out)
    add_strap_bridges_and_slots(comp, outer_block_lines(rings, r_out, length), p('lip_thickness'), p('strap_recess_depth'))
    return comp.bRepBodies.item(0)


def run(_context: str) -> None:
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.InchDistanceUnits
    ensure_parameters(design)
    root = design.rootComponent

    occurrences = {}
    for name, id_param, angle_param in FRAMES:
        # Build at the identity transform; sketch-space conversions assume component space == model space.
        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occurrence.component.name = name
        body = build_frame(design, occurrence.component, id_param, angle_param)
        occurrences[name] = occurrence
        print(f'{name}: volume {body.volume / CM_PER_IN ** 3:.3f} in^3')

    flip = adsk.core.Matrix3D.create()
    flip.setToRotation(math.pi, adsk.core.Vector3D.create(1, 0, 0), adsk.core.Point3D.create(0, 0, 0))
    flip.translation = adsk.core.Vector3D.create(*(c * CM_PER_IN for c in BOTTOM_FRAME_TRANSLATION_IN))
    occurrences['Bottom Frame'].transform2 = flip
    if design.snapshots.hasPendingSnapshot:
        design.snapshots.add()
