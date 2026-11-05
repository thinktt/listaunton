"""Repair two bounded pigment marks exposed by the corrected socket lights."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=ROOT/'build/queen-mission/socket-pigment-136';m=json.loads((p/'manifest.json').read_text())
source=ROOT/'build/queen-mission/136-fitted-socket-crescent/queen.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()==m['source_sha256']
x1,y1,x2,y2=m['crop'];pigment=np.load(p/'pigment-only.npy')[:,:,:3];h,w=pigment.shape[:2]
yy,xx=np.indices((h,w));mask=np.zeros((h,w),dtype=bool)
ellipses=[{'center':[528,695],'radii':[19,22]},{'center':[567,765],'radii':[22,14]}]
for e in ellipses:
    cx,cy=e['center'];rx,ry=e['radii'];mask|=((xx+x1-cx)/rx)**2+((yy+y1-cy)/ry)**2<1
log=np.log(np.maximum(pigment,.0001));flat=log.copy().reshape(-1,3);idx=np.flatnonzero(mask.reshape(-1))
boundary=(blur(mask.astype(np.float32),r=3,passes=1)>.001)&~mask;flat[idx]=np.median(log[boundary],axis=0)
for iteration in range(2500):
    new=(flat[idx-w]+flat[idx+w]+flat[idx-1]+flat[idx+1])*.25
    change=float(abs(new-flat[idx]).max());flat[idx]=new
    if iteration>100 and change<.00001:break
reference=np.asarray(Image.open(ROOT/'assets/queen/reference.png').convert('RGB'),dtype=np.float32)/255
ref=reference[y1:y2,x1:x2];luma=ref@np.array([.2126,.7152,.0722],dtype=np.float32)
fine=np.log(luma+.003);fine=np.clip(fine-blur(fine,r=3,passes=1),-.25,.25)
height=np.log(np.load(p/'relief-height.npy')[:,:,0]+.03)
medium=np.clip(blur(height,r=2,passes=1)-blur(height,r=12,passes=2),-.25,.25)
repair=np.exp(flat.reshape(h,w,3))*np.exp(fine*.7+medium)[:,:,None]
H,W=reference.shape[:2];field=np.zeros((H,W,3),dtype=np.float32);confidence=np.zeros((H,W),dtype=np.float32)
field[y1:y2,x1:x2]=repair;confidence[y1:y2,x1:x2]=blur(mask.astype(np.float32),r=2,passes=1)
out=ROOT/'build/queen-mission/socket-pigment-repair-136';out.mkdir(parents=True,exist_ok=True)
np.save(out/'pigment.npy',field);np.save(out/'confidence.npy',confidence)
config={'source_sha256':m['source_sha256'],'crop':m['crop'],'ellipses':ellipses,'mask_pixels':int(mask.sum()),
 'harmonic_iterations':iteration+1,'last_log_color_change':change,'fine_grain_strength':.7,'medium_grain_strength':1,
 'method':'Fill only the two exposed pigment imprints from adjacent log wood color; add bounded fine reference grain and medium relief-field variation. Preserve surrounding pigment and existing hidden-surface coverage.'}
(out/'parameters.json').write_text(json.dumps(config,indent=2)+'\n');print(json.dumps(config),flush=True)
