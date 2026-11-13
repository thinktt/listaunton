"""Locate actual surfaces that generate the saved-camera exterior contour.

Binary first-hit ray searches, rather than shaded pixels or control-ring
labels, distinguish a visible stem boundary from the rear base behind it.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source', default='models/bishop/bishop-rebuilt.blend')
p.add_argument('--profile', default='scripts/bishop/profile.json')
p.add_argument('--out', default='build/bishop-mission/178-contour-audit/meridians.json')
p.add_argument('--rows', nargs=3, type=int, default=[590, 820, 2])
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
source = ROOT / a.source
digest = hashlib.sha256(source.read_bytes()).hexdigest()
cfg = json.loads((ROOT / a.profile).read_text())
al = json.loads((ROOT / 'assets/bishop/original-alignment.json').read_text())
factor = 1254 / 300 / al['scale'] / cfg['scale']
co = math.cos(math.radians(54))
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
scene = bpy.context.scene
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
vertices, triangles, labels = [], [], []
for name in ['Bishop - continuous turned body', 'Bishop - domed button finial']:
    ob = bpy.data.objects[name].evaluated_get(deps)
    mesh = ob.to_mesh(); mesh.calc_loop_triangles()
    offset = len(vertices)
    vertices += [ob.matrix_world @ v.co for v in mesh.vertices]
    for tri in mesh.loop_triangles:
        triangles.append(tuple(offset + i for i in tri.vertices))
        labels.append(name)
    ob.to_mesh_clear()
bvh = BVHTree.FromPolygons(vertices, triangles, all_triangles=True)
w, h = scene.render.resolution_x, scene.render.resolution_y
camera = scene.camera
projection = camera.calc_matrix_camera(deps, x=w, y=h,
    scale_x=scene.render.pixel_aspect_x, scale_y=scene.render.pixel_aspect_y)
direction = camera.matrix_world.to_3x3() @ Vector((0, 0, -1))
elevation = math.degrees(math.asin(-direction.normalized().z))
assert camera.data.type == 'ORTHO' and abs(elevation - 54) < 1e-4
inverse = (projection @ camera.matrix_world.inverted()).inverted()
center = (cfg['cx'] - al['x'] * 3) * (1254 / 300 / al['scale'])
def ray(x, y):
    nx, ny = 2 * x / w - 1, 1 - 2 * y / h
    p0, p1 = inverse @ Vector((nx, ny, -1, 1)), inverse @ Vector((nx, ny, 1, 1))
    start, end = p0.xyz / p0.w, p1.xyz / p1.w
    return bvh.ray_cast(start, (end - start).normalized())
rows = []
for pixel_y in range(*a.rows):
    y = pixel_y + .5
    assert ray(center, y)[2] is not None
    record = {'pixel_y': y, 'sides': {}}
    for side, sign, distance in [('left', -1, center), ('right', 1, w - center)]:
        inside, outside = 0., float(distance)
        for _ in range(22):
            mid = (inside + outside) / 2
            if ray(center + sign * mid, y)[2] is None: outside = mid
            else: inside = mid
        edge = center + sign * (inside + outside) / 2
        # Slightly inside the boundary gives a stable triangle hit at tangency.
        hit, normal, index, depth = ray(center + sign * (inside - .025), y)
        assert hit is not None
        axis_y = cfg['y0'] - hit.z * co / factor
        radius = math.hypot(hit.x, hit.y) / factor
        region = ('foot' if axis_y >= 198 else 'base' if axis_y >= 174.5 else
                  'socket' if axis_y >= 162.5 else 'stem' if axis_y >= 114 else 'collars')
        record['sides'][side] = {'pixel_x': edge, 'world': list(hit),
            'profile_radius': radius, 'profile_axis_y': axis_y,
            'azimuth_degrees': math.degrees(math.atan2(hit.y, hit.x)),
            'normal_dot_view': abs(float(normal.dot(direction.normalized()))),
            'object': labels[index], 'region': region}
    rows.append(record)
report = {'source': a.source, 'source_sha256': digest, 'profile': a.profile,
    'camera_degrees_measured': elevation, 'camera_matrix': [list(r) for r in camera.matrix_world],
    'ortho_scale': camera.data.ortho_scale, 'axis_pixel_x': center,
    'rows': rows, 'source_unchanged': hashlib.sha256(source.read_bytes()).hexdigest() == digest,
    'method': '22-step binary first-hit ray search against evaluated closed body and button. Exact saved orthographic camera, stable surface probe 0.025 pixels inside each boundary.',
    'limitation': 'Labels describe the current reconstructed surface. Source-image contour provenance still requires comparison; shaded reference bands do not identify geometry by themselves.'}
assert report['source_unchanged']
out = ROOT / a.out; out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2) + '\n')
transitions = []
last = None
for row in rows:
    region = row['sides']['right']['region']
    if region != last:
        transitions.append({'row': row['pixel_y'], 'region': region,
                            'axis_y': row['sides']['right']['profile_axis_y']})
        last = region
print(json.dumps({'captured': len(rows), 'source_unchanged': True, 'transitions': transitions}, indent=2))
