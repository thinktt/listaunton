"""Test stronger bounded fine grain, with unchanged broad pigment and rig."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from image_math import blur
p=argparse.ArgumentParser();p.add_argument('--exponent',type=float,default=2.1);p.add_argument('--variant',default='094-stronger-fine-grain')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
assert 0<args.exponent<=3 and Path(args.variant).name==args.variant
source=ROOT/'build/queen-mission/093-direct-pigment-graph/queen.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='9f1bea6e0c1417a8a5cd8dcd772509965cd4779238bf53eac763523c8c1cf081'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;o=editable_mesh(s);n=o.data.materials[0].node_tree.nodes
response=ROOT/'build/queen-mission/pigment-fit-039'
old=np.load(response/'pigment.npy');ref=np.load(response/'reference-linear.npy');srgb=np.load(response/'reference-srgb.npy')
mask=(old[:,:,3]>.995).astype(np.float32)
broad=blur(old[:,:,:3]*mask[:,:,None],r=7,passes=3)/np.maximum(blur(mask,r=7,passes=3)[:,:,None],1e-6)
lum=np.maximum(ref@np.array([.2126,.7152,.0722],dtype=np.float32),0)
log=np.log(lum+.003);rm=(ref.max(2)>.001).astype(np.float32)
local=blur(log*rm,r=3,passes=3)/np.maximum(blur(rm,r=3,passes=3),1e-6)
detail=np.clip(log-local,-.55,.55)
weight=blur(np.clip((.68-srgb.min(2))/.4,0,1),r=3,passes=2)
rgba=np.dstack([np.clip(broad*np.exp(detail*weight*args.exponent)[:,:,None],0,.95),np.ones_like(lum)]).astype(np.float32)
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(parents=True,exist_ok=True)
im=bpy.data.images.new('Queen stronger fine pigment',width=rgba.shape[1],height=rgba.shape[0],alpha=False,float_buffer=True)
im.colorspace_settings.name='Linear Rec.709';im.pixels.foreach_set(rgba[::-1].copy().reshape(-1))
im.filepath_raw=str(out/'pigment.exr');im.file_format='OPEN_EXR';im.save();im.pack()
n['Image Texture.004'].image=im
cfg=json.loads(s['mission_material_config']);cfg['variant']=out.name
cfg['fine_grain_gain_trial']={'source':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'exponent_before':1.5,'exponent_after':args.exponent,'reference_blur_radius':3,'broad_pigment_blur_radius':7,'detail_log_bounds':[-.55,.55],'reference_sha256':hashlib.sha256((ROOT/'assets/queen/reference.png').read_bytes()).hexdigest(),'input_array_hashes':{name:hashlib.sha256((response/name).read_bytes()).hexdigest() for name in ['pigment.npy','reference-linear.npy','reference-srgb.npy']},'caveat':'Bounded fine luminance texture is an artistic pigment inference. Geometry, references, relief, broad pigment and lighting are unchanged.'}
s['mission_material_config']=json.dumps(cfg,sort_keys=True)
s.render.filepath=str(out/'wood.png');s.cycles.samples=64;s.cycles.use_denoising=True;s.render.use_persistent_data=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('FINE_GRAIN_GAIN_TRIAL_DONE',flush=True)
