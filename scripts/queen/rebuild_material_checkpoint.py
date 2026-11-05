"""Rebuild a material checkpoint from tracked geometry, atlas and rig inputs."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from configure_rig import configure
p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
cfg=json.loads(Path(args.config).read_text());source=ROOT/cfg['baseline'];texture=ROOT/cfg['texture']
assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['baseline_sha256']
assert hashlib.sha256(texture.read_bytes()).hexdigest()==cfg['texture_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;o=next(o for o in s.objects if o.type=='MESH' and not o.hide_render)
nodes=o.data.materials[0].node_tree.nodes;links=o.data.materials[0].node_tree.links;bs=nodes.get('Principled BSDF')
im=bpy.data.images.load(str(texture),check_existing=False);im.colorspace_settings.name='sRGB';im.pack()
tex=nodes.new('ShaderNodeTexImage');tex.image=im;uv=nodes.new('ShaderNodeUVMap');uv.uv_map='Pigment atlas';assert o.data.uv_layers.get(uv.uv_map)
links.new(uv.outputs[0],tex.inputs['Vector']);links.new(tex.outputs['Color'],bs.inputs['Base Color'])
settings=cfg['material_config'];configure(s,settings);s['mission_material_config']=json.dumps(settings,sort_keys=True);s['mission_variant']=cfg['variant']
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.cycles.samples=64;s.cycles.use_denoising=True
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');print('MATERIAL_CHECKPOINT_REBUILT',flush=True)
