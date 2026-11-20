"""Fit only the color/power of the real base reflector from fresh BSDF responses."""
from pathlib import Path
import sys,json,hashlib,argparse
import bpy,numpy as np,PyOpenColorIO as ocio
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',default='build/queen-mission/121-rectified-base-panel/queen.blend');p.add_argument('--variant',default='122-color-refined-base');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/args.source;digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;light=bpy.data.objects['Display fitted base-key'];lights=[o for o in s.objects if o.type=='LIGHT'];powers={o.name:o.data.energy for o in lights};world=s.world.node_tree.nodes['Background'];world_power=world.inputs['Strength'].default_value
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(parents=True,exist_ok=True);x1,y1,x2,y2=490,800,680,1005;W=s.render.resolution_x;H=s.render.resolution_y;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=x1/W;s.render.border_max_x=x2/W;s.render.border_min_y=1-y2/H;s.render.border_max_y=1-y1/H;s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA';s.render.use_persistent_data=True;s.cycles.samples=512;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
def render(name):
 path=out/(name+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);im=bpy.data.images.load(str(path),check_existing=False);w,h=im.size;a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(h,w,4)[::-1,:,:3].copy()
light.data.energy=0;baseline=render('baseline')
for o in lights:o.data.energy=0
world.inputs['Strength'].default_value=0;light.data.energy=powers[light.name];response=render('response')
ref=np.load(ROOT/'build/queen-mission/pigment-fit-011/reference-srgb.npy')[y1:y2,x1:x2];assert ref.shape==baseline.shape,(ref.shape,baseline.shape);np.savez_compressed(out/'responses.npz',baseline=baseline,response=response,reference=ref)
config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'));transform=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX');forward=config.getProcessor(transform).getDefaultCPUProcessor()
def display(a):
 a=np.ascontiguousarray(a,dtype=np.float32);forward.applyRGB(a);return a.astype(float)
base=baseline.reshape(-1,3);X=response.reshape(-1,3);target=ref.reshape(-1,3);weights=.5+np.clip((target.min(1)-.2)*3,0,1);gains=np.ones(3);history=[]
def loss(g):
 pred=display(base+X*g);return float(np.mean(weights[:,None]*(pred-target)**2)),pred
for iteration in range(15):
 err,pred=loss(gains);linear=base+X*gains;J=np.empty((len(base),3,3))
 for i in range(3):
  delta=np.zeros_like(X);delta[:,i]=X[:,i]*.02;J[:,:,i]=(display(linear+delta)-display(np.maximum(linear-delta,0)))/.04
 A=J.reshape(-1,3);weight=np.repeat(weights,3);rhs=(target-pred).reshape(-1)+A@gains;gram=A.T@(A*weight[:,None])+np.eye(3)*1e-5;b=A.T@(rhs*weight);proposal=np.clip(np.linalg.solve(gram,b),.25,3);best=gains;newerr=err
 for rate in [1,.5,.25,.125]:
  trial=gains+(proposal-gains)*rate;value,_=loss(trial)
  if value<newerr:best=trial;newerr=value;break
 history.append({'iteration':iteration,'before_mse':err,'after_mse':newerr});gains=best
 if err-newerr<1e-9:break
for o in lights:o.data.energy=powers[o.name]
world.inputs['Strength'].default_value=world_power;color=np.array(light.data.color)*gains;normalizer=max(float(color.max()),1);light.data.color=tuple(color/normalizer);light.data.energy=powers[light.name]*normalizer
cfg=json.loads(s['mission_material_config']);spec=next(a for a in cfg['lights'] if a['name']==light.name);spec['color']=list(light.data.color);spec['energy']=light.data.energy;cfg['variant']=args.variant;cfg['base_reflector_color_fit']={'source_sha256':digest,'crop':[x1,y1,x2,y2],'sample_count':512,'channel_gains':gains.tolist(),'history':history,'method':'Fresh real BSDF baseline and isolated base light, fitted through AgX. Only the actual light color and power change; no beauty compositing.'};s['mission_material_config']=json.dumps(cfg);s['mission_variant']=args.variant
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.render.filepath=str(out/'wood.png');s.cycles.samples=128;s.cycles.use_adaptive_sampling=True;s.cycles.use_denoising=True;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'));bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2));print('BASE_COLOR_FIT_DONE',json.dumps(cfg['base_reflector_color_fit']),flush=True)
