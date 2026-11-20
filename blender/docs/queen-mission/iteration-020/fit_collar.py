"""Small, bounded collar refit from an actual trial, without moving source pixels."""
from pathlib import Path
import json, math
import numpy as np
from PIL import Image
from scipy.optimize import least_squares
HERE=Path(__file__).resolve().parent
ROOT=next((p for p in HERE.parents if (p/'assets/queen').is_dir()),HERE.parent/'queen-profile-019');A=ROOT/'assets/queen'
control=np.load(ROOT/'build/queen-mission/189-rounded-lower-edge/controls.npz')['after']
base=np.c_[np.linalg.norm(control[:,:,:2],axis=2).mean(1),control[:,:,2].mean(1)].astype(float)
fit=json.loads((A/'finish-fit.json').read_text());S=fit['camera_scale'];y0=fit['camera_floor'];el=math.radians(54)
reg=json.loads((A/'original-reference-alignment.json').read_text());t,x,y=reg['scale'],reg['offset_x'],reg['offset_y']
original=Image.open(ROOT/'references/lichess-staunton-3d/Black-Queen.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(1/t,0,-x/t,0,1/t,-y/t),Image.Resampling.BILINEAR)
ys=np.arange(405,570)
def widths(im,ref=False):
    a=np.asarray(im.convert('RGBA'));m=a[:,:,3]>127
    if ref:m&=a[:,:,:3].max(2)>12
    v=(m.shape[1]-1-m[:,::-1].argmax(1)-m.argmax(1))/2;v[~m.any(1)]=0
    return v[ys]
target=widths(original,True);hi=widths(Image.open(A/'reference.png'),True)
trial=widths(Image.open(ROOT/'build/queen-mission/189-rounded-lower-edge/wood.png'))
old=widths(Image.open(ROOT/'history/queen-mission-019/queen-brown.png'))
tt=np.linspace(0,1,32,endpoint=False)
B=np.stack([(1-tt)**3,3*tt**3-6*tt*tt+4,-3*tt**3+3*tt*tt+3*tt+1,tt**3],axis=1)/6
indices=np.arange(51,59)
def envelope(p):
    cur=base.copy();cur[indices,0]+=p
    dense=np.concatenate([B@cur[i:i+4] for i in range(38,80)])
    rad=dense[:,0,None]*S;cy=y0-S*math.cos(el)*dense[:,1,None]
    return np.sqrt(np.maximum((rad*rad-((ys[None,:]-cy)/math.sin(el))**2).max(0),0))
zero=np.zeros(len(indices));cal=trial-envelope(zero)
def residual(p):
    pred=envelope(p)+cal
    return np.r_[(pred-target)/2,.25*(pred-hi)/2,p/.008,2*np.diff(p)/.008]
bound=np.array([.012,.012,.006,.005,.004,.005,.006,.006])
opt=least_squares(residual,zero,bounds=(-bound,bound),diff_step=.001,max_nfev=100)
cfg=json.loads((HERE/'189-rounded-lower-edge.json').read_text())
cfg['variant']='191-rounded-edge-refit'
cfg['hypothesis']='Keep the rounded collar underside and refit its radii within small bounds to the original outline, with lower weight for the generated high-resolution image.'
cfg['radii']={str(int(i)):float(base[i,0]+p) for i,p in zip(indices,opt.x)}
cfg['fit']={'success':bool(opt.success),'initial_loss':float(np.mean(residual(zero)**2)),'fitted_loss':float(np.mean(residual(opt.x)**2)),'radius_adjustments':opt.x.tolist(),'note':'Calibrated projected B-spline approximation; actual saved Blender renders decide acceptance.'}
(HERE/'191-rounded-edge-refit.json').write_text(json.dumps(cfg,indent=2)+'\n',encoding='utf-8')
print(json.dumps(cfg,indent=2))
print('y, original width, selected width, accepted width, trial width, predicted width')
pred=envelope(opt.x)+cal
for i in range(0,len(ys),10):print(ys[i],target[i],hi[i],old[i],trial[i],round(pred[i],2))
