"""Report object-only regional RGB medians; never change source images."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('variants',nargs='*');args=p.parse_args()
regions={'bowl':(330,90,630,310),'finial':(450,170,515,245),'body':(390,350,570,415),'collars':(350,445,610,530),'stem':(425,560,530,690),'socket':(380,760,580,805),'base':(300,840,660,970),'foot':(325,1040,630,1070)}
paths={'reference':ROOT/'assets/queen/reference.png','accepted':ROOT/'assets/queen/queen-brown.png'}
paths.update({v:ROOT/'build/queen-mission'/v/'wood.png' for v in args.variants})
result={}
for label,path in paths.items():
 a=np.array(Image.open(path).convert('RGBA'));result[label]={}
 for region,(x1,y1,x2,y2) in regions.items():
  c=a[y1:y2,x1:x2];m=(c[:,:,3]>127)&(c[:,:,:3].max(2)>20)&(c[:,:,:3].max(2)<160)
  result[label][region]=np.median(c[:,:,:3][m],axis=0).tolist()
print(json.dumps(result,indent=2))
