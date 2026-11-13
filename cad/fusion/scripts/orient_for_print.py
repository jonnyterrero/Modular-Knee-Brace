"""Turns the exported STLs into a print package: each part on its print face, at Z = 0, centred on the bed.

The Fusion export writes parts in model coordinates, which leaves the hinges on edge and the frames in their
tallest orientation if a slicer takes them as-is. This script needs only Python, not Fusion. It also checks every
mesh is closed and outward-facing, and reports height and layer counts.

Usage: python cad/fusion/scripts/orient_for_print.py
"""

import math
import os
import struct
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
SOURCE_DIR = os.path.join(REPO, 'cad', 'fusion', 'stl')
OUTPUT_DIR = os.path.join(REPO, 'cad', 'fusion', 'print')

# Rows of a proper rotation (determinant +1, so left and right parts keep their handedness).
# Each maps the part's chosen "up" axis in model coordinates onto +Z.
UP_PLUS_X = ((0, 1, 0), (0, 0, 1), (1, 0, 0))
UP_MINUS_X = ((0, 0, 1), (0, 1, 0), (-1, 0, 0))
UP_MINUS_Y = ((1, 0, 0), (0, 0, 1), (0, -1, 0))
UP_PLUS_Z = ((1, 0, 0), (0, 1, 0), (0, 0, 1))

# file stem -> (rotation, quantity, face on the bed)
PARTS = {
    'top-frame': (UP_MINUS_Y, 1, 'band end down, socket mouths up'),
    'bottom-frame': (UP_MINUS_Y, 1, 'band end down, socket mouths up'),
    'right-inner-hinge': (UP_PLUS_X, 1, 'base face down, snap post up'),
    'left-inner-hinge': (UP_MINUS_X, 1, 'base face down, snap post up'),
    'outer-hinge': (UP_MINUS_X, 2, 'cap face down'),
    'upper-connector': (UP_PLUS_Z, 2, 'on edge, flat profile face down'),
    'lower-connector': (UP_PLUS_Z, 2, 'on edge, flat profile face down'),
}
LAYER_HEIGHTS_MM = (0.2, 0.3)


def read_binary_stl(path):
    with open(path, 'rb') as handle:
        data = handle.read()
    count = struct.unpack_from('<I', data, 80)[0]
    if len(data) != 84 + 50 * count:
        raise ValueError(f'{path}: not a binary STL of {count} triangles')
    triangles = []
    for i in range(count):
        values = struct.unpack_from('<12f', data, 84 + 50 * i)
        triangles.append((values[3:6], values[6:9], values[9:12]))
    return triangles


def write_binary_stl(path, triangles, name):
    with open(path, 'wb') as handle:
        handle.write(name.encode('ascii')[:80].ljust(80, b' '))
        handle.write(struct.pack('<I', len(triangles)))
        for a, b, c in triangles:
            u = [b[k] - a[k] for k in range(3)]
            v = [c[k] - a[k] for k in range(3)]
            n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
            length = math.sqrt(sum(x * x for x in n)) or 1.0
            handle.write(struct.pack('<12fH', *(x / length for x in n), *a, *b, *c, 0))


def rotate(triangles, rows):
    def apply(p):
        return tuple(sum(rows[r][k] * p[k] for k in range(3)) for r in range(3))
    return [tuple(apply(p) for p in tri) for tri in triangles]


def place_on_bed(triangles):
    points = [p for tri in triangles for p in tri]
    low = [min(p[k] for p in points) for k in range(3)]
    high = [max(p[k] for p in points) for k in range(3)]
    shift = ((low[0] + high[0]) / 2, (low[1] + high[1]) / 2, low[2])
    moved = [tuple(tuple(p[k] - shift[k] for k in range(3)) for p in tri) for tri in triangles]
    return moved, [high[k] - low[k] for k in range(3)]


def mesh_problems(triangles):
    """Closed, consistently wound, outward-facing: every edge used once in each direction, positive volume."""
    def key(p):
        return tuple(round(x, 4) for x in p)

    edges = {}
    degenerate = 0
    volume = 0.0
    for a, b, c in triangles:
        ka, kb, kc = key(a), key(b), key(c)
        if len({ka, kb, kc}) < 3:
            degenerate += 1
            continue
        for e in ((ka, kb), (kb, kc), (kc, ka)):
            edges[e] = edges.get(e, 0) + 1
        volume += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                   + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    unmatched = sum(1 for (p, q), n in edges.items() if n != 1 or edges.get((q, p), 0) != 1)
    problems = []
    if unmatched:
        problems.append(f'{unmatched} open or non-manifold edges')
    if degenerate:
        problems.append(f'{degenerate} degenerate triangles')
    if volume <= 0:
        problems.append('inward-facing (negative volume)')
    return problems, volume


def main() -> int:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    failed = False
    print(f'{"part":<20}{"qty":>4}{"X":>8}{"Y":>8}{"Z mm":>8}' + ''.join(f'{"L@" + str(h):>8}' for h in LAYER_HEIGHTS_MM)
          + '  volume cm3  check')
    for stem, (rows, quantity, face) in PARTS.items():
        triangles = read_binary_stl(os.path.join(SOURCE_DIR, stem + '.stl'))
        placed, size = place_on_bed(rotate(triangles, rows))
        problems, volume = mesh_problems(placed)
        failed |= bool(problems)
        write_binary_stl(os.path.join(OUTPUT_DIR, stem + '.stl'), placed, f'MK-Brace {stem}, print-oriented, mm')
        layers = ''.join(f'{math.ceil(size[2] / h):>8}' for h in LAYER_HEIGHTS_MM)
        print(f'{stem:<20}{quantity:>4}{size[0]:>8.1f}{size[1]:>8.1f}{size[2]:>8.1f}{layers}  {volume / 1000:>9.1f}  '
              + ('; '.join(problems) if problems else 'ok') + f'  ({face})')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
