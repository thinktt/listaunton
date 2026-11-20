"""Measure three reference highlight cores without modifying the reference."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--out',default='build/queen-mission/finial-targets-016');args=p.parse_args()
path=ROOT/'assets/queen/reference.png';im=Image.open(path).convert('RGB');a=np.asarray(im,dtype=float)/255
windows={'left':[466,168,487,191],'top':[487,162,507,186],'right':[487,193,512,217]}
targets=[]
for name,(x1,y1,x2,y2) in windows.items():
    intensity=a[y1:y2,x1:x2].min(2);weight=np.maximum(intensity-.5,0)**2;yy,xx=np.indices(weight.shape);assert weight.sum()>0
    x=float((weight*xx).sum()/weight.sum()+x1);y=float((weight*yy).sum()/weight.sum()+y1)
    targets.append({'name':'Display fitted finial-'+name+'-spot','pixel':[x,y],'window':[x1,y1,x2,y2],'peak_min_rgb':float(intensity.max())})
out=ROOT/args.out;out.mkdir(exist_ok=True,parents=True)
(out/'targets.json').write_text(json.dumps({'reference':path.relative_to(ROOT).as_posix(),'reference_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'method':'Minimum RGB core weighted by max(minRGB - 0.50, 0)^2 within isolated glint windows.','targets':targets},indent=2)+'\n')
crop=im.crop((410,140,550,280)).resize((560,560));d=ImageDraw.Draw(crop)
for t in targets:
    x=(t['pixel'][0]-410)*4;y=(t['pixel'][1]-140)*4;d.ellipse((x-18,y-18,x+18,y+18),outline='cyan',width=2);d.text((x+21,y),t['name'].split('-')[-2],fill='cyan')
crop.save(out/'measured-glints.png');print(json.dumps(targets),flush=True)
