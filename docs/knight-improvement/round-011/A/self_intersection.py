"""Find non-adjacent intersections inside each individual evaluated carving."""
from pathlib import Path
import hashlib,json,sys
import bpy,numpy as np
from mathutils.bvhtree import BVHTree
D=Path(__file__).resolve().parent
def exact_pair(a,b,tol=1e-8):
    # Triangle separating axes include both normals and all edge cross products.
    # In their common plane the two triangles additionally require the planar
    # edge-normal axes. This also detects touching without a shared vertex ID.
    ea=np.roll(a,-1,axis=0)-a;eb=np.roll(b,-1,axis=0)-b
    na=np.cross(ea[0],ea[1]);nb=np.cross(eb[0],eb[1])
    axes=[na,nb,*np.cross(ea[:,None,:],eb[None,:,:]).reshape(9,3)]
    axes.extend(np.cross(na,ea));axes.extend(np.cross(nb,eb))
    axes=np.array(axes);size=np.linalg.norm(axes,axis=1);axes=axes[size>1e-14]/size[size>1e-14,None]
    p=a@axes.T;q=b@axes.T
    return bool(np.all(p.max(0)>=q.min(0)-tol)&np.all(q.max(0)>=p.min(0)-tol))
def test(obj,graph):
    ev=obj.evaluated_get(graph);me=ev.to_mesh()
    coords=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',coords.ravel())
    me.calc_loop_triangles();tri=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('vertices',tri.ravel())
    tree=BVHTree.FromPolygons(coords.tolist(),tri.tolist(),all_triangles=True,epsilon=0)
    pairs=tree.overlap(tree);hits=[];checked=0
    for l,r in pairs:
        if l>=r:continue
        lt,rt=tri[l],tri[r]
        if (lt[:,None]==rt[None,:]).any():continue
        checked+=1
        if exact_pair(coords[lt].astype(float),coords[rt].astype(float)):
            xyz=np.mean(np.vstack((coords[lt],coords[rt])).astype(float),axis=0)
            hits.append({'triangles':[l,r],'vertex_indices':[lt.tolist(),rt.tolist()],'centroid_local':xyz.tolist()})
    n=len(tri);ev.to_mesh_clear()
    return {'evaluated_triangles':n,'bvh_nonadjacent_pairs_checked':checked,'intersection_count':len(hits),'pairs':hits}
def main():
    result={};which=['near eye','far eye']
    if '--skull' in sys.argv:which=['continuous horse head and neck']
    for tag,n in [('parent','parent'),('candidate','knight')]:
        src=D/(n+'.blend');bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False)
        graph=bpy.context.evaluated_depsgraph_get()
        result[tag]={'sha256':hashlib.sha256(src.read_bytes()).hexdigest()}
        for name in which:
            v=test(bpy.context.scene.objects['Knight | '+name],graph);result[tag][name]=v;print(tag,name,v['intersection_count'],flush=True)
    out='skull-intersections.json' if '--skull' in sys.argv else 'self-intersections.json'
    (D/out).write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
