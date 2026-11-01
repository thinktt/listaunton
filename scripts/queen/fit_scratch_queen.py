"""Refit freshly drawn side-style controls to the original Lichess image at 54°.

The original sprite drives the fit. Smooth, bounded changes retain the carving
character of the side concept, which is an interpretation, not a measurement.
Real Blender renders remain the final check.
"""
from pathlib import Path
import sys, json, math
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent))
from scratch_profile import controls, apply_fit, PROFILE
from overlay_qa import largest_component,fill_holes

ROOT=Path(__file__).resolve().parents[2]
ref=ROOT/'references/lichess-staunton-3d/Black-Queen.png'
reg=json.loads((ROOT/'assets/queen/original-reference-alignment.json').read_text())
t,dx,dy=reg['scale'],reg['offset_x'],reg['offset_y']
image=Image.open(ref).convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,
 (1/t,0,-dx/t,0,1/t,-dy/t),Image.Resampling.BILINEAR)
a=np.asarray(image);mask=fill_holes(largest_component((a[:,:,3]>127)&(a[:,:,:3].max(2)>12)))
left=mask.argmax(1);right=mask.shape[1]-1-mask[:,::-1].argmax(1)
width=(right-left)/2;width[~mask.any(1)]=0
width=np.convolve(np.pad(width,(3,3),mode='edge'),np.ones(7)/7,'valid')
ys=np.arange(28,1120,4,dtype=float);target=np.interp(ys,np.arange(1254),width)
base=controls(96);e=math.radians(54);sn,cs=math.sin(e),math.cos(e)
def envelope(points,scale,floor):
    # Project the full turned cross section. Peak tips are included via their
    # upper and radial extents; rendered geometry determines the final metric.
    radii=np.linalg.norm(points[:,:,:2],axis=2).mean(1)
    z=points[:,:,2].mean(1)
    idx=np.linspace(0,len(z)-1,560)
    rr=np.interp(idx,np.arange(len(radii)),radii)*scale
    zz=np.interp(idx,np.arange(len(z)),z)
    y=floor-scale*cs*zz
    squared=rr[:,None]**2-((ys[None,:]-y[:,None])/sn)**2
    return np.sqrt(np.maximum(squared.max(0),0))

# Radius controls, feature-height offsets, uniform height change and camera.
p=np.zeros(16); camera_base=270.0;floor_base=860.0
def values(p):
    return dict(parameters=p[:13].tolist(),height_multiplier=1+p[13])
def loss(p,detail=False):
    points=apply_fit(base,values(p))
    if np.min(np.diff(points[:len(PROFILE),:,2].mean(1))) < -1e-5:return 1e8
    pred=envelope(points,camera_base*(1+p[14]),floor_base+p[15])
    delta=(pred-target)/t
    h=np.where(abs(delta)<2,.5*delta**2,2*abs(delta)-2)
    weights=np.where(ys<300,.65,1.0)
    silhouette=float(np.mean(weights*h))
    # Penalize departures from the drawing without forcing an exact imagined side.
    style=.24*np.mean((p[:8]/.12)**2)+.18*np.mean((p[8:13]/.15)**2)+.20*(p[13]/.15)**2
    smooth=.25*np.mean((np.diff(p[:8],2)/.1)**2)
    return (silhouette+style+smooth,silhouette,style,smooth) if detail else silhouette+style+smooth
initial=loss(p)
for step in [.04,.02,.01,.005,.0025]:
 for sweep in range(8):
  improved=False
  for j in range(len(p)):
   best=loss(p);bestp=p.copy()
   for sign in [-1,1]:
    trial=p.copy();delta=step*(200 if j==15 else 2 if 8<=j<13 else 1)
    limit=90 if j==15 else .16 if 8<=j<13 else .15 if j==13 else .12
    trial[j]=np.clip(trial[j]+sign*delta,-limit,limit)
    value=loss(trial)
    if value<best-1e-8:best=value;bestp=trial;improved=True
   p=bestp
  print('fit',step,sweep,round(loss(p),5),flush=True)
  if not improved:break
result={**values(p),'elevation_degrees_above_board':54,
 'camera_scale':camera_base*(1+p[14]),'camera_floor':floor_base+p[15],
 'camera_cx':reg['scale']*115.05+reg['offset_x'],
 'source':'references/lichess-staunton-3d/Black-Queen.png',
 'side_style_reference':'assets/queen/concepts/side-01.png',
 'initial_loss':initial,'final_loss':loss(p,True),
 'method':'Projected-ring width fit to the original black sprite at an assumed orthographic 54 degrees. Bounded profile deformations and a style penalty retain the new side-inspired carving where consistent with the original. Real-render validation is separate.'}
out=ROOT/'assets/queen/scratch-fit.json';out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
