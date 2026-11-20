"""Test a narrower varnish response without changing the scene's light rig."""
from pathlib import Path
import hashlib,json
import bpy
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'build/queen-mission/063-refined-tones/queen.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;o=next(o for o in s.objects if o.type=='MESH' and not o.hide_render);b=o.data.materials[0].node_tree.nodes.get('Principled BSDF')
settings={'Roughness':.12,'Coat Weight':.20,'Coat Roughness':.06}
for name,value in settings.items():
 assert not b.inputs[name].is_linked
 b.inputs[name].default_value=value
cfg=json.loads(s['mission_material_config']);cfg['variant']='066-sharper-varnish';cfg['varnish_response']={'source':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'settings':settings,'hypothesis':'Smaller reflection lobes may better match small finial spots and thin edge glints; keep the actual rig fixed for this isolated test.'};s['mission_material_config']=json.dumps(cfg,sort_keys=True)
out=ROOT/'build/queen-mission/066-sharper-varnish';out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png');s.cycles.samples=64;s.cycles.use_denoising=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');print('VARNISH_TRIAL_DONE',flush=True)
