"""Rebuild the queen collar checkpoint from its archived mesh, atlas and lights."""
from pathlib import Path
import argparse, hashlib, json, sys, math
import bpy
import numpy as np
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from render_regions import partition, link

p=argparse.ArgumentParser()
p.add_argument('config',nargs='?',default='docs/queen-mission/iteration-015/reproduction.json')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
cfg=json.loads((ROOT/args.config).read_text())
source=ROOT/cfg['baseline']
assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['baseline_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene; obj=editable_mesh(s); settings=cfg['material_config']
if settings.get('middle_collar_edge_refinement'):
    assert cfg['baseline_sha256']==settings['middle_collar_edge_refinement']['source_sha256']
    controls=np.empty(len(obj.data.vertices)*3,dtype=np.float32)
    obj.data.vertices.foreach_get('co',controls);controls=controls.reshape(-1,192,3)
    for edit in settings['middle_collar_edge_refinement']['rings']:
        i=edit['ring'];oldr=np.linalg.norm(controls[i,:,:2],axis=1)
        controls[i,:,:2]*=(edit['new_radius']/oldr)[:,None]
    from validate_middle_collar_edge import check as check_middle_edge
    check_middle_edge(controls,settings)
    obj.data.vertices.foreach_set('co',controls.reshape(-1));obj.data.update()
    bpy.context.view_layer.update()
for light in s.objects:
    if light.type=='LIGHT': light.light_linking.receiver_collection=None
for o in list(s.objects):
    if o.get('mission_render_region'): bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
    if c.name.startswith(('Queen render regions','Receivers ')): bpy.data.collections.remove(c)
parts,report=partition(s,obj,socket_band=True,collar_band=True,split_collars=bool(settings.get('subdivided_collar_receivers')))
byname={o['mission_render_region']:o for o in parts}
for spec in settings['lights']:
    light=bpy.data.objects.get(spec['name'])
    if light is None:
        if spec.get('clone_of'):
            original=bpy.data.objects[spec['clone_of']]; light=original.copy();light.data=original.data.copy()
            light.name=spec['name'];s.collection.objects.link(light)
        else:
            assert spec['name'].startswith('Collar crescent ') and spec['type']=='SPOT'
            data=bpy.data.lights.new(spec['name'],'SPOT')
            data.shadow_soft_size=spec['size']/2
            data.spot_size=math.radians(spec['spot_degrees']); data.spot_blend=spec['spot_blend']
            light=bpy.data.objects.new(spec['name'],data); s.collection.objects.link(light)
            light.location=spec['position']
            light.rotation_euler=(Vector(spec['target'])-light.location).to_track_quat('-Z','Y').to_euler()
            light.visible_diffuse=False; light.visible_glossy=True
    if spec.get('surface_pixel'):
        light.location=spec['position']
        light.rotation_euler=(Vector(spec['target'])-light.location).to_track_quat('-Z','Y').to_euler()
    if 'use_shadow' in spec: light.data.use_shadow=spec['use_shadow']
    light.data.energy=spec['energy']
    if 'color' in spec: light.data.color=spec['color']
    if spec.get('diffuse_factor',1)==0 and not ('finial-' in spec['name'] and spec['name'].endswith('-spot')):
        names=spec['receiver_parts'];link(light,[byname[n] for n in names],'+'.join(names))
for part in parts: part.hide_set(True)
for modifier in obj.modifiers:
    if modifier.type=='SUBSURF': modifier.levels=modifier.render_levels
settings['finial_receiver_isolation']['render_regions']=report
settings['variant']=cfg['variant'];s['mission_variant']=cfg['variant']
s['mission_material_config']=json.dumps(settings,sort_keys=True)
s.cycles.samples=64;s.cycles.use_denoising=True;s.render.use_persistent_data=True
if settings.get('glossy_interreflection'):s.cycles.glossy_bounces=settings['glossy_interreflection']['glossy_bounces']
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('COLLAR_CHECKPOINT_REBUILT',flush=True)
