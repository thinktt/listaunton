"""Fixed-coordinate high-pass grain diagnostic; excludes obvious reflections."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image
from image_math import blur
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('variants',nargs='+');args=p.parse_args()
ref=np.asarray(Image.open(ROOT/'assets/queen/reference.png').convert('RGBA'),dtype=np.float32)/255
def detail(a):
 x=np.log(.01+a[:,:,:3].mean(2));return x-blur(x,r=7,passes=3)
rd=detail(ref)
regions={'bowl_left':(350,165,420,255),'bowl_right':(550,165,615,255),'crown_body':(410,365,565,420),'stem':(425,610,550,720),'base':(330,850,610,985)}
records={}
for variant in ['accepted']+args.variants:
 path=ROOT/'assets/queen/queen-brown.png' if variant=='accepted' else ROOT/'build/queen-mission'/variant/'wood.png'
 a=np.asarray(Image.open(path).convert('RGBA'),dtype=np.float32)/255;ad=detail(a);scores={}
 mask=(a[:,:,3]>.995)&(ref[:,:,:3].max(2)>.06)&(a[:,:,:3].max(2)>.06)
 mask&=(ref[:,:,:3].min(2)<.23)&(a[:,:,:3].min(2)<.23)
 for name,(x0,y0,x1,y1) in regions.items():
  roi=(slice(y0,y1),slice(x0,x1));m=mask[roi];x=rd[roi][m];y=ad[roi][m]
  scores[name]={'pixels':int(m.sum()),'correlation':float(np.corrcoef(x,y)[0,1]),'reference_std':float(x.std()),'model_std':float(y.std())}
 records[variant]=scores
out=ROOT/'build/queen-mission/grain-correlation.json';out.write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records,indent=2))
