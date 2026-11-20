"""Rebuild the queen socket checkpoint from its archived mesh, atlas and lights."""
from pathlib import Path
import argparse, hashlib, json, sys, math
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from render_regions import partition, link

p=argparse.ArgumentParser()
p.add_argument('config',nargs='?',default='docs/queen-mission/iteration-014/reproduction.json')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
cfg=json.loads((ROOT/args.config).read_text())
source=ROOT/cfg['baseline']; texture=ROOT/cfg['texture']
assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['baseline_sha256']
assert hashlib.sha256(texture.read_bytes()).hexdigest()==cfg['texture_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene; obj=editable_mesh(s); settings=cfg['material_config']
for light in s.objects:
    if light.type=='LIGHT': light.light_linking.receiver_collection=None
for o in list(s.objects):
    if o.get('mission_render_region'): bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
    if c.name.startswith(('Queen render regions','Receivers ')): bpy.data.collections.remove(c)
mat=obj.data.materials[0]; ns=mat.node_tree.nodes; ls=mat.node_tree.links
im=bpy.data.images.load(str(texture),check_existing=False)
im.colorspace_settings.name='sRGB'; im.pack()
tex=ns.new('ShaderNodeTexImage'); tex.image=im
uv=ns.new('ShaderNodeUVMap'); uv.uv_map='Pigment atlas'
assert obj.data.uv_layers.get(uv.uv_map)
ls.new(uv.outputs[0],tex.inputs['Vector'])
ls.new(tex.outputs['Color'],ns.get('Principled BSDF').inputs['Base Color'])
parts,report=partition(s,obj,socket_band=True)
byname={o['mission_render_region']:o for o in parts}
for spec in settings['lights']:
    light=bpy.data.objects.get(spec['name'])
    if light is None:
        assert spec['name'].startswith('Socket crescent ') and spec['type']=='SPOT'
        data=bpy.data.lights.new(spec['name'],'SPOT')
        data.shadow_soft_size=spec['size']/2
        data.spot_size=math.radians(spec['spot_degrees']); data.spot_blend=spec['spot_blend']
        light=bpy.data.objects.new(spec['name'],data); s.collection.objects.link(light)
        light.location=spec['position']
        light.rotation_euler=(Vector(spec['target'])-light.location).to_track_quat('-Z','Y').to_euler()
        light.visible_diffuse=False; light.visible_glossy=True
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
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('SOCKET_CHECKPOINT_REBUILT',flush=True)
