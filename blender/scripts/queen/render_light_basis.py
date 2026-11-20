"""Render independent physical light contributions for a nonnegative energy fit.

These linear EXRs are diagnostics. A fitted rig must be rendered normally and
visually validated before any result can replace the accepted beauty image.
"""
from pathlib import Path
import json,math,sys,argparse,hashlib
import bpy
import numpy as np
import PyOpenColorIO as ocio
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--inspect-only',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=ROOT/'build/queen-mission/light-fit';out.mkdir(parents=True,exist_ok=True)
source=ROOT/'models/queen/queen-rebuilt.blend';source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);scene=bpy.context.scene
config_path=Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'
config=ocio.Config.CreateFromFile(str(config_path))
view=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display=scene.display_settings.display_device,view=scene.view_settings.view_transform)
view.setDirection(ocio.TRANSFORM_DIR_INVERSE);inverse=config.getProcessor(view).getDefaultCPUProcessor()
reference=np.load(out/'reference-srgb.npy');linear=reference.copy();inverse.applyRGB(linear)
view.setDirection(ocio.TRANSFORM_DIR_FORWARD);forward=config.getProcessor(view).getDefaultCPUProcessor();check=linear.copy();forward.applyRGB(check)
mask=reference.max(2)>.05;error=np.abs(check-reference)[mask]
assert np.isfinite(linear).all();assert float(error.mean())<.002,(float(error.mean()),float(error.max()))
np.save(out/'reference-linear.npy',linear)
print('OCIO inverse round trip',float(error.mean()),float(error.max()),'config',config_path,flush=True)
if args.inspect_only:sys.exit(0)
specs=[
 {'name':'original-top','position':[-1,-.3,12],'energy':1100,'size':.6},
 {'name':'original-right','position':[3,-5,7],'energy':400,'size':.5},
 {'name':'original-foot','position':[-3,-3,1.5],'target':[0,0,.3],'energy':150,'size':.7},
 {'name':'base-key','position':[3.74,-3.69,4.63],'target':[.3567,-.6887,.6858],'energy':280,'shape':'RECTANGLE','size':.45,'size_y':3.8},
 {'name':'socket-left','position':[-3.09,-3.65,5.45],'target':[-.2,-.45,1.28],'energy':250,'size':.7},
 {'name':'bowl-left','position':[.861,2.062,9.663],'target':[-.21,.31,4.03],'energy':300,'size':.7},
 {'name':'bowl-back','position':[-1.14,.93,9.88],'target':[.08,.4,4.03],'energy':500,'size':.6},
 {'name':'collars-right','position':[5.61,-3.34,2.74],'target':[.36,-.45,3.08],'energy':300,'size':.7},
 {'name':'lower-collar','position':[.83,2.1,8.24],'target':[.31,-.53,2.87],'energy':300,'size':.7},
 {'name':'finial-left','position':[-1.45,-3.81,8.94],'target':[-.02,-.09,4.46],'energy':150,'size':.3},
 {'name':'finial-top','position':[3.23,-2.24,9.06],'target':[.04,-.07,4.46],'energy':150,'size':.3},
 {'name':'foot-low','position':[-3.64,-5.42,-2.02],'target':[-.38,-.93,.25],'energy':200,'size':.8},
 {'name':'base-rear','position':[-2.84,5.9,-.87],'target':[-.63,.53,.64],'energy':100,'size':.8},
 {'name':'soft-fill','position':[0,-4,8],'target':[0,0,2.6],'energy':800,'size':5,'specular_factor':0},
 {'name':'world','world':.1}
]
for light in list(scene.objects):
 if light.type=='LIGHT':bpy.data.objects.remove(light,do_unlink=True)
scene.render.resolution_x=scene.render.resolution_y=418;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_depth='32';scene.render.image_settings.color_mode='RGBA'
scene.render.use_persistent_data=True;scene.cycles.samples=32;scene.cycles.use_denoising=False
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
manifest={'source_sha256':source_hash,'width':418,'height':418,'samples':32,'denoising':False,'color_config':str(config_path),'inverse_round_trip_mae':float(error.mean()),'specs':specs}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for i,spec in enumerate(specs):
 for light in list(scene.objects):
  if light.type=='LIGHT':bpy.data.objects.remove(light,do_unlink=True)
 scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=spec.get('world',0)
 if 'position' in spec:
  data=bpy.data.lights.new(spec['name'],'AREA');data.energy=spec['energy'];data.shape=spec.get('shape','DISK');data.size=spec['size'];data.specular_factor=spec.get('specular_factor',1)
  if data.shape=='RECTANGLE':data.size_y=spec['size_y']
  light=bpy.data.objects.new(spec['name'],data);scene.collection.objects.link(light);light.location=spec['position'];light.rotation_euler=(Vector(spec.get('target',[0,0,2.3]))-light.location).to_track_quat('-Z','Y').to_euler()
 path=out/(spec['name']+'.exr');scene.render.filepath=str(path)
 bpy.ops.render.render(write_still=True)
 im=bpy.data.images.load(str(path),check_existing=False);a=np.empty(418*418*4,dtype=np.float32);im.pixels.foreach_get(a);a=a.reshape(418,418,4)[::-1].copy();bpy.data.images.remove(im)
 np.save(out/(spec['name']+'.npy'),a)
 print('LIGHT_BASIS_DONE',i+1,len(specs),spec['name'],flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
print('ALL_LIGHT_BASES_DONE',flush=True)
