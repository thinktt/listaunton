"""Place a finite amber strip where both flanks' physical bevel would reflect the studio."""
import numpy as np,bpy
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from survey import rest_coords,pose,world_vertices,MANE
def fit(s,oval,v):
    o=s.objects[MANE].evaluated_get(bpy.context.evaluated_depsgraph_get());m=o.to_mesh();m.calc_loop_triangles()
    mw=np.asarray(o.matrix_world);world=world_vertices(o);rest=rest_coords(world,pose(s))
    tri=np.empty((len(m.loop_triangles),3),np.int32);m.loop_triangles.foreach_get('vertices',tri.ravel())
    loops=np.empty_like(tri);m.loop_triangles.foreach_get('loops',loops.ravel());n=np.empty((len(m.corner_normals),3),np.float32);m.corner_normals.foreach_get('vector',n.ravel())
    tree=BVHTree.FromPolygons(rest.tolist(),tri.tolist(),all_triangles=True)
    cam=np.asarray(s.camera.matrix_world.to_quaternion()@Vector((0,0,1)));q=[];r=[]
    for x in np.linspace(-.81,.17,57):
        knee=np.interp(x,[-1.,-.78,-.62,-.40,-.20,-.04,.09,.18,.29],[.077,.093,.101,.106,.113,.118,.122,.102,.060])
        y=-knee+v[0]-v[14];pt,_,i,_=tree.ray_cast((x,y,6.),(0,0,-1))
        if pt is None:continue
        f=rest[tri[i]];a,b=np.linalg.lstsq((f[1:]-f[0]).T,np.asarray(pt)-f[0],rcond=None)[0]
        w=np.array([1-a-b,a,b]);normal=w@n[loops[i]]@np.linalg.inv(mw[:3,:3]);normal/=np.linalg.norm(normal)
        q.append(w@world[tri[i]]);r.append(2*cam.dot(normal)*normal-cam)
    o.to_mesh_clear();q=np.asarray(q);r=np.asarray(r)
    norm=np.median(r,axis=0);norm/=np.linalg.norm(norm);center=q.mean(0)+1.56*norm
    pts=q+r*(((center-q)@norm)/(r@norm))[:,None]
    mid=np.median(pts,axis=0);_,_,U=np.linalg.svd(pts-mid);along=U[0]-norm*U[0].dot(norm);along/=np.linalg.norm(along);across=np.cross(norm,along)
    low,high=np.percentile((pts-mid)@along,[1,99]);mid+=.5*(low+high)*along
    oval.location=Vector(mid);oval.rotation_euler=Matrix(np.column_stack([along,across,norm])).to_euler()
    oval.data.size=float(np.clip((high-low)*1.17,.95,4.1));oval.data.size_y=v[5]
