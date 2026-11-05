"""Rebuild checkpoint 13 from tracked baseline, four ring radii, atlas and one light."""
from pathlib import Path
import argparse, hashlib, json, sys
import bpy
import numpy as np
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from render_regions import partition, link
from validate_base_transition import check as check_transition

p=argparse.ArgumentParser()
p.add_argument('config',nargs='?',default='docs/queen-mission/iteration-013/reproduction.json')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
cfg=json.loads((ROOT/args.config).read_text())
source=ROOT/cfg['baseline']; texture=ROOT/cfg['texture']
assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['baseline_sha256']
assert hashlib.sha256(texture.read_bytes()).hexdigest()==cfg['texture_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene; obj=editable_mesh(s); settings=cfg['material_config']
controls=np.empty(len(obj.data.vertices)*3,dtype=np.float32)
obj.data.vertices.foreach_get('co',controls); controls=controls.reshape(-1,192,3)
radii=np.linalg.norm(controls[:,:,:2],axis=2).mean(1)
for entry in settings['base_transition_refinement']['rings']:
    i=entry['ring']; controls[i,:,:2]*=entry['new_radius']/radii[i]
assert check_transition(controls,settings)
obj.data.vertices.foreach_set('co',controls.reshape(-1)); obj.data.update()
mat=obj.data.materials[0]; ns=mat.node_tree.nodes; ls=mat.node_tree.links
im=bpy.data.images.load(str(texture),check_existing=False)
im.colorspace_settings.name='sRGB'; im.pack()
tex=ns.new('ShaderNodeTexImage'); tex.image=im
uv=ns.new('ShaderNodeUVMap'); uv.uv_map='Pigment atlas'
assert obj.data.uv_layers.get(uv.uv_map)
ls.new(uv.outputs[0],tex.inputs['Vector'])
ls.new(tex.outputs['Color'],ns.get('Principled BSDF').inputs['Base Color'])
# Derived receivers are rebuilt from the changed, closed control.
for o in s.objects:
    if o.type=='LIGHT': o.light_linking.receiver_collection=None
for o in list(s.objects):
    if o.get('mission_render_region'): bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
    if c.name.startswith(('Queen render regions','Receivers ')): bpy.data.collections.remove(c)
bpy.context.view_layer.update()
parts,report=partition(s,obj,finial_only=True)
body=next(o for o in parts if o['mission_render_region']=='turned-body')
for spec in settings['lights']:
    if spec.get('diffuse_factor',1)==0 and not ('finial-' in spec['name'] and spec['name'].endswith('-spot')):
        link(bpy.data.objects[spec['name']],[body],'turned-body')
for part in parts: part.hide_set(True)
spec=next(a for a in settings['lights'] if a['name']=='Display fitted base-key')
light=bpy.data.objects[spec['name']]; light.location=spec['position']
light.rotation_euler=(Vector(spec['target'])-light.location).to_track_quat('-Z','Y').to_euler()
light.data.size=spec['size']; light.data.size_y=spec['size_y']
light.data.color=spec['color']; light.data.energy=spec['energy']
settings['finial_receiver_isolation']['render_regions']=report
settings['variant']=cfg['variant']; s['mission_variant']=cfg['variant']
s['mission_material_config']=json.dumps(settings,sort_keys=True)
s.cycles.samples=64; s.cycles.use_denoising=True; s.render.use_persistent_data=True
out=ROOT/'build/queen-mission'/cfg['variant']; out.mkdir(parents=True,exist_ok=True)
s.render.filepath=str(out/'wood.png'); bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences; prefs.compute_device_type='OPTIX'; prefs.get_devices()
for d in prefs.devices: d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices): s.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('BASE_CHECKPOINT_REBUILT',flush=True)
