from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageFilter,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[2]
im=Image.open(root/'assets/queen/reference.png').convert('RGB')
arr=np.array(im.filter(ImageFilter.GaussianBlur(1.2)),dtype=float)/255
lum=arr@np.array([.2126,.7152,.0722]);gy,gx=np.gradient(lum)
cx=483.625;b=.809017
results={}
for name,ar,fr in [('upper',range(108,142,2),range(450,471)),('middle',range(151,177,2),range(503,527)),('lower',range(170,185,2),range(548,567))]:
    trials=[]
    for a in ar:
      for front in fr:
        t=np.linspace(-.82,.82,200);x=cx+a*t;y=front-b*a*(1-np.sqrt(1-t*t))
        ix=x.astype(int);iy=y.astype(int)
        # Dark drop just below the bright rolled front edge.
        nx=b*t/np.sqrt(1-t*t);ny=np.ones_like(t);norm=np.sqrt(nx*nx+1)
        edge=-(gx[iy,ix]*nx+gy[iy,ix])/norm
        score=float(np.mean(np.clip(edge,0,None)))
        trials.append((score,a,front))
    trials.sort(reverse=True)
    chosen=trials[0]
    results[name]={'radius_px':chosen[1],'front_y':chosen[2],'score':chosen[0],'top5':trials[:5]}
out=root/'build/queen-mission';out.mkdir(parents=True,exist_ok=True)
(out/'collar-arc-candidates.json').write_text(json.dumps(results,indent=2))
display=im.crop((280,300,690,590)).resize((820,580))
d=ImageDraw.Draw(display)
colors=['#ff55cc','#33ddff','#55ff55']
for (name,item),col in zip(results.items(),colors):
 a=item['radius_px'];front=item['front_y'];t=np.linspace(-.92,.92,250)
 pts=[((cx+a*v-280)*2,(front-b*a*(1-np.sqrt(1-v*v))-300)*2) for v in t]
 d.line(pts,fill=col,width=2)
display.save(out/'collar-arcs.png')
print(json.dumps(results,indent=2))
