"""Remove bounded negative reflection imprints from inferred wood pigment."""
from pathlib import Path
import numpy as np,json,hashlib,sys,argparse
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser();p.add_argument('--source',default='models/queen/queen-rebuilt.blend');p.add_argument('--only-finial',action='store_true');p.add_argument('--capture',default='surface-components-016');p.add_argument('--out',default='crown-pigment-repair-016');p.add_argument('--reference-grain',type=float,default=0);p.add_argument('--medium-grain',type=float,default=1);args=p.parse_args()
source=ROOT/args.source;data=ROOT/'build/queen-mission'/args.capture;manifest=json.loads((data/'manifest.json').read_text());digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==manifest['source_sha256']
x1,y1,x2,y2=345,115,620,285;crop=[x1,y1,x2,y2]
pigment=np.load(data/'pigment-only.npy')[y1:y2,x1:x2,:3];height=np.load(data/'relief-height.npy')[y1:y2,x1:x2,0]
reflection=np.asarray(Image.open(data/'reflection-only.png').convert('RGB'),dtype=np.float32)[y1:y2,x1:x2]/255
yy,xx=np.indices(pigment.shape[:2]);X=xx+x1;Y=yy+y1
finial=((X-483)/53)**2+((Y-211)/59)**2<1
bowl=(X>=364)&(X<=604)&(Y>=128)&(Y<=194)&~finial
if args.only_finial:bowl[:]=False
bright=reflection.min(2)>.12
mask=(blur((bright&(finial|bowl)).astype(np.float32),r=7,passes=1)>.001)&(finial|bowl)
mask[[0,-1],:]=False;mask[:,[0,-1]]=False
assert 100<mask.sum()<12000,int(mask.sum())
log=np.log(np.maximum(pigment,.0001));h,w=mask.shape;flat=log.copy().reshape(-1,3);idx=np.flatnonzero(mask.reshape(-1));boundary=(blur(mask.astype(np.float32),r=3,passes=1)>.001)&~mask
flat[idx]=np.median(log[boundary],axis=0)
for iteration in range(5000):
 new=(flat[idx-w]+flat[idx+w]+flat[idx-1]+flat[idx+1])*.25;change=float(abs(new-flat[idx]).max());flat[idx]=new
 if iteration>100 and change<.00001:break
grain=np.log(height+.03);medium=np.clip(blur(grain,r=2,passes=1)-blur(grain,r=11,passes=2),-.22,.22);fine=np.clip(grain-blur(grain,r=2,passes=1),-.20,.20)
extra=np.zeros_like(medium)
if args.reference_grain:
 reference=np.asarray(Image.open(ROOT/'assets/queen/reference.png').convert('RGB'),dtype=np.float32)[y1:y2,x1:x2]/255
 luma=reference@np.array([.2126,.7152,.0722],dtype=np.float32);log_luma=np.log(luma+.003)
 detail=np.clip(log_luma-blur(log_luma,r=2,passes=1),-.25,.25)
 highlights=blur((reference.min(2)>.4).astype(np.float32),r=5,passes=1)>.001
 extra=np.where(highlights,0,detail)*args.reference_grain
repair=np.exp(flat.reshape(h,w,3)+args.medium_grain*medium[:,:,None]+.35*fine[:,:,None]+extra[:,:,None])
full=np.load(data/'pigment-only.npy');H,W=full.shape[:2];field=np.zeros((H,W,3),dtype=np.float32);confidence=np.zeros((H,W),dtype=np.float32)
field[y1:y2,x1:x2]=repair;confidence[y1:y2,x1:x2]=blur(mask.astype(np.float32),r=2,passes=1)
out=ROOT/'build/queen-mission'/args.out;out.mkdir(exist_ok=True,parents=True);np.save(out/'pigment.npy',field);np.save(out/'confidence.npy',confidence)
config={'source_sha256':digest,'only_finial':args.only_finial,'capture':args.capture,'input_pigment_sha256':hashlib.sha256((data/'pigment-only.npy').read_bytes()).hexdigest(),'input_height_sha256':hashlib.sha256((data/'relief-height.npy').read_bytes()).hexdigest(),'crop':crop,'mask_pixels':int(mask.sum()),'harmonic_iterations':iteration+1,'last_log_color_change':change,'reflection_threshold':.12,'mask_expansion_radius':7,'fine_grain_strength':.35,'medium_grain_strength':args.medium_grain,'reference_grain_strength':args.reference_grain,'reference_grain_exclusion':'Exclude reference specular peaks (minimum RGB > .4) expanded by five pixels; remaining bounded radius-two detail only.','grain_source':'Accepted relief-field bandpass, optionally supplemented with bounded high-frequency reference grain outside expanded highlight masks; no broad reference brightness added.','method':'Fill negative highlight-shaped pigment marks from nearby log wood color in the selected finial-only or finial-and-bowl region. Preserve surrounding pigment, hidden coverage, geometry, UVs, normals and lights. Retain medium/fine grain from the existing independent relief field.'}
(out/'parameters.json').write_text(json.dumps(config,indent=2)+'\n')
Image.fromarray(np.uint8(np.clip(confidence,0,1)*255)).save(out/'mask.png')
im=Image.open(data/'pigment-only.png').convert('RGBA');tint=Image.new('RGBA',im.size,(0,220,255,0));tint.putalpha(Image.fromarray(np.uint8(np.clip(confidence,0,1)*100)));Image.alpha_composite(im,tint).crop((300,45,675,365)).resize((750,640)).save(out/'mask-inspection.png')
print(json.dumps(config),flush=True)
