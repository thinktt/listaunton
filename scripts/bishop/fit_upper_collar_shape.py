"""Fit a single coupled collar radius/height parameter to the original outline.

This proposes a real surface change. Keeping y + r*sin(54) fixed holds the
front meridian in place while correcting the back/side bulge. The saved mesh,
neutral render and side view, not this analytical proxy, decide acceptance.
"""
from pathlib import Path
import argparse,hashlib,json,math,shutil
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--region',choices=['upper','middle'],default='upper');a=p.parse_args()
out=ROOT/'build/bishop-mission/144-surface-audit';out.mkdir(parents=True,exist_ok=True)
archive=ROOT/'history/bishop-mission-017';archive.mkdir(exist_ok=True)
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
for original,name in [('models/bishop/bishop-rebuilt.blend','bishop-rebuilt.blend'),('scripts/bishop/profile.json','profile.json')]+[
        ('assets/bishop/'+name,name) for name in ['render.png','render-clay.png','side-profile.png','head-side.png','rear-oblique.png','camera.json','mesh.json','mesh.bin','bishop-boxwood-albedo.png']]:
    target=archive/name
    if target.exists():assert sha(target)==sha(ROOT/original),name
    else:shutil.copy2(ROOT/original,target)
cfg=json.loads((archive/'profile.json').read_text());profile=np.array(cfg['profile'],dtype=float)
al=json.loads((ROOT/'assets/bishop/original-alignment.json').read_text());F=1254/300/al['scale'];sn=math.sin(math.radians(54))
source=Image.open(ROOT/'assets/bishop/original.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,
    (al['scale']*300/1254,0,al['x']*3,0,al['scale']*300/1254,al['y']*3),Image.Resampling.BILINEAR)
ar=np.array(source);mask=(ar[:,:,3]>127)&(ar[:,:,:3].max(2)>12)
model=np.array(Image.open(archive/'render.png').convert('RGBA'))[:,:,3]>127
ys=np.arange(340,516,2,dtype=float)
def widths(m):
    return np.array([(np.flatnonzero(m[int(y)])[-1]-np.flatnonzero(m[int(y)])[0])/2 for y in ys])
target=widths(mask);actual=widths(model)
weights={58:.25,59:.7,60:1,61:1,62:1,63:1,64:.7,65:.3} if a.region=='upper' else {49:.3,50:.7,51:1,52:1,53:1,54:1,55:.7,56:.3}
def proposed(delta):
    q=profile.copy()
    for i,w in weights.items():q[i,0]+=delta*w;q[i,1]-=sn*delta*w
    return q
def predicted(pro):
    smooth=pro.copy();smooth[1:-1]=.125*pro[:-2]+.75*pro[1:-1]+.125*pro[2:]
    q=np.empty((len(pro)*2-1,2));q[::2]=smooth;q[1::2]=(pro[:-1]+pro[1:])/2
    t=np.linspace(0,1,16,endpoint=False);q=(q[:-1,None,:]*(1-t[None,:,None])+q[1:,None,:]*t[None,:,None]).reshape(-1,2)
    r=q[:,0]*F;center=(q[:,1]-al['y']*3)*F
    sq=r[None,:]**2-((ys[:,None]-center[None,:])/sn)**2
    predicted.indices=np.argmax(sq,axis=1)/32
    return np.sqrt(np.maximum(sq,0)).max(1)
bias=actual-predicted(profile)
controlling_indices=predicted.indices.copy()
def error(delta):return predicted(proposed(delta))+bias-target
grid=np.linspace(-2.5,.5,121)
loss=[float(np.mean(error(d)**2)+.4*d*d) for d in grid]
best=float(grid[int(np.argmin(loss))]);q=proposed(best)
config={'variant':'145-upper-collar-neck' if a.region=='upper' else '146-middle-collar-neck','source':'history/bishop-mission-017/bishop-rebuilt.blend',
    'source_sha256':sha(archive/'bishop-rebuilt.blend'),'profile':'history/bishop-mission-017/profile.json','samples':128,
    'body_rings':{str(i):q[i].tolist() for i in weights},
    'interpretation':f'Narrow and lower the {a.region} collar with a weighted single parameter while pinning its front-meridian y+r*sin(54). Correct the side/back neck bulge against the original; preserve all other controls, material, lights and reference camera.'}
(out/(a.region+'-collar-neck-fit.json')).write_text(json.dumps(config,indent=2)+'\n')
report={'fit_rows':[340,516,2],'parameter_delta_radius_original_units':best,
    'front_meridian_pinned_by_construction':True,'before_mae':float(np.mean(abs(error(0)))),
    'predicted_mae':float(np.mean(abs(error(best)))),'parameter_grid':grid.tolist(),'loss':loss,
    'note':'Analytical profile proposal, calibrated to the current rendered outline; not a rendered improvement claim.'}
report['largest_original_discrepancies']=[{'row':float(ys[i]),'half_width_error':float(actual[i]-target[i]),'controlling_profile_index':float(controlling_indices[i])}
    for i in np.argsort(abs(actual-target))[-12:]]
(out/(a.region+'-collar-neck-fit-report.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['parameter_grid','loss']},indent=2))
