"""Extract actual evaluated UV locations and physical vertex positions from 11B."""
from pathlib import Path
import sys
import bpy,numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import load,rest_coords,pose,MANE,pchip,ST,POST,ED,ease
def run():
    s=load('parent.blend');dg=bpy.context.evaluated_depsgraph_get();out={}
    for o in s.objects:
        if o.type!='MESH' or o.hide_render:continue
        ob=o.evaluated_get(dg);m=np.array(ob.matrix_world);me=ob.to_mesh();me.calc_loop_triangles()
        tri=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('loops',tri.ravel())
        uv=np.empty((len(me.loops),2),np.float32);me.uv_layers['Knight wood atlas'].data.foreach_get('uv',uv.ravel())
        key=o.name.removeprefix('Knight | ');out[key]=uv[tri]
        if key==MANE:
            lv=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',lv)
            c=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',c.ravel())
            a=rest_coords(c@m[:3,:3].T+m[:3,3],pose(s));x,y,z=a.T
            back=pchip(ST,POST,z)
            # Broad wood-tone correction on the descending *bilateral*
            # facing surface. Rear grain, distal seat and upper poll blend
            # gradually back into the unaltered parent wood.
            gate=ease((z-2.16)/.57)*(1-ease((z-4.32)/.31))
            gate*=ease((x-back-.015)/.42)
            out['strength']=gate[lv[tri]].astype(np.float32)
        ob.to_mesh_clear()
    np.savez_compressed(D/'atlas-geometry.npz',**out)
if __name__=='__main__':run()
