"""Record where the inherited physical upper softbox faces the actual eye."""
from pathlib import Path
import math,sys,json
import numpy as np
import bpy
from mathutils import Vector
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from orbital import AX,UP,pose,rest_coords,chart
from evidence import load
from probe_carving import point_probe
def measure(s):
    p=pose(s);q=point_probe(s);view=np.asarray(s.camera.matrix_world.to_quaternion()@Vector((0,0,1)))
    a=math.radians(p[2]);ca,sa=math.cos(a),math.sin(a)
    UE=np.r_[ca*AX[0],sa*AX[0],AX[1]];VE=np.r_[ca*UP[0],sa*UP[0],UP[1]];L=np.r_[sa,-ca,0.]
    pts={}
    for x,y in [(493,469),(497,471),(501,471),(504,473),(503,480),(508,477),(511,484),(516,482),(526,484),(534,483),(539,485)]:
        hit=q(x+.5,y+.5)
        if not hit:continue
        w=np.array(hit[2]);o=rest_coords(w[None,:],p);u,v=chart(o)
        n=np.array(hit[3])
        light=np.array(s.objects['Eye reflection upper'].matrix_world.translation)-w;light/=np.linalg.norm(light);target=light+view;target/=np.linalg.norm(target)
        slope=lambda h:[round(float(-h.dot(ax)/h.dot(L)),4) for ax in [UE,VE]]
        pts[str((x,y))]={'xy':[x,y],'u_v_depth':[float(u[0]),float(v[0]),float(abs(o[0,1]))],
               'owner':hit[1],'actual_shape_slopes':slope(n),'card_facing_slopes':slope(target)}
    return pts
if __name__=='__main__':
    s=load('parent.blend');q=measure(s);(D/'upper-card-parent.json').write_text(json.dumps(q,indent=2)+'\n')
    for val in q.values():print(val['xy'],np.round(val['u_v_depth'],3),val['actual_shape_slopes'],val['card_facing_slopes'])
