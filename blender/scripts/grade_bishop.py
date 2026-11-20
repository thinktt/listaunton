"""Fit global RGB curves to the aligned original; never resample output pixels."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
items=json.loads((root/'assets/candidates/alignment.json').read_text())['pieces']['bishop']
src=next(v for v in items if v['id']=='white-candidate-3');ref=next(v for v in items if v['id']=='white')
def sample(item):
 a=np.array(Image.open(root/item['file']).convert('RGBA').resize((600,600),Image.Resampling.BILINEAR),float)/255
 y,x=np.indices((300,300));sx=(x-item['x']*3)/item['scale']*2;sy=(y-item['y']*3)/item['scale']*2
 ix=np.clip(sx.astype(int),0,598);iy=np.clip(sy.astype(int),0,598);fx=np.clip(sx-ix,0,1)[...,None];fy=np.clip(sy-iy,0,1)[...,None]
 return (a[iy,ix]*(1-fx)+a[iy,ix+1]*fx)*(1-fy)+(a[iy+1,ix]*(1-fx)+a[iy+1,ix+1]*fx)*fy
s=sample(src);t=sample(ref)
mask=(s[:,:,3]>.98)&(t[:,:,3]>.98)&(s[:,:,:3].max(2)>.22)&(t[:,:,:3].max(2)>.22)&(s[:,:,:3].max(2)<.85)&(t[:,:,:3].max(2)<.85)
gamma=np.clip(np.median(np.log(np.maximum(t[:,:,:3][mask],.02))/np.log(np.maximum(s[:,:,:3][mask],.02)),axis=0),.75,1.4)
a=np.array(Image.open(root/src['file']).convert('RGBA'));out=a.copy();out[:,:,:3]=np.round(255*(a[:,:,:3]/255.)**gamma).astype('uint8')
dest=root/'assets/candidates/bishop/white-candidate-4-direct-grade.png';Image.fromarray(out).save(dest)
assert np.array_equal(out[:,:,3],a[:,:,3])
report={'source':src['file'],'reference':ref['file'],'gamma_rgb':gamma.tolist(),'method':'Median per-channel log-ratio fit on aligned opaque midtones; global monotonic RGB curves only. Output is not resampled.','alpha_unchanged':True,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
(dest.parent/'white-color-grade.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
