"""Rebuild a finial material/reflector checkpoint from an archived model and UV atlas."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from render_regions import link
from polish_finial import apply_finial_polish

p=argparse.ArgumentParser();p.add_argument('config');p.add_argument('--variant')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);config=json.loads((ROOT/a.config).read_text())
source=ROOT/config['baseline'];texture=ROOT/config['texture']
assert hashlib.sha256(source.read_bytes()).hexdigest()==config['baseline_sha256']
assert hashlib.sha256(texture.read_bytes()).hexdigest()==config['texture_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;obj=editable_mesh(s)
settings=config['material_config'];variant=a.variant or config['variant']
nodes=obj.data.materials[0].node_tree.nodes;links=obj.data.materials[0].node_tree.links
image=bpy.data.images.load(str(texture),check_existing=False);image.colorspace_settings.name='sRGB';image.pack()
node=nodes.new('ShaderNodeTexImage');node.image=image;node.label='UV pigment atlas, local finial repair only'
uv=nodes.new('ShaderNodeUVMap');uv.uv_map='Pigment atlas';assert obj.data.uv_layers.get(uv.uv_map)
links.new(uv.outputs['UV'],node.inputs['Vector']);links.new(node.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
polish=apply_finial_polish(s,settings['finial_polish']['factor'])
assert abs(polish['finial_distance']-settings['finial_polish']['finial_distance'])<1e-9
settings['finial_polish'].update(polish)
settings['finial_polish'].pop('world_z_transition',None);settings['finial_polish'].pop('world_radius_max',None)
regions={o['mission_render_region']:o for o in s.objects if o.get('mission_render_region')}
new_names=[];updated_names=[]
for spec in settings['lights']:
    name=spec['name'];is_finial='finial-' in name and name.endswith('-spot');retained=name.startswith('Finial retained ')
    if not (is_finial or retained):continue
    light=bpy.data.objects.get(name)
    if retained:
        assert light is None
        original=bpy.data.objects[spec['clone_of']]
        light=original.copy();light.data=original.data.copy();light.name=name;s.collection.objects.link(light);new_names.append(name)
    else:updated_names.append(name)
    light.location=spec['position'];light.rotation_euler=(Vector(spec['target'])-light.location).to_track_quat('-Z','Y').to_euler()
    if 'rotation_euler' in spec:light.rotation_euler=spec['rotation_euler']
    light.data.energy=spec['energy'];light.data.color=spec['color'];light.data.shadow_soft_size=spec['shadow_soft_size']
    light.data.spot_size=math.radians(spec['spot_degrees']);light.data.spot_blend=spec['spot_blend']
    light.visible_diffuse=False;light.visible_glossy=True
    link(light,[regions[n] for n in spec['receiver_parts']],'+'.join(spec['receiver_parts']))
assert len(new_names)==3 and len(updated_names)==3
settings.update(variant=variant,texture=config['texture'],texture_sha256=config['texture_sha256'],atlas_bakes_lighting=False,atlas_reused_uv=True)
s['mission_material_config']=json.dumps(settings,sort_keys=True);s['mission_variant']=variant
out=ROOT/'build/queen-mission'/variant;out.mkdir(exist_ok=True,parents=True)
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8'
sampling=settings.get('render_sampling',{'samples':64,'adaptive':True})
s.cycles.samples=sampling['samples'];s.cycles.use_adaptive_sampling=sampling['adaptive'];s.cycles.use_denoising=True;s.render.filepath=str(out/'wood.png')
if 'light_tree' in sampling:s.cycles.use_light_tree=sampling['light_tree']
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'queen.blend'),load_ui=False)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):bpy.context.scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(settings,indent=2)+'\n')
assert hashlib.sha256(source.read_bytes()).hexdigest()==config['baseline_sha256']
print('FINIAL_CHECKPOINT_REBUILT',variant,flush=True)
