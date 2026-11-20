import sys,numpy as np
from pathlib import Path
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D));from sculpt import load,pose,rest_coords,world_vertices
grid=np.load(D/'ring-chart.npz')['grid']
for file in ['parent','inspection']:
 s=load(file);v=rest_coords(world_vertices(s.objects['Knight | swept rounded mane']),pose(s))[grid];a=v[8];axis=a[128,[0,2]]-a[0,[0,2]];axis/=np.linalg.norm(axis);idx=128+np.arange(0,77,2);r=(a[idx][:,[0,2]]-a[128,[0,2]])@axis;w=abs(a[idx,1]);print(file,[(i*.5,round(float(wi),3),round(float(ri),3),round(float((r[i+1]-ri)/(w[i+1]-wi)),2)) for i,(wi,ri) in enumerate(zip(w[:-1],r[:-1])) if i%2==0])
