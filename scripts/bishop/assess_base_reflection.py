"""Measure fixed-image base-reflection changes; these are not fidelity scores."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent));from image_math import blur
p=argparse.ArgumentParser();p.add_argument('--render',required=True);p.add_argument('--previous',required=True);p.add_argument('--out',required=True)
a=p.parse_args()
def read(path):return np.array(Image.open(ROOT/path).convert('RGBA'),dtype=float)
ref=read('assets/bishop/reference.png');old=read(a.previous);new=read(a.render)
mask=(ref[:,:,3]>127)&(ref[:,:,:3].max(2)>12)&(old[:,:,3]>254)&(new[:,:,3]>254)
mask=blur(mask.astype(np.float32),4)>.999
regions={'base':(230,850,755,1035),'foot':(220,1020,760,1120),'main_glint':(520,930,650,1020),'socket':(355,740,635,865),'upper_piece':(285,150,690,740)}
report={'note':'Fixed foreground RGB and bright-core diagnostics. They combine geometry, pigment and illumination; they do not replace visual assessment. Consult the render manifests for sample counts and acceptance status.', 'render':a.render,'previous':a.previous,'regions':{},'bright_core':{}}
for name,(x0,y0,x1,y1) in regions.items():
    sl=np.s_[y0:y1,x0:x1];m=mask[sl];d=np.abs(old[sl][:,:,:3]-new[sl][:,:,:3])[m]
    report['regions'][name]={'pixels':int(m.sum()),'before_rgb_mae':float(np.abs(old[sl][:,:,:3]-ref[sl][:,:,:3])[m].mean()),
     'after_rgb_mae':float(np.abs(new[sl][:,:,:3]-ref[sl][:,:,:3])[m].mean()),'mean_change':float(d.mean()),'p99_channel_change':float(np.percentile(d,99))}
box=np.s_[920:1030,500:670];r=ref[box][:,:,:3];bright=(r[:,:,2]>np.percentile(r[:,:,2],98))&mask[box]
for name,ar in [('reference',ref),('before',old),('after',new)]:
    v=ar[box][:,:,:3];core=v[:,:,2]>np.percentile(v[:,:,2],98);yy,xx=np.nonzero(core)
    report['bright_core'][name]={'own_blue_p98_centroid':[float(xx.mean()+500),float(yy.mean()+920)],
       'mean_rgb_on_reference_bright_core':v[bright].mean(0).tolist(),'rgb_error_on_reference_bright_core':float(np.abs(v[bright]-r[bright]).mean())}
report['bright_core_reference_mask_pixels']=int(bright.sum())
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
