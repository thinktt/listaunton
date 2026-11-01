"""Small physical refit calibrated to the latest actual Blender render."""
from pathlib import Path
import json,math,sys
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent))
from scratch_profile import controls,apply_fit,PROFILE
from overlay_qa import largest_component,fill_holes
root=Path(__file__).resolve().parents[2];out=root/'assets/queen'
fit=json.loads((out/'scratch-fit.json').read_text());reg=json.loads((out/'original-reference-alignment.json').read_text())
t,dx,dy=reg['scale'],reg['offset_x'],reg['offset_y']
reference=Image.open(root/'references/lichess-staunton-3d/Black-Queen.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(1/t,0,-dx/t,0,1/t,-dy/t),Image.Resampling.BILINEAR)
a=np.asarray(reference);om=fill_holes(largest_component((a[:,:,3]>127)&(a[:,:,:3].max(2)>12)))
mm=np.asarray(Image.open(out/'queen-matched.png').convert('RGBA'))[:,:,3]>127
ys=np.arange(28,1105,4,dtype=float)
def widths(m):
 left=m.argmax(1);right=m.shape[1]-1-m[:,::-1].argmax(1)
 value=(right-left)/2;value[~m.any(1)]=0
 value=np.convolve(np.pad(value,(3,3),mode='edge'),np.ones(7)/7,'valid')
 return np.interp(ys,np.arange(1254),value)
target=widths(om);actual=widths(mm)
points=controls(96);sn=math.sin(math.radians(54));cs=math.cos(math.radians(54))
old_scale=fit['camera_scale'];old_floor=fit['camera_floor']
def envelope(p):
 f=dict(fit);f['parameters']=p.tolist();a=apply_fit(points,f)
 r=np.linalg.norm(a[:,:,:2],axis=2).mean(1);z=a[:,:,2].mean(1)
 idx=np.linspace(0,len(z)-1,560);r=np.interp(idx,np.arange(len(r)),r)*old_scale;z=np.interp(idx,np.arange(len(z)),z)
 y=old_floor-old_scale*cs*z
 return np.sqrt(np.maximum((r[:,None]**2-((ys[None,:]-y[:,None])/sn)**2).max(0),0))
starting=np.asarray(fit['parameters']);base=envelope(starting)
def loss(p):
 f=dict(fit);f['parameters']=p.tolist();a=apply_fit(points,f)
 if np.min(np.diff(a[:len(PROFILE),:,2].mean(1))) < -1e-5:return 1e8
 pred=np.maximum(0,actual+envelope(p)-base)
 delta=(pred-target)/t;h=np.where(abs(delta)<2,.5*delta**2,2*abs(delta)-2)
 weight=np.where(ys<305,.35,1.0)
 diff=p-starting
 return float(np.mean(weight*h)+.12*np.mean((diff[:8]/.04)**2)+.12*np.mean((diff[8:]/.07)**2)+.15*np.mean((np.diff(diff[:8],2)/.04)**2))
p=starting.copy();before=loss(p)
for step in [.02,.01,.005,.0025]:
 for sweep in range(5):
  improved=False
  for j in range(len(p)):
   best=loss(p);bestp=p.copy()
   for direction in [-1,1]:
    trial=p.copy();limit=.045 if j<8 else .08;delta=step if j<8 else step*1.5
    trial[j]=np.clip(trial[j]+direction*delta,starting[j]-limit,starting[j]+limit)
    value=loss(trial)
    if value<best-1e-8:best=value;bestp=trial;improved=True
   p=bestp
  if not improved:break
fit['parameters']=p.tolist();fit['actual_render_refinement']={'source':'Black-Queen.png',
 'method':'Bounded adjustments to the new profile using a projected-ring approximation calibrated to its actual prior render. Original Lichess sprite weighted as target.',
 'loss_before':before,'loss_after':loss(p),'parameter_delta':(p-starting).tolist()}
(out/'scratch-fit.json').write_text(json.dumps(fit,indent=2)+'\n')
print(json.dumps(fit['actual_render_refinement'],indent=2))
