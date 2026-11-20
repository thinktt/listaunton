"""Limit a real area light's spread, preserving its measured base contribution."""
from pathlib import Path
import hashlib,json,sys
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from configure_rig import configure
source=ROOT/'models/queen/queen-rebuilt.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest()
assert digest=='16904dba7abc57e60ec8e6d73c30f46f9e0890ec46272753c648e7e88f64247e'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
cfg=json.loads(s['mission_material_config']);spec=next(v for v in cfg['lights'] if v['name']=='Display fitted base-key')
prior_energy=spec['energy'];spec['spread_degrees']=36
basis=ROOT/'build/queen-mission/specular-expanded-039'
manifest=json.loads((basis/'manifest.json').read_text());oldspec=next(v for v in manifest['specs'] if v['name']=='base-key')
old=np.load(basis/'base-key.npy')[:,:,:3]*(prior_energy/oldspec['energy'])
test=dict(spec);test['energy']=oldspec['energy'];test['color']=[1,1,1]
configure(s,{'lights':[test],'world':0,'cycles_ray_visibility':True})
o=next(o for o in s.objects if o.type=='MESH' and not o.hide_render);nodes=o.data.materials[0].node_tree.nodes;links=o.data.materials[0].node_tree.links;b=nodes.get('Principled BSDF')
color=b.inputs['Base Color'].links[0].from_socket
for link in list(b.inputs['Base Color'].links):links.remove(link)
b.inputs['Base Color'].default_value=(0,0,0,1)
out=ROOT/'build/queen-mission/071-limited-base-reflector';out.mkdir(parents=True,exist_ok=True)
s.render.resolution_x=s.render.resolution_y=418;s.render.use_persistent_data=True;s.cycles.samples=64;s.cycles.use_denoising=False
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA';s.render.filepath=str(out/'diagnostic-limited-reflector.exr')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
im=bpy.data.images.load(s.render.filepath,check_existing=False);a=np.empty(418*418*4,dtype=np.float32);im.pixels.foreach_get(a);a=a.reshape(418,418,4)[::-1].copy();bpy.data.images.remove(im)
np.save(out/'diagnostic-limited-reflector.npy',a)
# Keep the previously accepted base contribution; this is not a new fit to
# the photograph, and deliberately excludes the crown we intend to darken.
roi=(slice(270,350),slice(70,255));x=a[roi][:,:,:3];y=old[roi]
factor=float(np.sum(x*y)/max(np.sum(x*x),1e-12));assert 0<factor<10
spec['energy']=oldspec['energy']*factor
cfg['variant']='071-limited-base-reflector';cfg['source']='models/queen/queen-rebuilt.blend'
cfg['reflector_spread_trial']={'source_sha256':digest,'spread_degrees':36,'previous_energy':prior_energy,'new_energy':spec['energy'],'power_fit_roi_at_418':[70,270,255,350],'old_response_source':str((basis/'base-key.npy').relative_to(ROOT)),'old_response_sha256':hashlib.sha256((basis/'base-key.npy').read_bytes()).hexdigest(),'old_black_response_geometry_and_relief_preserved':True,'hypothesis':'Prevent the tall base reflector from also drawing a vertical streak on the finial. Refit only its power to preserve the prior base contribution.'}
links.new(color,b.inputs['Base Color']);configure(s,cfg);s['mission_material_config']=json.dumps(cfg,sort_keys=True)
s.render.resolution_x=s.render.resolution_y=1254;s.cycles.use_denoising=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'));bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print('LIMITED_REFLECTOR_DONE',cfg['reflector_spread_trial'],flush=True)
