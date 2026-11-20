"""Match opposite vertices by the two native unfolded sphere maps."""
import numpy as np
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
import bmesh,bpy
def coordinates(mesh,mirrored=False):
    vi=np.empty(len(mesh.loops),np.int32);mesh.loops.foreach_get('vertex_index',vi)
    uv=np.empty((len(vi),2),np.float32);mesh.uv_layers['UVMap'].data.foreach_get('uv',uv.ravel())
    if mirrored:uv[:,0]*=-1
    phase=2*np.pi*uv[:,0];count=np.bincount(vi)
    theta=np.angle(np.bincount(vi,weights=np.cos(phase))+1j*np.bincount(vi,weights=np.sin(phase)))
    lat=np.pi*np.bincount(vi,weights=uv[:,1])/count
    return np.column_stack((np.cos(theta)*np.sin(lat),np.sin(theta)*np.sin(lat),np.cos(lat)))
def opposite(near,far):
    a=coordinates(near);b=coordinates(far,True);tree=KDTree(len(a))
    for i,pt in enumerate(a):tree.insert(pt,i)
    tree.balance();hits=[tree.find(pt) for pt in b]
    ids=np.array([h[1] for h in hits]);worst=max(h[2] for h in hits)
    assert len(set(ids))==len(b) and worst<.0002,(len(set(ids)),len(b),worst)
    return ids
def intersections(mesh):
    mesh.calc_loop_triangles()
    v=np.empty((len(mesh.vertices),3),np.float32);mesh.vertices.foreach_get('co',v.ravel())
    f=np.empty((len(mesh.loop_triangles),3),np.int32);mesh.loop_triangles.foreach_get('vertices',f.ravel())
    tree=BVHTree.FromPolygons(v.tolist(),f.tolist(),all_triangles=True)
    return [(mesh.loop_triangles[i].polygon_index,mesh.loop_triangles[j].polygon_index) for i,j in tree.overlap(tree)
            if i<j and not (f[i][:,None]==f[j]).any()]
def triangles(ob):
    original=ob.data;pairs=intersections(original)
    if not pairs:return []
    p,count=np.unique(np.asarray(pairs),return_counts=True);ids=[int(i) for i in p[np.argsort(count)[::-1]]]
    for faces in [[i] for i in ids]+[ids]:
        for method in ['ALTERNATE','FIXED','BEAUTY','LONG_EDGE']:
            me=original.copy();bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table()
            bmesh.ops.triangulate(bm,faces=[bm.faces[i] for i in faces],quad_method=method)
            bm.to_mesh(me);bm.free();me.update()
            if not intersections(me):
                ob.data=me
                if original.users==0:bpy.data.meshes.remove(original)
                return [faces,method]
            bpy.data.meshes.remove(me)
    raise RuntimeError(('Unable to seat the original folded return',pairs))
