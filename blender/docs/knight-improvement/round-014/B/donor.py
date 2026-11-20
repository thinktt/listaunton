"""Read the actual adjacent neck wood as a donor at a calibrated physical scale."""
from pathlib import Path
import sys
import bpy,numpy as np
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from map import unpose
from evidence import load

def main():
    s=load('parent.blend');o=s.objects['Knight | continuous horse head and neck'].evaluated_get(bpy.context.evaluated_depsgraph_get())
    me=o.to_mesh();m=np.asarray(o.matrix_world);co=np.empty((len(me.vertices),3),np.float32)
    me.vertices.foreach_get('co',co.ravel());co=unpose(s,co@m[:3,:3].T+m[:3,3])
    me.calc_loop_triangles();tri=np.empty((len(me.loop_triangles),3),np.int32);ll=np.empty_like(tri)
    me.loop_triangles.foreach_get('vertices',tri.ravel());me.loop_triangles.foreach_get('loops',ll.ravel())
    uv=np.empty((len(me.loops),2),np.float32);me.uv_layers['Knight wood atlas'].data.foreach_get('uv',uv.ravel())
    tree=BVHTree.FromPolygons(co.tolist(),tri.tolist(),all_triangles=True)
    xmin,xmax,zmin,zmax=-.70,.55,2.1,4.28;spacing=.0038
    xs=np.arange(xmin,xmax,spacing);zs=np.arange(zmin,zmax,spacing)
    out=[]
    for sign in (-1,1):
        hit=np.full((len(zs),len(xs)),-1,np.int32)
        for row,z in enumerate(zs):
            for col,x in enumerate(xs):
                idx=tree.ray_cast((x,sign*3,z),(0,-sign,0))[2]
                if idx is not None:hit[row,col]=idx
        y,x=np.nonzero(hit>=0);ids=hit[y,x];v=co[tri[ids]][:,:,[0,2]]
        ab=v[:,1]-v[:,0];ac=v[:,2]-v[:,0];coord=np.column_stack((xs[x],zs[y]))-v[:,0]
        det=ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0]
        w1=(coord[:,0]*ac[:,1]-coord[:,1]*ac[:,0])/det;w2=(ab[:,0]*coord[:,1]-ab[:,1]*coord[:,0])/det
        basis=np.column_stack((1-w1-w2,w1,w2));target=np.full((*hit.shape,2),np.nan,np.float32)
        target[y,x]=np.sum(basis[:,:,None]*uv[ll[ids]],axis=1);out.append(target)
    current=np.array(out);np.savez_compressed(D/'neck-donor.npz',uv=current,spacing=spacing,x_min=xmin,z_min=zmin)
    o.to_mesh_clear()
if __name__=='__main__':main()
