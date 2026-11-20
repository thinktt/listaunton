"""Measure bright low-saturation reflection regions without editing images."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('variants',nargs='*');args=p.parse_args()
regions={'bowl':(390,120,580,180),'finial':(440,165,525,240),'collars':(330,440,625,555),'socket':(365,720,600,810),'base_right':(510,820,665,985),'base_left':(300,850,480,1000),'foot':(330,1000,645,1050)}
paths={'reference':ROOT/'assets/queen/reference.png','accepted':ROOT/'assets/queen/queen-brown.png'};paths.update({v:ROOT/'build/queen-mission'/v/'wood.png' for v in args.variants})
result={}
for label,path in paths.items():
 a=np.array(Image.open(path).convert('RGB').filter(ImageFilter.GaussianBlur(2))).astype(float);result[label]={}
 for region,(x1,y1,x2,y2) in regions.items():
  w=np.maximum(0,a[y1:y2,x1:x2].min(2)-75);ys,xs=np.indices(w.shape)
  if w.sum()>0:
   cx=(xs*w).sum()/w.sum();cy=(ys*w).sum()/w.sum()
   result[label][region]={'mass':round(float(w.sum()),2),'centroid':[round(float(cx+x1),2),round(float(cy+y1),2)],'std_xy':[round(float(np.sqrt(((xs-cx)**2*w).sum()/w.sum())),2),round(float(np.sqrt(((ys-cy)**2*w).sum()/w.sum())),2)]}
  else:result[label][region]={'mass':0,'centroid':None,'std_xy':None}
print(json.dumps(result,indent=2))
