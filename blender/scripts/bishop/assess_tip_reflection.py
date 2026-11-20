"""Measure the actual tip highlight and off-target changes at fixed registration."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--render',required=True);p.add_argument('--out',required=True)
p.add_argument('--baseline',default='history/bishop-mission-006/render.png')
a=p.parse_args()
ref=np.asarray(Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA')).astype(float)
old=np.asarray(Image.open(ROOT/a.baseline).convert('RGBA')).astype(float)
new=np.asarray(Image.open(ROOT/a.render).convert('RGBA')).astype(float)
yy,xx=np.mgrid[:ref.shape[0],:ref.shape[1]]
foreground=(ref[:,:,3]>127)&(old[:,:,3]>254)&(new[:,:,3]>254)&(ref[:,:,:3].max(2)>12)
tip=(((xx-497)/15)**2+((yy-430)/12)**2<1)&foreground
core=tip&(ref[:,:,1]>245)
context=(xx>445)&(xx<560)&(yy>390)&(yy<475)
outside=foreground&~context
delta=np.abs(new[:,:,:3]-old[:,:,:3]);values={}
for name,mask in [('tip',tip),('reference_bright_core',core),('all_foreground',foreground)]:
    values[name]={'pixels':int(mask.sum()),'reference_mean_rgb':ref[:,:,:3][mask].mean(0).tolist(),
                 'previous_mean_rgb':old[:,:,:3][mask].mean(0).tolist(),'current_mean_rgb':new[:,:,:3][mask].mean(0).tolist(),
                 'previous_mean_rgb_error':float(np.abs(old[:,:,:3][mask]-ref[:,:,:3][mask]).mean()),
                 'current_mean_rgb_error':float(np.abs(new[:,:,:3][mask]-ref[:,:,:3][mask]).mean())}
result={'render':a.render,'baseline':a.baseline,'regions':values,'outside_tip_context':{
 'pixels':int(outside.sum()),'mean_absolute_rgb_change':float(delta[outside].mean()),
 'p99_absolute_channel_change':float(np.quantile(delta[outside],.99)),
 'maximum_channel_change':float(delta[outside].max()),'pixels_with_any_channel_change_over_5':int((delta.max(2)[outside]>5).sum())},
 'note':'Native 8-bit values at fixed registration. Small off-target changes can reflect Monte Carlo sampling/denoising. These diagnostics do not replace actual image inspection.'}
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
