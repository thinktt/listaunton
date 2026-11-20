"""Fit eleven existing crown reflectors against the repaired real wood material."""
from pathlib import Path
import bpy,numpy as np,PyOpenColorIO as ocio,json,hashlib,argparse,sys
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--finial-only',action='store_true');p.add_argument('--source',default='build/queen-mission/161-crown-grain-repair/queen.blend');p.add_argument('--variant',default='162-repaired-head-light-fit');p.add_argument('--fit-dir',default='crown-repair-fit-016');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/args.source
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
out=ROOT/'build/queen-mission'/args.fit_dir;out.mkdir(exist_ok=True,parents=True)
assert s.view_settings.exposure==0 and s.view_settings.gamma==1
print('VIEW',s.view_settings.view_transform,s.view_settings.look,flush=True)
assert s.view_settings.look in ('None','NONE')
alllights=[o for o in s.objects if o.type=='LIGHT'];powers={o.name:o.data.energy for o in alllights};spots=[o for o in alllights if ((not args.finial_only and o.name.startswith('Bowl focused ')) or ('finial-' in o.name and o.name.endswith('-spot')))]
count=len(spots);assert count==(3 if args.finial_only else 11)
world=s.world.node_tree.nodes['Background'];worldpower=world.inputs['Strength'].default_value
x1,y1,x2,y2=[422,145,541,275] if args.finial_only else [345,110,620,280]
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=(x1+.01)/1254;s.render.border_max_x=(x2+.01)/1254;s.render.border_min_y=(1254-y2+.01)/1254;s.render.border_max_y=(1254-y1+.01)/1254
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
ref_image=bpy.data.images.load(str(ROOT/'assets/queen/reference.png'),check_existing=False)
ref_image.colorspace_settings.name='Non-Color'
rw,rh=ref_image.size;ref=np.empty(rw*rh*4,dtype=np.float32);ref_image.pixels.foreach_get(ref)
ref=ref.reshape(rh,rw,4)[::-1,:,:3][y1:y2,x1:x2].copy();bpy.data.images.remove(ref_image)
assert ref.shape==baseline.shape,(ref.shape,baseline.shape)

config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
t=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX');forward=config.getProcessor(t).getDefaultCPUProcessor()
def display(a):
 a=np.ascontiguousarray(a,dtype=np.float32);forward.applyRGB(a);return a.astype(float)
base=baseline.reshape(-1,3);X=np.stack(responses,axis=-1).reshape(-1,3,count);target=ref.reshape(-1,3)
weights=.5+np.clip((target.min(1)-.2)*3,0,1);f=np.ones(count);history=[]
def loss(f):
 pred=display(base+X@f);return float(np.mean(weights[:,None]*(pred-target)**2)),pred
for iteration in range(20):
 err,pred=loss(f);linear=base+X@f;J=np.empty((len(base),3,count))
 for i in range(count):J[:,:,i]=(display(linear+X[:,:,i]*.02)-display(np.maximum(linear-X[:,:,i]*.02,0)))/.04
 A=J.reshape(-1,count);weight=np.repeat(weights,3);rhs=(target-pred).reshape(-1)+A@f
 gram=A.T@(A*weight[:,None])+np.eye(count)*.0001;b=A.T@(rhs*weight);proposal=f.copy()
 for step in range(100):
  prev=proposal.copy()
  for i in range(count):proposal[i]=np.clip(proposal[i]+(b[i]-gram[i]@proposal)/max(gram[i,i],1e-10),0,8)
  if np.max(abs(proposal-prev))<1e-6:break
 best=f;newerr=err
 for rate in [1,.5,.25,.125]:
  candidate=f+(proposal-f)*rate;v,_=loss(candidate)
  if v<newerr:best=candidate;newerr=v;break
 history.append({'iteration':iteration,'before_mse':err,'after_mse':newerr});f=best
 print('HEAD_FIT',iteration,newerr,f.tolist(),flush=True)
 if err-newerr<1e-8:break
for o in alllights:o.data.energy=powers[o.name]
world.inputs['Strength'].default_value=worldpower
cfg=json.loads(s['mission_material_config'])
for o,gain in zip(spots,f):
 o.data.energy=powers[o.name]*gain
 for spec in cfg['lights']:
  if spec['name']==o.name:spec['energy']=o.data.energy
cfg['variant']=args.variant;cfg['crown_reflector_fit']={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sample_count':512,'crop':[x1,y1,x2,y2],'gain_factors':dict(zip([o.name for o in spots],f.tolist())),'history':history,'method':'Full colored wood BSDF response per real linked light, fit through AgX; fixed remaining rig, geometry and material.'}
s['mission_material_config']=json.dumps(cfg);s['mission_variant']=cfg['variant']
trial=ROOT/'build/queen-mission'/cfg['variant'];trial.mkdir(exist_ok=True,parents=True)
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.render.filepath=str(trial/'wood.png');s.cycles.samples=64;s.cycles.use_adaptive_sampling=True;s.cycles.use_denoising=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(trial/'queen.blend'))
# Assess a freshly opened saved scene, avoiding transient state from response renders.
bpy.ops.wm.open_mainfile(filepath=str(trial/'queen.blend'),load_ui=False)
bpy.ops.render.render(write_still=True)
(trial/'parameters.json').write_text(json.dumps(cfg,indent=2));(out/'fit.json').write_text(json.dumps(cfg['crown_reflector_fit'],indent=2));print('CROWN_REFLECTOR_FIT_DONE',flush=True)
