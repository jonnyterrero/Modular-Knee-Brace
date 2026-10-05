"""Prints the measurable geometry of every body in the active design: size, volume, cylinder diameters and planar face offsets."""

import adsk.core
import adsk.fusion

CM_PER_IN = 2.54
SURFACE_NAMES = {0: 'plane', 1: 'cylinder', 2: 'cone', 3: 'sphere', 4: 'torus', 7: 'nurbs'}


def inches(point: adsk.core.Point3D) -> list:
    return [round(c / CM_PER_IN, 4) for c in point.asArray()]


def describe(body: adsk.fusion.BRepBody) -> list:
    box = body.boundingBox
    low, high = inches(box.minPoint), inches(box.maxPoint)
    lines = [f'{body.parentComponent.name} / {body.name}: volume {body.volume / CM_PER_IN ** 3:.4f} in^3, '
             f'size {[round(h - l, 4) for l, h in zip(low, high)]} in, box {low} .. {high}']

    counts, cylinders, planes = {}, {}, {}
    for face in body.faces:
        surface = face.geometry
        kind = surface.surfaceType
        counts[SURFACE_NAMES.get(kind, kind)] = counts.get(SURFACE_NAMES.get(kind, kind), 0) + 1
        if kind == adsk.core.SurfaceTypes.CylinderSurfaceType:
            axis = surface.axis
            key = (round(2 * surface.radius / CM_PER_IN, 4), tuple(round(abs(c), 3) for c in (axis.x, axis.y, axis.z)))
            cylinders[key] = cylinders.get(key, 0) + 1
        elif kind == adsk.core.SurfaceTypes.PlaneSurfaceType:
            normal = surface.normal
            components = (normal.x, normal.y, normal.z)
            dominant = max(range(3), key=lambda i: abs(components[i]))
            sign = 1 if components[dominant] > 0 else -1
            direction = tuple(round(sign * c, 3) for c in components)
            origin = surface.origin
            offset = sign * (origin.x * normal.x + origin.y * normal.y + origin.z * normal.z) / CM_PER_IN
            planes.setdefault(direction, set()).add(round(offset, 4))

    lines.append(f'  faces: {counts}')
    for (diameter, axis), count in sorted(cylinders.items()):
        lines.append(f'  cylinder d={diameter} in, axis {axis} x{count}')
    for direction, offsets in sorted(planes.items(), key=lambda item: -len(item[1])):
        lines.append(f'  planes normal {direction} at {sorted(offsets)} in')
    return lines


def run(_context: str) -> None:
    design = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    for component in design.allComponents:
        for body in component.bRepBodies:
            print('\n'.join(describe(body)))
