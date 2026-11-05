"""Diagnostic clay from the accepted model/camera, without modifying its file."""
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/bishop/bishop-rebuilt.blend'),load_ui=False)
s=bpy.context.scene;mat=bpy.data.materials.new('Mission diagnostic clay');mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.28,.3,.34,1);p.inputs['Roughness'].default_value=.3
for o in s.objects:
    if o.type=='MESH' and not o.hide_render:o.data.materials.clear();o.data.materials.append(mat)
s.cycles.samples=32;s.render.filepath=str(ROOT/'assets/bishop/render-clay.png')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
