"""Propose a small upper refit using the fixed original-white outline and collar arcs.

Run after the shorter 'moderate' trial. The proxy has one subdivision pass,
calibrated to the actual saved trial. Render the proposal before accepting it.
"""
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/'assets/bishop'
BUILD=ROOT/'build/bishop-mission'
stage=BUILD/'turning-moderate'
config=json.loads((ROOT/'docs/bishop-mission/iteration-025/turning.json').read_text())
q=json.loads((ASSETS/'original-alignment.json').read_text())
F=1254/300/q['scale']
unit=F/260
sine=math.sin(math.radians(54))
cosine=math.cos(math.radians(54))
s=q['scale']*300/1254
im=Image.open(ASSETS/'original.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,
    (s,0,3*q['x'],0,s,3*q['y']),Image.Resampling.BILINEAR)
raw=np.array(im)
sprite=(raw[:,:,3]>127)&(raw[:,:,:3].max(2)>12)
render=np.array(Image.open(stage/'wood.png'))[:,:,3]>127
profile=json.loads((stage/'profile.json').read_text())
source=np.array(profile['profile'])
button=np.array(profile['finial']['profile'])
yy=np.arange(178,627,3)
def width(mask):
    return np.array([(np.flatnonzero(mask[y])[-1]-np.flatnonzero(mask[y])[0]+1)/2 for y in yy])

def subdivide(p):
    mid=(p[1:]+p[:-1])/2
    smooth=p.copy()
    smooth[1:-1]=(p[:-2]+6*p[1:-1]+p[2:])/8
    res=np.empty((len(p)+len(mid),2))
    res[::2]=smooth
    res[1::2]=mid
    t=np.arange(12)[None,:,None]/12
    return (res[:-1,None,:]*(1-t)+res[1:,None,:]*t).reshape(-1,2)

def outline(body,cap):
    sec=np.vstack([subdivide(body),subdivide(cap)])
    r=sec[:,0]*F
    cy=(sec[:,1]-3*q['y'])*F
    return np.sqrt(np.maximum(r*r-((yy[:,None]-cy)/sine)**2,0)).max(axis=1)

# Modes follow the original bishop ring numbers above the donor's first
# support. Keep the closed head/button junction and saw unchanged locally.
idx=np.arange(len(source))-7
modes=[
 ([33,35,37,39],[0,1,.35,0]),                    # stem waist
 ([40,43,46,48],[0,1,1,0]),                      # lower collar radius
 ([49,52,54,57],[0,1,1,0]),                      # middle collar radius
 ([59,62,64,65],[0,1,.4,0]),                     # upper collar radius
 ([65,70,74,79,85],[0,.55,1,.6,0]),              # lower mitre curvature
 ([76,83,90,97,103],[0,.5,1,.45,0]),             # upper mitre curvature
]
W=np.stack([np.interp(idx,ns,vs,left=0,right=0) for ns,vs in modes],axis=1)
mode_head=np.interp(idx,[62,65],[0,1])
case0=config['cases']['moderate']
head_drop=.020
collar_drop=.013
old=np.array(json.loads((ROOT/config['profile']).read_text())['profile'])
old_z=(profile['y0']-old[:,1])*unit/cosine
t=np.clip((old_z[33:]-old_z[32])/(old_z[39]-old_z[32]),0,1)
collar_weight=np.r_[np.zeros(40),t*t*(3-2*t)]
body=source.copy()
body[:,1]+=(cosine/unit)*((collar_drop-case0['collar_drop'])*collar_weight+
      ((head_drop-case0['head_drop'])-(collar_drop-case0['collar_drop']))*mode_head)
cap=button.copy()
cap[:,1]+=(head_drop-case0['head_drop'])*cosine/unit
cap_drop=.022
cap[:,1]+=cap_drop*cosine/unit*np.array([0,0,0,0,0,0,0,0,.12,.55,.93,1])
native_bias=width(render)-outline(source,button)
target=width(sprite)
# The dark troughs follow the projected physical edge. Use a small interval
# above each trough to allow for the displaced optical shadow in the sprite.
crest_targets=np.array([512.,566.5,610.])
def crests(p):
    out=[]
    for start,end in [(59,65),(50,57),(41,48)]:
        patch=subdivide(p[start+7-1:end+7+2])
        v=(patch[:,1]+sine*patch[:,0]-3*q['y'])*F
        # restrict the search so a neighbouring collar's valley cannot take it
        keep=(patch[:,1]>=p[end+7,1])&(patch[:,1]<=p[start+7,1])
        out.append(v[keep].max())
    return np.array(out)
# Calibrate the analytic arcs with the previously measured evaluated crests.
prior_crests=np.array([510.905850,564.581098,607.785353])
old_proxy=np.vstack([np.zeros((7,2)),old])
crest_bias=prior_crests-crests(old_proxy)
def residual(x):
    p=body.copy()
    p[:,0]+=W@x
    return np.r_[outline(p,cap)+native_bias-target,(crests(p)+crest_bias-crest_targets)*2.5,5*x]
x=np.zeros(len(modes))
start=float(np.abs(residual(x)[:len(yy)]).mean())
for i in range(20):
    r=residual(x)
    jac=np.stack([(residual(x+step*.035)-r)/.035 for step in np.eye(len(x))],axis=1)
    delta=np.linalg.solve(jac.T@jac+np.eye(len(x))*.6,-jac.T@r)
    for multiplier in [1,.5,.25,.125,.0625]:
        trial=np.clip(x+delta*multiplier,-1.0,1.0)
        if np.linalg.norm(residual(trial))<np.linalg.norm(r)-1e-7:
            x=trial
            break
    else:
        break
dr=W@x*unit
edits={str(i-7):[0.,round(float(d),7)] for i,d in enumerate(dr) if abs(d)>1e-6}
case={'donor_scale':case0['donor_scale'],'head_drop':head_drop,'collar_drop':collar_drop,
      'cap_drop':cap_drop,'upper_edits':edits}
report={'case':case,'mode_amplitudes_original_units':x.tolist(),'old_trial':'moderate',
        'target_original_white':True,'approx_upper_halfwidth_mae_px_before':start,
        'approx_upper_halfwidth_mae_px_after':float(np.abs(residual(x)[:len(yy)]).mean()),
        'collar_front_targets':crest_targets.tolist(),'predicted_crests':(residual(x)[len(yy):len(yy)+3]/2.5+crest_targets).tolist(),
        'note':'Fitting proxy; measured renders and interior features are assessed separately.'}
(BUILD/'turning-upper-proposal.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:v for k,v in report.items() if k!='case'})

# On a second pass fit the exposed stem only. Below row 615 the original
# starts showing the rear of its base, while the lower shared flare exposes
# more stem. Treating those rows as evidence for a thicker stem biases it.
refit=BUILD/'turning-refit'
if (refit/'wood.png').exists():
    from copy import deepcopy
    p2=json.loads((refit/'profile.json').read_text())
    sec=np.array(p2['profile'])
    cap2=np.array(p2['finial']['profile'])
    actual=np.array(Image.open(refit/'wood.png'))[:,:,3]>127
    exposed=(yy>=595)&(yy<=614)
    native=width(actual)
    bias=native-outline(sec,cap2)
    choices=[]
    for change in np.linspace(-1.6,.3,77):
        candidate=sec.copy()
        candidate[:,0]+=W[:,0]*change
        edges=outline(candidate,cap2)+bias
        mse=np.mean((edges[exposed]-target[exposed])**2)
        choices.append((float(mse+.16*change**2),float(change),float(np.abs(edges[exposed]-target[exposed]).mean())))
    _,change,mae=min(choices)
    final=deepcopy(config['cases']['refit'])
    for row in np.flatnonzero(W[:,0]):
        key=str(row-7)
        dz,dr=final['upper_edits'].get(key,[0.,0.])
        final['upper_edits'][key]=[dz,round(dr+unit*W[row,0]*change,7)]
    audit={'case':final,'stem_change_original_units':change,'rows':yy[exposed].tolist(),
           'actual_halfwidth_mae_before':float(abs(native[exposed]-target[exposed]).mean()),
           'predicted_halfwidth_mae_after':mae}
    (BUILD/'turning-stem-proposal.json').write_text(json.dumps(audit,indent=2)+'\n')
    print({k:v for k,v in audit.items() if k!='case'})
