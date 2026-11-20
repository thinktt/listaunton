"""Identify the true part and native mane station under the front return in the fixed view."""
from pathlib import Path
import json,sys,numpy as np,bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D));from sculpt import load,carve,pose
from probe_carving import point_probe
from lower_carving_fit import rest_coords
def run():
 s=load('parent');carve(s);probe=point_probe(s);o=s.objects['Knight | swept rounded mane'];m=o.data;m.calc_loop_triangles();mat=np.array(o.matrix_world)
 v=np.array([x.co[:] for x in m.vertices])@mat[:3,:3].T+mat[:3,3];tri=np.array([t.vertices[:] for t in m.loop_triangles])
 tree=BVHTree.FromPolygons(v.tolist(),tri.tolist(),all_triangles=True)
 c=np.load(D/'ring-chart.npz');grid=c['grid'];ss=np.full(len(v),-1.);jj=ss.copy();ss[grid]=np.arange(len(grid))[:,None]/4;jj[grid]=np.abs(np.arange(256)-128)/4
 np.savez(D/'sampled-front.npz',vertices=rest_coords(v,pose(s)),grid=grid)
 print('custom normals',m.has_custom_normals,'smooth',sum(f.use_smooth for f in m.polygons),'total',len(m.polygons))
 rec=[]
 for y in range(314,390,3):
  row=[]
  for x in range(443,496,3):
   h=probe(x+.5,y+.5);name=h[1] if h else 'background'
   if name.endswith('mane'):
    _,_,i,_=tree.find_nearest(h[2]);ii=tri[i];data=[round(float(ss[ii].mean()),2),round(float(jj[ii].mean()),1)]
   else:data=None
   row.append([x,name.split(' | ')[-1],data])
  rec.append([y,row])
 (D/'front-map.json').write_text(json.dumps(rec)+'\n')
 print('columns x443..494 step3. Numbers=station*4, H=skull, C=cap')
 for y,row in rec:
  print(y,' '.join([' H' if v[2] is None else (' C' if v[2][0]<0 else '%2d'%round(v[2][0]*4)) for v in row]))
if __name__=='__main__':run()
