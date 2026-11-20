"""Record which part and bilateral surface carries the small fixed silhouette difference."""
from pathlib import Path
import sys,json,numpy as np,bpy
sys.dont_write_bytecode=True;D=Path(__file__).resolve().parent;sys.path.insert(0,str(D));from pictures import open_model
from probe_carving import point_probe,rest
from sculpt import chart
for name in ('parent','knight'):
 s=open_model(name);p=json.loads(s['knight_mission_pose']);probe=point_probe(s);rec=[]
 for px,py in ((392,303),(414,303),(422,304),(429,305),(437,307),(450,310),(500,325),(539,342)):
  for dy in [1.0,2.5,4.,8.0]:
   h=probe(px+.5,py+dy)
   if not h:continue
   q=rest(h[2],p);x,y=chart(np.array([q]));rec.append([px,py+dy,h[1],round(float(x[0]),3),round(float(y[0]),3),round(q[1],3)])
 (D/(name+'-crown-check.json')).write_text(json.dumps(rec,indent=2)+'\n')
