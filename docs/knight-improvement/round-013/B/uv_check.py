"""Audit the actual atlas coordinates on opened parent and candidate eyes."""
from pathlib import Path
import json,sys
import bpy,numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from orbital import pose,rest_coords,mesh_tree,HEAD,chart
from evidence import load

def measure(s,part,sign):
    tree=mesh_tree(s,HEAD)
    ob=s.objects['Knight | '+part].evaluated_get(bpy.context.evaluated_depsgraph_get())
    data=ob.to_mesh();m=np.asarray(ob.matrix_world);data.calc_loop_triangles()
    uv=np.empty((len(data.loops),2),np.float32)
    data.uv_layers['Knight wood atlas'].data.foreach_get('uv',uv.ravel())
    assert np.isfinite(uv).all() and uv.min()>=0 and uv.max()<=1
    co=np.empty((len(data.vertices),3),np.float32);data.vertices.foreach_get('co',co.ravel())
    co=rest_coords(co@m[:3,:3].T+m[:3,3],pose(s))
    tris=np.empty((len(data.loop_triangles),3),np.int32);data.loop_triangles.foreach_get('vertices',tris.ravel())
    loops=np.empty_like(tris);data.loop_triangles.foreach_get('loops',loops.ravel())
    normal=np.cross(co[tris[:,1]]-co[tris[:,0]],co[tris[:,2]]-co[tris[:,0]])
    external=np.flatnonzero(sign*normal[:,1]>0)
    p=co[tris[external]].mean(1)
    use=[]
    for index,(x,y,z) in zip(external,p):
        q=tree.ray_cast((x,sign*2,z),(0,-sign,0))[0]
        if q is not None and sign*(y-q.y)>0:use.append(index)
    t=uv[loops[use]].astype(float);edge=(np.roll(t,1,axis=1)-t)*3072
    area=.5*abs(edge[:,0,0]*edge[:,1,1]-edge[:,0,1]*edge[:,1,0])
    lens=np.linalg.norm(edge,axis=2).max(1);bad=np.array(use)[lens>4]
    if len(bad):
        pos=co[tris[bad]].mean(1);u,v=chart(pos)
        region=np.column_stack((u,v))
        true_area=np.linalg.norm(normal,axis=1)
        adverse={'triangles':len(bad),'exposed_surface_area_percent':round(float(100*true_area[bad].sum()/true_area[use].sum()),3),
                 'center_u_v_range':[region.min(0).round(4).tolist(),region.max(0).round(4).tolist()]}
    else:adverse={'triangles':0,'exposed_surface_area_percent':0}
    out={'uv_min':uv.min(0).tolist(),'uv_max':uv.max(0).tolist(),'finite_and_in_range':True,
         'visible_outer_triangles':len(use),'exposed_uv_area_below_1e-7_sq_texels':int((area<1e-7).sum()),
         'visible_longest_uv_edge_p50_p95_p99_max_in_texels':np.round(np.percentile(lens,[50,95,99,100]),4).tolist(),
         'uv_over_four_texels':adverse}
    ob.to_mesh_clear();return out

out={}
for name in ['parent','knight']:
    s=load(name+'.blend');out[name]={label:measure(s,label+' eye',sg) for label,sg in [('near',-1),('far',1)]}
for side in ['near','far']:
    a=out['parent'][side];b=out['knight'][side]
    for k,sg in [('uv_min',1),('uv_max',-1)]:
        assert np.all(sg*(np.array(b[k])-a[k])>=-1e-6)
(D/'uv-check.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
