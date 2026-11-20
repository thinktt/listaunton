"""Align relief with v3 pigment while keeping geometry, color and rig fixed."""
from pathlib import Path
import argparse,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',default='models/queen/queen-rebuilt.blend');p.add_argument('--variant',default='062-atlas-relief');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(ROOT/args.source),load_ui=False)
s=bpy.context.scene;o=next(o for o in s.objects if o.type=='MESH' and not o.hide_render);n=o.data.materials[0].node_tree.nodes;l=o.data.materials[0].node_tree.links;b=n.get('Principled BSDF')
directory=ROOT/'build/queen-mission/atlas-relief-v3'
im=bpy.data.images.load(str(directory/'height.png'),check_existing=False);im.colorspace_settings.name='Non-Color';im.pack()
tex=n.new('ShaderNodeTexImage');tex.image=im;uv=n.new('ShaderNodeUVMap');uv.uv_map='Pigment atlas';l.new(uv.outputs[0],tex.inputs['Vector'])
coord=n.new('ShaderNodeTexCoord');pore=n.new('ShaderNodeTexNoise');pore.inputs['Scale'].default_value=180;pore.inputs['Detail'].default_value=2;pore.inputs['Roughness'].default_value=.7;l.new(coord.outputs['Object'],pore.inputs['Vector'])
mix=n.new('ShaderNodeMixRGB');mix.inputs[0].default_value=.15;l.new(tex.outputs['Color'],mix.inputs[1]);l.new(pore.outputs['Fac'],mix.inputs[2])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.35;bump.inputs['Distance'].default_value=.006;l.new(mix.outputs[0],bump.inputs['Height']);l.new(bump.outputs['Normal'],b.inputs['Normal']);l.new(bump.outputs['Normal'],b.inputs['Coat Normal'])
cfg=json.loads(s['mission_material_config']);cfg['variant']=args.variant;cfg['v3_relief']={'source':args.source,'derivation':json.loads((directory/'derivation.json').read_text()),'strength':.35,'distance':.006,'pore_scale':180,'pore_mix':.15};s['mission_material_config']=json.dumps(cfg,sort_keys=True)
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png');s.cycles.samples=64;s.cycles.use_denoising=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');print('ATLAS_RELIEF_TRIAL_DONE',flush=True)
