"""Fit the physical socket crescent through measured full-wood light responses."""
from pathlib import Path
import bpy,numpy as np,PyOpenColorIO as ocio,json,hashlib
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'build/queen-mission/135-socket-crescent/queen.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
out=ROOT/'build/queen-mission/socket-crescent-fit-013';out.mkdir(exist_ok=True,parents=True)
assert s.view_settings.exposure==0 and s.view_settings.gamma==1
print('VIEW',s.view_settings.view_transform,s.view_settings.look,flush=True)
assert s.view_settings.look in ('None','NONE')
alllights=[o for o in s.objects if o.type=='LIGHT'];powers={o.name:o.data.energy for o in alllights};spots=[o for o in alllights if o.name.startswith('Socket crescent ')]
assert len(spots)==10
world=s.world.node_tree.nodes['Background'];worldpower=world.inputs['Strength'].default_value
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=(365+.01)/1254;s.render.border_max_x=(600+.01)/1254;s.render.border_min_y=(1254-795+.01)/1254;s.render.border_max_y=(1254-695+.01)/1254
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA';s.render.use_persistent_data=True
s.cycles.samples=512;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
def render(name):
 path=out/(name+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 im=bpy.data.images.load(str(path),check_existing=False);w,h=im.size[:];a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);a=a.reshape(h,w,4)[::-1,:,:3].copy();np.save(out/(name+'.npy'),a);return a
for o in spots:o.data.energy=0
baseline=render('baseline')
for o in alllights:o.data.energy=0
world.inputs['Strength'].default_value=0
responses=[]
for i,o in enumerate(spots):
 o.data.energy=powers[o.name];responses.append(render('response-'+str(i)));o.data.energy=0
ref=np.load(ROOT/'build/queen-mission/socket-inspection-013/reference-srgb.npy')[695:795,365:600];assert ref.shape==baseline.shape,(ref.shape,baseline.shape)
config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
t=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX');forward=config.getProcessor(t).getDefaultCPUProcessor()
def display(a):
 a=np.ascontiguousarray(a,dtype=np.float32);forward.applyRGB(a);return a.astype(float)
base=baseline.reshape(-1,3);X=np.stack(responses,axis=-1).reshape(-1,3,10);target=ref.reshape(-1,3)
weights=.5+np.clip((target.min(1)-.2)*3,0,1);f=np.ones(10);history=[]
def loss(f):
 pred=display(base+X@f);return float(np.mean(weights[:,None]*(pred-target)**2)),pred
for iteration in range(20):
 err,pred=loss(f);linear=base+X@f;J=np.empty((len(base),3,10))
 for i in range(10):J[:,:,i]=(display(linear+X[:,:,i]*.02)-display(np.maximum(linear-X[:,:,i]*.02,0)))/.04
 A=J.reshape(-1,10);weight=np.repeat(weights,3);rhs=(target-pred).reshape(-1)+A@f
 gram=A.T@(A*weight[:,None])+np.eye(10)*.0001;b=A.T@(rhs*weight);proposal=f.copy()
 for step in range(100):
  prev=proposal.copy()
  for i in range(10):proposal[i]=np.clip(proposal[i]+(b[i]-gram[i]@proposal)/max(gram[i,i],1e-10),0,8)
  if np.max(abs(proposal-prev))<1e-6:break
 best=f;newerr=err
 for rate in [1,.5,.25,.125]:
  candidate=f+(proposal-f)*rate;v,_=loss(candidate)
  if v<newerr:best=candidate;newerr=v;break
 history.append({'iteration':iteration,'before_mse':err,'after_mse':newerr});f=best
 print('SOCKET_FIT',iteration,newerr,f.tolist(),flush=True)
 if err-newerr<1e-8:break
for o in alllights:o.data.energy=powers[o.name]
world.inputs['Strength'].default_value=worldpower
cfg=json.loads(s['mission_material_config'])
for o,gain in zip(spots,f):
 o.data.energy=powers[o.name]*gain
 for spec in cfg['lights']:
  if spec['name']==o.name:spec['energy']=o.data.energy
cfg['variant']='136-fitted-socket-crescent';cfg['socket_crescent_fit']={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sample_count':512,'crop':[365,695,600,795],'gain_factors':dict(zip([o.name for o in spots],f.tolist())),'history':history,'method':'Full colored wood BSDF response per real linked light, fit through AgX; fixed remaining rig, geometry and material.'}
s['mission_material_config']=json.dumps(cfg);s['mission_variant']=cfg['variant']
trial=ROOT/'build/queen-mission'/cfg['variant'];trial.mkdir(exist_ok=True,parents=True)
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.render.filepath=str(trial/'wood.png');s.cycles.samples=64;s.cycles.use_adaptive_sampling=True;s.cycles.use_denoising=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(trial/'queen.blend'));bpy.ops.render.render(write_still=True)
(trial/'parameters.json').write_text(json.dumps(cfg,indent=2));(out/'fit.json').write_text(json.dumps(cfg['socket_crescent_fit'],indent=2));print('SOCKET_CRESCENT_FIT_DONE',flush=True)
