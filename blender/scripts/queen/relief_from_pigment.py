"""Align micro-relief with the visible pigment; preserve geometry and lights."""
from pathlib import Path
import argparse,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);settings=json.loads(Path(args.config).read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/settings['source']),load_ui=False)
scene=bpy.context.scene;obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
nodes=obj.data.materials[0].node_tree.nodes;links=obj.data.materials[0].node_tree.links;bs=nodes.get('Principled BSDF')
# Unlit, ungraded pigment controls grain relief; regional color grades do not.
atlas=next(n for n in nodes if n.type=='TEX_IMAGE' and n.image and n.image.name.startswith('Queen pigment atlas'))
gray=nodes.new('ShaderNodeRGBToBW');links.new(atlas.outputs['Color'],gray.inputs[0])
height=nodes.new('ShaderNodeMapRange');height.clamp=False
height.inputs['From Min'].default_value=.01;height.inputs['From Max'].default_value=settings['relief_range'];links.new(gray.outputs[0],height.inputs['Value'])
coord=nodes.new('ShaderNodeTexCoord');pores=nodes.new('ShaderNodeTexNoise');pores.inputs['Scale'].default_value=settings['pore_scale'];pores.inputs['Detail'].default_value=2;pores.inputs['Roughness'].default_value=.7;links.new(coord.outputs['Object'],pores.inputs['Vector'])
mix=nodes.new('ShaderNodeMixRGB');mix.inputs[0].default_value=settings['pore_mix'];links.new(height.outputs[0],mix.inputs[1]);links.new(pores.outputs['Fac'],mix.inputs[2])
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=settings['strength'];bump.inputs['Distance'].default_value=settings['distance'];links.new(mix.outputs[0],bump.inputs['Height'])
links.new(bump.outputs['Normal'],bs.inputs['Normal']);links.new(bump.outputs['Normal'],bs.inputs['Coat Normal'])
for link in list(bs.inputs['Roughness'].links):links.remove(link)
bs.inputs['Roughness'].default_value=settings['roughness'];bs.inputs['Coat Roughness'].default_value=settings['coat_roughness'];bs.inputs['Coat Weight'].default_value=settings['coat']
if settings.get('anisotropy'):
 tangent=nodes.new('ShaderNodeTangent');tangent.direction_type='UV_MAP';tangent.uv_map='Pigment atlas';links.new(tangent.outputs[0],bs.inputs['Tangent'])
 geom=nodes.new('ShaderNodeNewGeometry');pos=nodes.new('ShaderNodeSeparateXYZ');links.new(geom.outputs['Position'],pos.inputs[0])
 anis=nodes.new('ShaderNodeMapRange');anis.inputs['From Min'].default_value=3.8;anis.inputs['From Max'].default_value=4.02;anis.inputs['To Min'].default_value=settings['anisotropy'];anis.inputs['To Max'].default_value=0;links.new(pos.outputs['Z'],anis.inputs['Value']);links.new(anis.outputs[0],bs.inputs['Anisotropic'])
cfg=json.loads(scene['mission_material_config']);cfg['variant']=settings['variant'];cfg['relief_from_pigment']=settings;scene['mission_material_config']=json.dumps(cfg,sort_keys=True)
out=ROOT/'build/queen-mission'/settings['variant'];out.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(out/'wood.png');scene.cycles.samples=64;scene.cycles.use_denoising=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
except Exception as exc:print('CPU fallback',exc)
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');print('PIGMENT_RELIEF_DONE',flush=True)
