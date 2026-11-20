"""Test opposite-color slit orientation without changing the accepted scene.

Rotate the evaluated geometry only for first-hit diagnostics. The saved
camera, source image alignment, model, material and standard view stay exact.
An original black image need not expose the same face of a through slit.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source', default='models/bishop/bishop-rebuilt.blend')
p.add_argument('--out', default='build/bishop-mission/166-opposite-pose')
p.add_argument('--angles', nargs='+', type=float, default=list(range(0, 360, 45)))
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
source, out = ROOT / a.source, ROOT / a.out
out.mkdir(parents=True, exist_ok=True)
digest = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
scene = bpy.context.scene
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
vertices, triangles, labels = [], [], []
for name in ['Bishop - continuous turned body', 'Bishop - domed button finial']:
    ob = bpy.data.objects[name].evaluated_get(deps)
    mesh = ob.to_mesh()
    mesh.calc_loop_triangles()
    offset = len(vertices)
    vertices.extend(ob.matrix_world @ v.co for v in mesh.vertices)
    for tri in mesh.loop_triangles:
        triangles.append(tuple(offset + i for i in tri.vertices))
        labels.append(3 if 'finial' in name else 2 if mesh.polygons[tri.polygon_index].material_index == 1 else 1)
    ob.to_mesh_clear()
camera = scene.camera
assert camera.data.type == 'ORTHO'
direction = camera.matrix_world.to_3x3() @ Vector((0, 0, -1))
assert abs(math.degrees(math.asin(-direction.normalized().z)) - 54) < 1e-4
projection = camera.calc_matrix_camera(deps, x=1254, y=1254)
inverse = (projection @ camera.matrix_world.inverted()).inverted()
border = [320, 200, 675, 500]
x0, y0, x1, y1 = border
rays = []
for y in range(y0, y1):
    for x in range(x0, x1):
        p0 = inverse @ Vector((2 * (x + .5) / 1254 - 1, 1 - 2 * (y + .5) / 1254, -1, 1))
        p1 = inverse @ Vector((2 * (x + .5) / 1254 - 1, 1 - 2 * (y + .5) / 1254, 1, 1))
        start, end = p0.xyz / p0.w, p1.xyz / p1.w
        rays.append((start, (end - start).normalized()))
captures = {}
for angle in a.angles:
    rotation = Matrix.Rotation(math.radians(angle), 3, 'Z')
    bvh = BVHTree.FromPolygons([rotation @ v for v in vertices], triangles, all_triangles=True)
    mask = np.zeros((y1 - y0, x1 - x0), dtype=np.uint8)
    for i, (start, ray) in enumerate(rays):
        hit, normal, index, distance = bvh.ray_cast(start, ray)
        if index is not None:
            mask.flat[i] = labels[index]
    captures[str(angle)] = mask
    print('OPPOSITE_POSE_CAPTURED', angle, int((mask == 2).sum()), flush=True)
np.savez_compressed(out / 'surface-labels.npz', **captures)
report = {
    'source': a.source, 'source_sha256': digest, 'angles_degrees': a.angles,
    'border': border, 'camera_degrees': 54,
    'method': 'Unsaved world-Z rotation of evaluated body/button triangles, then first-hit labels at the exact standard camera. No pigment, lighting, alignment change, or image fitting.',
    'source_unchanged': hashlib.sha256(source.read_bytes()).hexdigest() == digest,
    'note': 'These rotations are diagnostic only, not alternative public models or evidence of recovered historical camera metadata.'
}
assert report['source_unchanged']
(out / 'capture.json').write_text(json.dumps(report, indent=2) + '\n')
