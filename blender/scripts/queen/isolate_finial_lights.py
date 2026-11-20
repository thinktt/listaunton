"""Test broad finial lights and diagnose specular contributors separately."""
from pathlib import Path
import hashlib,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from configure_rig import configure
source=ROOT/'models/queen/queen-rebuilt.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest()
assert digest=='16904dba7abc57e60ec8e6d73c30f46f9e0890ec46272753c648e7e88f64247e'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
original=json.loads(s['mission_material_config']);cfg=json.loads(json.dumps(original))
names={'Display fitted finial-left','Display fitted finial-top','Display fitted finial-right'}
cfg['lights']=[v for v in cfg['lights'] if v['name'] not in names]
cfg['variant']='070-isolated-finial-lights';cfg['light_isolation']={'source_sha256':digest,'removed_area_lights':sorted(names),'hypothesis':'Remove broad finial area reflections while keeping their narrow spots. Diagnostic passes also inspect whether the vertical base key spills onto the finial.'}
configure(s,cfg);s['mission_material_config']=json.dumps(cfg,sort_keys=True)
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
s.render.use_persistent_data=True;s.cycles.samples=64;s.cycles.use_denoising=True;s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
configure(s,original);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
o=next(o for o in s.objects if o.type=='MESH' and not o.hide_render);n=o.data.materials[0].node_tree.nodes;l=o.data.materials[0].node_tree.links;b=n.get('Principled BSDF')
for link in list(b.inputs['Base Color'].links):l.remove(link)
b.inputs['Base Color'].default_value=(0,0,0,1)
s.render.resolution_x=s.render.resolution_y=418
groups={'base-key':lambda name:name=='Display fitted base-key','finial-areas':lambda name:name in names,'finial-spots':lambda name:name.endswith('-spot'),'remaining':lambda name:name not in names and not name.endswith('-spot') and name!='Display fitted base-key'}
for name,predicate in groups.items():
 for light in s.objects:
  if light.type=='LIGHT':light.hide_render=not predicate(light.name)
 s.render.filepath=str(out/('diagnostic-'+name+'.png'));bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print('FINIAL_LIGHT_ISOLATION_DONE',flush=True)
