"""Check the real carved triangles and bilateral aperture before and after saving."""
from pathlib import Path
import json,sys
import bpy,numpy as np
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import load,pose,chart,rest_coords,AX,UP,CENTER,sculpt,DESIGNS
def inspect(scene):
    p=pose(scene);dg=bpy.context.evaluated_depsgraph_get();trees={};counts={}
    for name in ['near eye','far eye','continuous horse head and neck']:
        ob=scene.objects['Knight | '+name].evaluated_get(dg)
        me=ob.to_mesh();me.calc_loop_triangles();m=np.asarray(ob.matrix_world)
        v=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',v.ravel())
        xyz=rest_coords(v@m[:3,:3].T+m[:3,3],p)
        f=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('vertices',f.ravel())
        if not name.endswith('eye'):
            u,w=chart(xyz);local=(abs(u-.025)<.44)&(abs(w-.011)<.30);f=f[local[f].any(1)]
        tree=BVHTree.FromPolygons(xyz.tolist(),f.tolist(),all_triangles=True);trees[name]=tree
        crossing=[(a,b) for a,b in tree.overlap(tree) if a<b and not np.any(f[a][:,None]==f[b])]
        samples=[]
        if crossing:
            pts=np.array([.5*(xyz[f[a]].mean(0)+xyz[f[b]].mean(0)) for a,b in crossing])
            u,v=chart(pts);samples=np.round(np.column_stack((u,v,pts[:,1])),5).tolist()[:8]
        counts[name]={'triangles_checked':len(f),'nonadjacent_crossings':len(crossing),'sample_crossings_u_v_y':samples};ob.to_mesh_clear()
    uv=np.array([(u,w) for u in np.arange(-.29,.331,.006) for w in np.arange(-.12,.157,.006)])
    pos=CENTER+uv[:,0,None]*AX+uv[:,1,None]*UP
    masks=[];depths=[]
    for name,sign in [('near',-1),('far',1)]:
        exposed=[];depth=[]
        for x,z in pos:
            ray=(x,sign*2.8,z);towards=(0,-sign,0)
            h=trees['continuous horse head and neck'].ray_cast(ray,towards)[0];e=trees[name+' eye'].ray_cast(ray,towards)[0]
            a=h is not None and e is not None and sign*(e.y-h.y)>0
            exposed.append(a);depth.append(sign*(e.y if a else h.y) if h else np.nan)
        masks.append(np.array(exposed));depths.append(np.array(depth))
    are=masks[0]|masks[1];q=abs(np.subtract(*depths))[are]
    return {'nonadjacent_intersections':counts,'sample_spacing':.006,'near_exposed_samples':int(masks[0].sum()),
            'far_exposed_samples':int(masks[1].sum()),'mirrored_exposure_iou':float((masks[0]&masks[1]).sum()/are.sum()),
            'exposed_mirrored_depth_difference_p95':float(np.percentile(q,95))}
if __name__=='__main__':
    opts=sys.argv[sys.argv.index('--')+1:]
    for name in opts:
        scene=load('parent.blend' if name.isdigit() or name=='dense' else name+'.blend')
        if name=='dense':
            from carve import densify
            for side in ['near','far']:densify(scene.objects['Knight | '+side+' eye'])
        if name.isdigit():sculpt(scene,DESIGNS[int(name)])
        out=inspect(scene);print(name,out,flush=True)
        (D/f'native-check-{name}.json').write_text(json.dumps(out,indent=2)+'\n')
