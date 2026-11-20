"""Locate the two eye islands in the inherited walnut atlas."""
from pathlib import Path
import sys,json
import bpy,numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D))
from carve import load,pose,rest_coords,world_vertices,chart
def run():
    s=load('parent.blend');p=pose(s);out={}
    for label in ['near eye','far eye','continuous horse head and neck','turned pedestal','swept rounded mane','near swept ear','far swept ear']:
        o=s.objects['Knight | '+label];me=o.data
        mat=o.active_material;atlas=mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node
        uvname=atlas.inputs['Vector'].links[0].from_node.uv_map
        uv=np.empty((len(me.loops),2),np.float32);me.uv_layers[uvname].data.foreach_get('uv',uv.ravel())
        me.calc_loop_triangles();loops=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('loops',loops.ravel())
        idx=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',idx)
        pts=rest_coords(world_vertices(o),p)
        if label.endswith('eye'):
            print(label,uvname,uv.min(0),uv.max(0),flush=True)
        out[label.replace(' ','_')+'_UV']=uv[loops]
        if label.endswith('eye') or label=='continuous horse head and neck':out[label.replace(' ','_')+'_pts']=pts[idx[loops]]
    np.savez_compressed(D/'atlas-parts.npz',**out)
if __name__=='__main__':run()
