"""Measure the actual socket-top meridian, independently of lights or pigment."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import bpy
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source', required=True)
p.add_argument('--profile', required=True)
p.add_argument('--out', required=True)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
source = ROOT / a.source
digest = hashlib.sha256(source.read_bytes()).hexdigest()
cfg = json.loads((ROOT / a.profile).read_text())
align = json.loads((ROOT / 'assets/bishop/original-alignment.json').read_text())
factor = 1254 / 300 / align['scale'] / cfg['scale']
co = math.cos(math.radians(54))
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
scene = bpy.context.scene
bpy.context.view_layer.update()
body = bpy.data.objects['Bishop - continuous turned body'].evaluated_get(bpy.context.evaluated_depsgraph_get())
inverse = body.matrix_world.inverted()
rows = []
for radius in np.linspace(24.8, 30.3, 221):
    start = inverse @ Vector((0, -float(radius) * factor, (cfg['y0'] - 148) * factor / co))
    direction = inverse.to_3x3() @ Vector((0, 0, -1))
    hit, point, normal, face = body.ray_cast(start, direction.normalized())
    assert hit
    world = body.matrix_world @ point
    axis_y = cfg['y0'] - world.z * co / factor
    assert 155 < axis_y < 170, (radius, axis_y)
    ndc = world_to_camera_view(scene, scene.camera, world)
    rows.append({'radius': float(radius), 'axis_y': axis_y,
                 'pixel': [float(ndc.x * 1254), float((1 - ndc.y) * 1254)]})
ys = np.array([r['axis_y'] for r in rows])
# Outward travel should descend from the stem into a simple rolled socket.
# A positive reversal here means an inner trough followed by an outward rise.
reversal = np.maximum.accumulate(ys) - ys
peak = int(np.argmax(reversal))
trough = int(np.argmax(ys[:peak + 1]))
report = {
    'source': a.source, 'source_sha256': digest, 'profile': a.profile,
    'method': 'Vertical first-hit rays on the evaluated front meridian below the collars; saved orthographic 54-degree camera. No shader, image edge, or silhouette fitting.',
    'rows': rows,
    'maximum_outward_height_reversal_original_axis_units': float(reversal[peak]),
    'reversal_trough': rows[trough], 'reversal_outer_high_point': rows[peak],
    'source_unchanged': hashlib.sha256(source.read_bytes()).hexdigest() == digest,
    'caution': 'A height reversal is a measured shape feature, not proof by itself that the photo requires or excludes a recess.'
}
assert report['source_unchanged']
out = ROOT / a.out
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'rows'}, indent=2))
