"""Nonnegative least-squares light energies from physically rendered basis images."""
from pathlib import Path
import argparse,json
import numpy as np
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'build/queen-mission/light-fit'
p=argparse.ArgumentParser();p.add_argument('--variant',default='032-fitted-lights');p.add_argument('--max-world',type=float);args=p.parse_args()
manifest=json.loads((out/'manifest.json').read_text());target=np.load(out/'reference-linear.npy');srgb=np.load(out/'reference-srgb.npy')
basis=[np.load(out/(s['name']+'.npy')) for s in manifest['specs']]
mask=(basis[0][:,:,3]>.995)&(srgb.max(2)>.05)
# Relative radiometric error, with extra weight on pale highlights and equalized
# major height regions, avoids rewarding black background or only the large base.
weight=1/np.sqrt(.025+np.maximum(0,target.mean(2)))
weight*=np.where(srgb.min(2)>.25,1.5,1)
for lo,hi in [(0,120),(120,190),(190,275),(275,418)]:
 count=mask[lo:hi].sum();weight[lo:hi]*=np.sqrt(mask.sum()/max(1,count)/4)
a=np.stack([b[:,:,:3][mask].reshape(-1) for b in basis],axis=1).astype(np.float64)
y=target[mask].reshape(-1).astype(np.float64);w=np.repeat(weight[mask],3);a*=w[:,None];y*=w
scale=np.linalg.norm(a,axis=0);scale=np.maximum(scale,1e-10);a/=scale
gram=a.T@a;rhs=a.T@y;gram+=np.eye(len(scale))*.0001
x=np.zeros(len(scale))
upper=np.full(len(scale),np.inf)
if args.max_world is not None:
 for j,spec in enumerate(manifest['specs']):
  if 'world' in spec:upper[j]=scale[j]*args.max_world/spec['world']
for iteration in range(6000):
 old=x.copy()
 for j in range(len(x)):x[j]=min(upper[j],max(0,x[j]+(rhs[j]-gram[j]@x)/gram[j,j]))
 if np.max(np.abs(x-old))<1e-7:break
factors=x/scale
cfg={'source':'models/queen/queen-rebuilt.blend','variant':args.variant,'world':0,'lights':[]}
for factor,spec in zip(factors,manifest['specs']):
 if 'world' in spec:cfg['world']=round(float(spec['world']*factor),6)
 elif factor>1e-5:
  light=dict(spec);light['energy']=round(float(light['energy']*factor),4);cfg['lights'].append(light)
previous=np.zeros(len(factors));previous[:3]=1;previous[-1]=.3
prediction=sum(float(f)*b[:,:,:3] for f,b in zip(factors,basis))
np.save(out/'predicted-linear.npy',prediction)
report={'source_sha256':manifest['source_sha256'],'method':'Nonnegative least squares on scene-linear single-light renders; actual full render still required','fit_pixels':int(mask.sum()),'iterations':iteration+1,'weights':dict(zip([s['name'] for s in manifest['specs']],map(float,factors))),'weighted_linear_rmse':float(np.sqrt(np.mean((a@x-y)**2))),'previous_rig_weighted_linear_rmse':float(np.sqrt(np.mean((a@(previous*scale)-y)**2))),'config':cfg}
(out/'fit-report.json').write_text(json.dumps(report,indent=2)+'\n');(out/'fitted-config.json').write_text(json.dumps(cfg,indent=2)+'\n')
print(json.dumps(report,indent=2))
