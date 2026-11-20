import sys
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import pchip,pose,ST,POST,ED,DESIGNS,HE,PULL,sculpt,load
from probe_carving import point_probe,rest
import json
for i in map(int,sys.argv[sys.argv.index('--')+1:]):
    s=load('parent.blend');sculpt(s,i);probe=point_probe(s);p=json.loads(s['knight_mission_pose'])
    rows=json.loads((D/f'sections-{i}.json').read_text())['rows']
    for r in rows:
        px,py=r['back_x']+1,r['row'];q=probe(px+.5,py+.5)
        if q is None:continue
        x,y,z=rest(q[2],p);b=pchip(ST,POST,z)+.021;e=pchip(ST,ED,z)-DESIGNS[i][0]*pchip(HE,PULL,z)
        hit=probe(r['joint_x']+.5,py+.5)
        qj=rest(hit[2],p)
        print(i,py,'z',round(z,3),'r',round((x-b)/(e-b),3),'joint',np.round(qj,3).tolist(),flush=True)
