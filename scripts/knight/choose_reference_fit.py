"""Choose uniform camera framing on a fixed five-yaw grid; geometry is unchanged."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[2];a=root/'assets/knight';out=a/'reference-fit';N=300;F=600
placement=json.loads((a/'original-alignment.json').read_text());s=placement['scale'];x=placement['x'];y=placement['y']
orig=Image.open(a/'original.png').convert('RGBA').transform((N,N),Image.Transform.AFFINE,(s,0,x*3,0,s,y*3),Image.Resampling.BILINEAR)
ar=np.asarray(orig);target=((ar[:,:,3]>128)&(ar[:,:,:3].max(2)>12)).astype(float);area=target.sum();tf=np.fft.rfft2(target,s=(F,F))
shifts=np.arange(-24,25);idx=shifts%F;rows=[]
for yaw in [-12,-6,0,6,12]:
 image=Image.open(out/f'yaw-{yaw:+d}.png').convert('RGBA').getchannel('A')
 best=None
 for scale in np.linspace(.92,1.12,41):
  im=image.transform((N,N),Image.Transform.AFFINE,(2/scale,0,300-300/scale,0,2/scale,300-300/scale),Image.Resampling.BILINEAR)
  m=(np.asarray(im)>128).astype(float)
  corr=np.fft.irfft2(tf*np.conj(np.fft.rfft2(m,s=(F,F))),s=(F,F))
  vals=corr[np.ix_(idx,idx)];iy,ix=np.unravel_index(np.argmax(vals),vals.shape);inter=vals[iy,ix];iou=inter/(area+m.sum()-inter)
  result={'yawDegrees':yaw,'scale':float(scale),'dxPixels1254':float(shifts[ix]*1254/N),'dyPixels1254':float(shifts[iy]*1254/N),'originalSilhouetteIoU300':float(iou)}
  if best is None or iou>best['originalSilhouetteIoU300']:best=result
 rows.append(best)
best=max(rows,key=lambda r:r['originalSilhouetteIoU300'])
report={'method':'Five fixed yaw angles at 54 degree elevation; 41 uniform scales from 0.92 to 1.12; bounded image translations of +/-100 pixels at 1254 resolution. FFT mask overlap at 300 resolution proposes framing only. Final rendered 1254 image is checked separately. Geometry, source images and source registration are unchanged.','candidates':rows,'best':best,'frozenReferenceMetrics':json.loads((a/'qa.json').read_text())}
(out/'fit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
