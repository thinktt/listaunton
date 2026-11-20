"""Reconstruct pigment beneath a false highlight-shaped imprint using nearby wood."""
from pathlib import Path
import sys,json,hashlib,argparse
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
parser=argparse.ArgumentParser();parser.add_argument('--source',default='models/queen/queen-rebuilt.blend');parser.add_argument('--medium-grain',type=float,default=0);parser.add_argument('--out',default='base-pigment-repair-012');args=parser.parse_args();p=ROOT/'build/queen-mission/base-pigment-012';manifest=json.loads((p/'manifest.json').read_text());source=ROOT/args.source;assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['source_sha256'];x1,y1,x2,y2=manifest['crop'];pigment=np.load(p/'pigment-only.npy')[:,:,:3];reference=np.load(ROOT/'build/queen-mission/pigment-fit-011/reference-srgb.npy');actual=np.asarray(Image.open(p/'actual-wood.png').convert('RGB')).astype(np.float32)/255;ref=reference[y1:y2,x1:x2];h,w=pigment.shape[:2];assert ref.shape==pigment.shape
Y,X=np.indices((h,w));box=(X+x1>=500)&(X+x1<=660)&(Y+y1>=810)&(Y+y1<=1005);mask=((ref.min(2)>.22)|(actual.min(2)>.25))&box;mask=(blur(mask.astype(np.float32),r=4,passes=1)>.001)&box;mask[[0,-1],:]=False;mask[:,[0,-1]]=False
log=np.log(np.maximum(pigment,.0001));flat=log.copy().reshape(-1,3);idx=np.flatnonzero(mask.reshape(-1));boundary=(blur(mask.astype(np.float32),r=4,passes=1)>.001)&~mask;flat[idx]=np.median(log[boundary],axis=0);change=float('inf')
for iteration in range(5000):
 new=(flat[idx-w]+flat[idx+w]+flat[idx-1]+flat[idx+1])*.25
 if iteration%100==0:change=float(abs(new-flat[idx]).max())
 flat[idx]=new
 if iteration>100 and change<.00001:break
repaired=np.exp(flat.reshape(h,w,3));linear=np.load(ROOT/'build/queen-mission/pigment-fit-011/reference-linear.npy')[y1:y2,x1:x2];lum=linear@np.array([.2126,.7152,.0722],dtype=np.float32);grain=np.log(lum+.003);grain=np.clip(grain-blur(grain,r=3,passes=1),-.3,.3);repaired*=np.exp(grain*.7)[:,:,None]
if args.medium_grain:
 height=np.load(p/'relief-height.npy')[:,:,0]
 medium=np.log(height+.03)
 medium=np.clip(blur(medium,r=2,passes=1)-blur(medium,r=12,passes=2),-.25,.25)
 repaired*=np.exp(medium*args.medium_grain)[:,:,None]
weight=blur(mask.astype(np.float32),r=2,passes=1)
H,W=reference.shape[:2];field=np.zeros((H,W,3),dtype=np.float32);confidence=np.zeros((H,W),dtype=np.float32);field[y1:y2,x1:x2]=repaired;confidence[y1:y2,x1:x2]=weight;out=ROOT/'build/queen-mission'/args.out;out.mkdir(parents=True,exist_ok=True);np.save(out/'pigment.npy',field);np.save(out/'confidence.npy',confidence)
config={'source_sha256':manifest['source_sha256'],'crop':manifest['crop'],'repair_window':[500,810,660,1005],'mask_pixels':int(mask.sum()),'harmonic_iterations':iteration+1,'last_log_color_change':change,'grain_log_clip':[-.3,.3],'grain_strength':.7,'grain_radius':3,'medium_grain_strength':args.medium_grain,'medium_grain_source':'Existing relief-height field, bandpass radii 2 and 12, clipped to +/-0.25 in log height; excludes the invalid pigment imprint.','method':'Interpolate log pigment from adjacent wood through the highlight-shaped invalid region, adding bounded fine reference grain. Broad reference brightness is excluded. Existing hidden-surface coverage and all unmasked pigment are retained.'};(out/'parameters.json').write_text(json.dumps(config,indent=2));print(json.dumps(config),flush=True)
