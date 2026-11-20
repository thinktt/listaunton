"""Fit one confined reflector's power using actual on/off BSDF renders.

Predictions are diagnostics only. Render the resulting configuration before
acceptance; clipping, denoising and finite samples limit this fit.
"""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
from image_math import blur
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--on',required=True);p.add_argument('--off',required=True)
p.add_argument('--config',required=True);p.add_argument('--out',required=True);a=p.parse_args()
def load(path):return np.array(Image.open(ROOT/path).convert('RGB'),dtype=np.float32)/255
def linear(x):return np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
def srgb(x):return np.where(x<=.0031308,12.92*x,1.055*np.maximum(x,0)**(1/2.4)-.055)
ref=load('assets/bishop/reference.png');on=load(a.on);off=load(a.off)
b=blur(linear(off),2);delta=blur(linear(on)-linear(off),2)
# Keep only the lower base/foot; the lamp has no intended upper-piece role.
box=np.s_[920:1090,500:670];r=blur(ref,2)[box];b=b[box];delta=delta[box]
w=np.ones(r.shape[:2],dtype=np.float32);w[110:]*=2
bright=(r[:,:,2]>.70)&(np.indices(w.shape)[0]<110);w[bright]*=4
def loss(factor):
    predicted=np.clip(srgb(np.maximum(b+delta*factor,0)),0,1)
    return float((np.abs(predicted-r).mean(2)*w).sum()/w.sum())
factors=np.linspace(0,12,601);losses=np.array([loss(float(f)) for f in factors]);best=float(factors[losses.argmin()])
cfg=json.loads((ROOT/a.config).read_text());lamp=cfg['lights'][0]
response_manifest=(ROOT/a.on).parent/'manifest.json'
response_samples=json.loads(response_manifest.read_text()).get('samples') if response_manifest.exists() else None
record={'note':'Predicted fit from actual on/off BSDF passes, not a rendered result or fidelity score. Power only; geometry, material and beam stay fixed.',
 'measured_samples':response_samples,
 'on':a.on,'off':a.off,'fit_box':[500,920,670,1090],'core_weight':4,'foot_weight':2,
 'old_power':lamp['energy'],'power_factor':best,'new_power':lamp['energy']*best,
 'weighted_predicted_rgb_mae_before':loss(1)*255,'weighted_predicted_rgb_mae_after':loss(best)*255,
 'factors_and_errors':[[float(v),float(l)*255] for v,l in zip(factors[::25],losses[::25])]}
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k!='factors_and_errors'},indent=2))
