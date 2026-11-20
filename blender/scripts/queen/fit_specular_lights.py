"""Fit warm reflection strengths independently of the accepted diffuse lighting."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--variant',default='043-highlights-fit');p.add_argument('--highlight-weight',type=float,default=16);p.add_argument('--directory',default='build/queen-mission/specular-fit-039');args=p.parse_args();out=ROOT/args.directory
m=json.loads((out/'manifest.json').read_text());specs=m['specs']
reference=np.load(ROOT/'build/queen-mission/pigment-fit-033/reference-linear.npy').reshape(418,3,418,3,3).mean((1,3))
# Artistic two-color decomposition: warm brown diffuse + warm cream reflection.
# These vectors are hypotheses, not recovered source illuminants or reflectance.
d=np.array([1,.23,.08]);c=np.array([1,.58,.4]);dc=np.column_stack((d,c))
components=reference@np.linalg.pinv(dc).T
target=np.maximum(components[:,:,1],0)
responses=[np.load(out/(s['name']+'.npy')) for s in specs]
mask=responses[0][:,:,3]>.995
bases=np.stack([a[:,:,:3].mean(2)[mask] for a in responses],axis=1)
y=target[mask];weight=np.sqrt(1+args.highlight_weight*y/(y+.08))/np.sqrt(.03+y)
X=bases*weight[:,None];yw=y*weight
scale=np.linalg.norm(X,axis=0);scale=np.maximum(scale,1e-9);A=X/scale
gram=A.T@A+np.eye(len(specs))*.0001;rhs=A.T@yw;x=np.zeros(len(specs))
world=next(i for i,s in enumerate(specs) if s['name']=='world')
upper=np.full(len(specs),np.inf);upper[world]=0 # Keep the accepted world; avoid an additional reflective veil.
for iteration in range(6000):
 old=x.copy()
 for i in range(len(x)):x[i]=min(upper[i],max(0,x[i]+(rhs[i]-gram[i]@x)/gram[i,i]))
 if np.max(abs(x-old))<1e-8:break
factors=x/scale;prediction=bases@factors
accepted=json.loads((ROOT/'build/queen-mission/026-graded-atlas/parameters.json').read_text())
lights=[]
for light in accepted['lights']:
 v=dict(light);v['name']='Diffuse '+v['name'];v['specular_factor']=0;lights.append(v)
for spec,factor in zip(specs,factors):
 if 'position' not in spec or factor<1e-5:continue
 v=dict(spec);v['name']='Warm reflection '+v['name'];v['energy']=float(v['energy']*factor);v['diffuse_factor']=0;v['color']=c.tolist();lights.append(v)
cfg={'variant':args.variant,'source':m['source'].replace(chr(92),'/'),'samples':96,'world':accepted['world'],'lights':lights,'cycles_ray_visibility':True,'method':'Art-directed warm specular lights fitted independently; accepted white diffuse light rig retained','source_sha256':m['source_sha256'],'diffuse_chromaticity':d.tolist(),'specular_chromaticity':c.tolist(),'highlight_weight':args.highlight_weight}
(out/(args.variant+'-config.json')).write_text(json.dumps(cfg,indent=2)+'\n')
report={'foreground_pixels':int(mask.sum()),'iterations':iteration+1,'highlight_weight':args.highlight_weight,'weighted_rmse':float(np.sqrt(np.mean(((prediction-y)*weight)**2))),'factors':{s['name']:float(f) for s,f in zip(specs,factors)},'reference_sha256':hashlib.sha256((ROOT/'assets/queen/reference.png').read_bytes()).hexdigest(),'caveat':'Subjective chromatic separation of unknown source shading; actual full BSDF render and visual inspection required.'}
(out/(args.variant+'-report.json')).write_text(json.dumps(report,indent=2)+'\n')
pred=np.zeros_like(target);pred[mask]=prediction
for name,a in [('target-specular',target),('predicted-specular',pred)]:
 np.save(out/(args.variant+'-'+name+'.npy'),a);v=np.clip(a,0,1)**(1/2.2);Image.fromarray(np.uint8(v*255)).save(out/(args.variant+'-'+name+'.png'))
print(json.dumps(report,indent=2))
