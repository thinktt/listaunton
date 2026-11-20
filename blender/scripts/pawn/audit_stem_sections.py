from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
r=Path(__file__).resolve().parents[2]
paths={'reference':r/'assets/pawn/reference.png','013':r/'history/pawn-mission-013/render.png'}
for trial in sys.argv[1:]:paths[trial]=r/'build/pawn-mission'/trial/'fixed.png'
out={}
for label,path in paths.items():
    a=np.asarray(Image.open(path).convert('RGB'),float)@np.array([.24,.53,.23]);rows=[]
    for y in [616,620,624,628,632,636,640]:
        x=np.arange(388,435);q=a[y-1:y+2,388:435].mean(0)
        center=1033-y;area=abs(x-center)<14
        b=q.copy();b[~area]=0
        peak=b.max();above=area&(b>max(80,peak*.65));mass=np.maximum(b-65,0);mass[~area]=0
        centroid=round(float(np.sum(mass*x)/mass.sum()),2) if mass.sum()>0 else None
        rows.append({'y':y,'peak_x':int(x[b.argmax()]),'centroid':centroid,'peak':round(float(peak),2),'width65':int(above.sum())})
    out[label]=rows
print(json.dumps(out,indent=2))
(r/'build/pawn-mission/stem-sections.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
