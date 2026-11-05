"""Keep the baked pigment and geometry; adjust physically rendered polish/lights."""
from pathlib import Path
import argparse,json,sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(Path(args.config).read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/cfg['source']),load_ui=False)
scene=bpy.context.scene;obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
nodes=obj.data.materials[0].node_tree.nodes;links=obj.data.materials[0].node_tree.links;bs=nodes.get('Principled BSDF')
tex=bs.inputs['Base Color'].links[0].from_socket
gray=nodes.new('ShaderNodeRGBToBW');links.new(tex,gray.inputs[0])
rough=nodes.new('ShaderNodeMapRange');rough.inputs['From Min'].default_value=.02;rough.inputs['From Max'].default_value=.24
rough.inputs['To Min'].default_value=cfg['rough_dark'];rough.inputs['To Max'].default_value=cfg['rough_light'];links.new(gray.outputs[0],rough.inputs['Value']);links.new(rough.outputs[0],bs.inputs['Roughness'])
bs.inputs['Coat Weight'].default_value=cfg['coat'];bs.inputs['Coat Roughness'].default_value=cfg['coat_roughness']
if cfg.get('surface_polish'):
    geom=nodes.new('ShaderNodeNewGeometry');normal=nodes.new('ShaderNodeSeparateXYZ');links.new(geom.outputs['True Normal'],normal.inputs[0])
    vertical=nodes.new('ShaderNodeMath');vertical.operation='ABSOLUTE';links.new(normal.outputs['Z'],vertical.inputs[0])
    position=nodes.new('ShaderNodeSeparateXYZ');links.new(geom.outputs['Position'],position.inputs[0])
    head=nodes.new('ShaderNodeMapRange');head.inputs['From Min'].default_value=3.95;head.inputs['From Max'].default_value=4.08;links.new(position.outputs['Z'],head.inputs['Value'])
    for socket,low,high,head_value in [('Roughness',.38,.13,.13),('Coat Roughness',.28,.07,.07)]:
        polish=nodes.new('ShaderNodeMapRange');polish.inputs['From Min'].default_value=.1;polish.inputs['From Max'].default_value=.8
        polish.inputs['To Min'].default_value=low;polish.inputs['To Max'].default_value=high;links.new(vertical.outputs[0],polish.inputs['Value'])
        blend=nodes.new('ShaderNodeMixRGB');links.new(head.outputs[0],blend.inputs[0]);links.new(polish.outputs[0],blend.inputs[1]);blend.inputs[2].default_value=(head_value,head_value,head_value,1)
        links.new(blend.outputs[0],bs.inputs[socket])
bump=next(n for n in nodes if n.type=='BUMP');bump.inputs['Strength'].default_value=cfg['bump_strength'];bump.inputs['Distance'].default_value=cfg['bump_distance']
mix=nodes.new('ShaderNodeMixRGB');mix.inputs[0].default_value=cfg['pore_mix'];links.new(gray.outputs[0],mix.inputs[1])
pores=next(n for n in nodes if n.type=='TEX_NOISE' and abs(n.inputs['Scale'].default_value-180)<.1)
links.new(pores.outputs['Fac'],mix.inputs[2]);links.new(mix.outputs[0],bump.inputs['Height']);links.new(bump.outputs[0],bs.inputs['Coat Normal'])
for light in list(scene.objects):
    if light.type=='LIGHT':bpy.data.objects.remove(light,do_unlink=True)
for spec in cfg['lights']:
    data=bpy.data.lights.new(spec['name'],'AREA');data.energy=spec['energy'];data.shape=spec.get('shape','DISK');data.size=spec['size']
    data.diffuse_factor=spec.get('diffuse_factor',1);data.specular_factor=spec.get('specular_factor',1)
    if data.shape=='RECTANGLE':data.size_y=spec['size_y']
    light=bpy.data.objects.new(spec['name'],data);scene.collection.objects.link(light);light.location=spec['position']
    light.rotation_euler=(Vector(spec.get('target',[0,0,2.3]))-light.location).to_track_quat('-Z','Y').to_euler()
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=cfg['world']
material=json.loads(scene['mission_material_config']);material.update(cfg);scene['mission_material_config']=json.dumps(material,sort_keys=True)
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
scene.render.filepath=str(out/'wood.png');scene.cycles.samples=64;scene.cycles.use_denoising=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
except Exception as exc:print('CPU fallback',exc)
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(material,indent=2)+'\n');print('ATLAS_LIGHTING_DONE',cfg['variant'],flush=True)
