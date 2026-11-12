"""Conservative local lathe proposal against the registered original outline.

The analytical subdivision approximation proposes controls only. Saved Blender
renders, internal landmarks and original/detail comparisons decide acceptance.
No source, camera or registration is adjusted by this analysis.
"""
from pathlib import Path
import argparse, hashlib, json, math
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',default='build/bishop-mission/134-geometry-audit')
p.add_argument('--mode',choices=['radial','radial-smooth','shoulder-height','stem'],default='radial')
a=p.parse_args();out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
cfg=json.loads((ROOT/'history/bishop-mission-015/profile.json').read_text())
al=json.loads((ROOT/'assets/bishop/original-alignment.json').read_text())
F=1254/300/al['scale'];sn=math.sin(math.radians(54));cx=(cfg['cx']-al['x']*3)*F
base_spec=None
if a.mode=='stem':
    base_spec=json.loads((out/'upper-collar-fit.json').read_text())
    for key,pair in base_spec['body_rings'].items():cfg['profile'][int(key)]=pair
profile=np.array(cfg['profile'],dtype=float)
original=Image.open(ROOT/'assets/bishop/original.png').convert('RGBA').transform(
    (1254,1254),Image.Transform.AFFINE,(al['scale']*300/1254,0,al['x']*3,0,al['scale']*300/1254,al['y']*3),Image.Resampling.BILINEAR)
ref=np.array(original);mask=(ref[:,:,3]>127)&(ref[:,:,:3].max(2)>12)
model=np.array(Image.open(ROOT/('build/bishop-mission/137-upper-collar-underside/wood.png' if a.mode=='stem' else 'assets/bishop/render.png')).convert('RGBA'))[:,:,3]>127
ys=np.arange(606,628,1,dtype=float) if a.mode=='stem' else np.arange(610,795,2,dtype=float)
target=[];actual=[]
for y in ys.astype(int):
    x=np.flatnonzero(mask[y]);target.append((x[-1]-x[0]+1)/2)
    x=np.flatnonzero(model[y]);actual.append((x[-1]-x[0]+1)/2)
target=np.array(target);actual=np.array(actual)

def subdivide(pro):
    smooth=pro.copy()
    smooth[1:-1]=(.125*pro[:-2]+.75*pro[1:-1]+.125*pro[2:])
    mid=(pro[:-1]+pro[1:])/2
    q=np.empty((len(pro)*2-1,2));q[::2]=smooth;q[1::2]=mid
    t=np.linspace(0,1,12,endpoint=False)
    return (q[:-1,None,:]*(1-t[None,:,None])+q[1:,None,:]*t[None,:,None]).reshape(-1,2)

def outline(pro):
    q=subdivide(pro[:65]);r=q[:,0]*F;cy=(q[:,1]-al['y']*3)*F
    rr=r[None,:]**2-((ys[:,None]-cy[None,:])/sn)**2
    return np.sqrt(np.maximum(rr,0)).max(1)

indices=np.arange(32,38) if a.mode=='stem' else np.arange(17,24) if a.mode=='radial' else np.arange(15,23)
start=profile[indices,0].copy() if a.mode!='shoulder-height' else np.r_[profile[indices,0],profile[indices,1]]
base_pred=outline(profile)
# Correct only the subpixel approximation bias measured against the actual
# baseline render, rather than pretending this proxy is an exact renderer.
bias=actual-base_pred
def proposed(v):
    q=profile.copy()
    if a.mode!='shoulder-height':q[indices,0]=v
    else:q[indices,0]=v[:len(indices)];q[indices,1]=v[len(indices):]
    return q
def residual(v):
    q=proposed(v)
    if a.mode!='shoulder-height':
        regularity=np.r_[.65*(v-start), 2*np.diff(v-start,2)]
        if a.mode=='stem':regularity=np.r_[regularity,30*np.minimum(q[31:36,0]-q[32:37,0],0)]
        if a.mode=='radial-smooth':
            d=np.diff(q[13:24],axis=0)
            angles=np.arctan2(-d[:,0],-d[:,1]/math.cos(math.radians(54)))
            regularity=np.r_[regularity,35*np.minimum(np.diff(angles),0),5*np.diff(angles,2)]
    else:
        d=(v-start).reshape(2,-1)
        regularity=np.r_[1.1*d.ravel(), 2*np.diff(d,2).ravel(),
                         30*np.minimum(q[14:23,1]-q[15:24,1]-.2,0),
                         15*np.minimum(q[14:23,0]-q[15:24,0],0)]
    return np.r_[outline(q)+bias-target,regularity]

v=start.copy();trace=[]
for step in range(25):
    e=residual(v);J=np.stack([(residual(v+np.eye(len(v))[i]*.035)-e)/.035 for i in range(len(v))],axis=1)
    delta=np.linalg.solve(J.T@J+np.eye(len(v))*.4,-J.T@e)
    found=False
    for scale in [1,.5,.25,.125,.0625]:
        candidate=np.clip(v+delta*scale,start-4,start+4)
        if a.mode=='stem':candidate[0]=min(candidate[0],24.5)
        if np.linalg.norm(residual(candidate))<np.linalg.norm(e)-1e-7:
            v=candidate;found=True;break
    trace.append(float(np.mean(abs(residual(v)[:len(ys)]))))
    if not found:break
proposal=proposed(v)
spec={'variant':{'radial':'135-lower-shoulder-fit','shoulder-height':'136-shoulder-height-fit','stem':'139-constrained-stem-fit','radial-smooth':'141-rounded-shoulder-fit'}[a.mode],'source':'history/bishop-mission-015/bishop-rebuilt.blend',
      'source_sha256':hashlib.sha256((ROOT/'history/bishop-mission-015/bishop-rebuilt.blend').read_bytes()).hexdigest(),
      'profile':'history/bishop-mission-015/profile.json','samples':128,
      'body_rings':{str(i):[round(float(proposal[i,0]),5),float(proposal[i,1])] for i in indices},
      'interpretation':'Fit the raised rear shoulder to the original white outline using declared local profile controls. All unlisted controls, socket, stem, collars, head, button, slit, finish and 54-degree camera remain fixed. Analytical fit is a proposal, not acceptance.'}
if base_spec:spec['body_rings']={**base_spec['body_rings'],**spec['body_rings']}
prefix={'radial':'shoulder-fit','shoulder-height':'shoulder-height-fit','stem':'stem-fit','radial-smooth':'rounded-shoulder-fit'}[a.mode]
(out/(prefix+'.json')).write_text(json.dumps(spec,indent=2)+'\n')
report={'method':'Original-white fixed-registration horizontal outline, local profile controls only; native-render bias measured on baseline; damped finite-difference least squares with bounded changes and regularization.',
 'rows':ys.tolist(),'target_original_half_width':target.tolist(),'baseline_render_half_width':actual.tolist(),
 'predicted_candidate_half_width':(outline(proposal)+bias).tolist(),
 'baseline_mean_abs_half_width_error':float(np.mean(abs(actual-target))),
 'proposal_mean_abs_half_width_error':float(np.mean(abs(outline(proposal)+bias-target))),
 'baseline_proxy_bias_mean_abs':float(np.mean(abs(bias))),'trace':trace,'proposal':spec}
(out/(prefix+'-report.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['rows','target_original_half_width','baseline_render_half_width','predicted_candidate_half_width']},indent=2))
