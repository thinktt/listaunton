"""Fit real reflection-light powers after the AgX display transform.

Unlike the earlier linear-intensity fit, this objective measures displayed
colors and keeps clipped peak pixels from dominating the rest of a highlight.
Run with Blender for its exact bundled OCIO processor; no render is performed.
"""
from pathlib import Path
import argparse,json,sys
import bpy
import numpy as np
import PyOpenColorIO as ocio
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--directory',default='build/queen-mission/specular-narrow-spots-039');p.add_argument('--output',default='build/queen-mission/display-reflection-fit');p.add_argument('--variant',default='053-display-reflections')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=ROOT/args.output;out.mkdir(parents=True,exist_ok=True)
directory=ROOT/args.directory
if not directory.exists():
 choices=list((ROOT/'build/queen-mission').glob('specular*039/manifest.json'))
 directory=next(p.parent for p in choices if len(json.loads(p.read_text())['specs'])==19 and any(s.get('spot_degrees')==1.2 for s in json.loads(p.read_text())['specs']))
m=json.loads((directory/'manifest.json').read_text());specs=m['specs'];responses=[np.load(directory/(s['name']+'.npy')) for s in specs]
mask=responses[0][:,:,3]>.995
bases=np.stack([a[:,:,:3].mean(2)[mask] for a in responses],axis=1).astype(np.float64)
world=next(i for i,s in enumerate(specs) if s['name']=='world')
config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
t=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX')
forward=config.getProcessor(t).getDefaultCPUProcessor();t.setDirection(ocio.TRANSFORM_DIR_INVERSE);inverse=config.getProcessor(t).getDefaultCPUProcessor()
accepted=np.load(ROOT/'build/queen-mission/display-reflection-fit/accepted-srgb.npy');inverse.applyRGB(accepted)
black=np.load(ROOT/'build/queen-mission/pigment-fit-039/black-bsdf.npy')[:,:,:3]
diffuse=(accepted-black).reshape(418,3,418,3,3).mean((1,3))[mask]
baseline=np.maximum(diffuse,0)+bases[:,world,None]*.3
ref=np.load(ROOT/'build/queen-mission/pigment-fit-039/reference-srgb.npy').reshape(418,3,418,3,3).mean((1,3))[mask]
# Modest emphasis on pale highlights, while penalizing new stray reflections.
weight=.4+np.clip(ref.min(1)*3,0,1)
color=np.array([1,.7,.5]);X=bases.copy();X[:,world]=0
def display(a):
 v=np.asarray(a,dtype=np.float32).copy();forward.applyRGB(v);return v.astype(np.float64)
def loss(f):
 a=display(baseline+(X@f)[:,None]*color);return float(np.mean(weight[:,None]*(a-ref)**2)),a
f=np.zeros(len(specs));f[:3]=.5
history=[]
for step in range(30):
 value,pred=loss(f);amp=X@f;linear=baseline+amp[:,None]*color
 epsilon=np.maximum(.0001,amp*.005)
 deriv=(display(linear+epsilon[:,None]*color)-display(np.maximum(linear-epsilon[:,None]*color,0)))/(2*epsilon[:,None])
 norm=(deriv**2).sum(1)*weight
 rhs_pixel=((ref-pred)*deriv).sum(1)*weight+norm*amp
 scale=np.sqrt((X*X*norm[:,None]).sum(0));scale=np.maximum(scale,1e-6)
 A=X/scale;gram=A.T@(A*norm[:,None])+np.eye(len(specs))*1e-4;rhs=A.T@rhs_pixel
 proposal=f*scale
 for iteration in range(500):
  previous=proposal.copy()
  for i in range(len(specs)):
   proposal[i]=max(0,proposal[i]+(rhs[i]-gram[i]@proposal)/gram[i,i]) if i!=world else 0
  if np.max(abs(proposal-previous))<1e-6:break
 target=proposal/scale
 chosen=f;newvalue=value
 for rate in (1,.5,.25,.125,.0625):
  trial=f+(target-f)*rate;v,_=loss(trial)
  if v<newvalue:chosen=trial;newvalue=v;break
 history.append({'iteration':step,'weighted_display_mse':value,'accepted_mse':newvalue});f=chosen
 print('DISPLAY_FIT',step,value,newvalue,flush=True)
 if value-newvalue<1e-8:break
acceptedcfg=json.loads((ROOT/'build/queen-mission/026-graded-atlas/parameters.json').read_text())
lights=[]
for light in acceptedcfg['lights']:
 v=dict(light);v['name']='Diffuse '+v['name'];v['specular_factor']=0;lights.append(v)
for spec,factor in zip(specs,f):
 if 'position' not in spec or factor<1e-5:continue
 v=dict(spec);v['name']='Display fitted '+v['name'];v['energy']=float(v['energy']*factor);v['diffuse_factor']=0;v['color']=color.tolist();lights.append(v)
cfg={'variant':args.variant,'source':'models/queen/queen-rebuilt.blend','samples':64,'world':.03,'lights':lights,'cycles_ray_visibility':True,'method':'Fit actual light response powers through AgX to displayed reference; accepted diffuse rig retained','light_chromaticity':color.tolist(),'response_source':directory.relative_to(ROOT).as_posix(),'caveat':'Art-directed light powers; approximate diffuse/specular separation and low-resolution basis. Requires a full render and visual verification.'}
(out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
(out/'fit.json').write_text(json.dumps({'history':history,'factors':{s['name']:float(v) for s,v in zip(specs,f)},'pixels':int(mask.sum())},indent=2)+'\n')
predicted=np.zeros((418,418,3),dtype=np.float32);predicted[mask]=loss(f)[1];np.save(out/'predicted-srgb.npy',predicted)
print('DISPLAY_REFLECTION_FIT_DONE',flush=True)
