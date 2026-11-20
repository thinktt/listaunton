"""Survey the native crown and its physical studio before cutting the new shoulder."""
from pathlib import Path
import json,sys
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from evidence import load
from mission_scene import world_vertices
from lower_carving_fit import rest_coords
from probe_carving import point_probe
MANE='Knight | swept rounded mane'
def pose(s):
    a=json.loads(s['knight_mission_pose']);return [a[k] for k in ('dx','dy','twist_degrees')]
def survey(s):
    p=pose(s);probe=point_probe(s);cam=np.asarray(s.camera.matrix_world.to_quaternion()@Vector((0,0,1)))
    o=s.objects[MANE];m=o.data;co=world_vertices(o);a=rest_coords(co,p)
    mesh=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).data;mw=np.array(o.matrix_world)
    mesh.calc_loop_triangles();vs=np.empty((len(mesh.vertices),3),np.float32);mesh.vertices.foreach_get('co',vs.ravel());vs=vs@mw[:3,:3].T+mw[:3,3]
    tris=np.empty((len(mesh.loop_triangles),3),np.int32);mesh.loop_triangles.foreach_get('vertices',tris.ravel())
    loops=np.empty_like(tris);mesh.loop_triangles.foreach_get('loops',loops.ravel())
    normals=np.empty((len(mesh.corner_normals),3),np.float32);mesh.corner_normals.foreach_get('vector',normals.ravel())
    tree=BVHTree.FromPolygons(vs.tolist(),tris.tolist(),all_triangles=True)
    cov=np.empty(len(mesh.vertices),np.float32);mesh.attributes['Knight varnish coverage'].data.foreach_get('value',cov)
    rows=[];guide=[[298,347],[320,341],[340,338],[360,338],[380,338],[400,339],[420,340],[440,342],[452,345],[462,350],[471,355]]
    for x in list(range(300,471,4))+[435,438]:
        for dy in [-21,-14,-9,-5,-2,0,2,4,8,16]:
            y=round(np.interp(x,*np.array(guide).T))+dy;h=probe(x+.5,y+.5)
            if not h or h[1]!=o.name:continue
            xyz=np.asarray(h[2]);_,_,it,_=tree.find_nearest(Vector(xyz));tri=vs[tris[it]]
            u,v=np.linalg.lstsq((tri[1:]-tri[0]).T,xyz-tri[0],rcond=None)[0];w=np.array([1-u-v,u,v])
            n=w@normals[loops[it]]@np.linalg.inv(mw[:3,:3]);n/=np.linalg.norm(n)
            rows.append({'pixel':[x,y],'offset':dy,'rest':rest_coords(xyz[None,:],p)[0].tolist(),'world':xyz.tolist(),
                         'normal':n.tolist(),'reflected':(2*n.dot(cam)*n-cam).tolist(),'polish':float(w@cov[tris[it]])})
    lamps={}
    for o in s.objects:
        if o.type=='LIGHT' and ('Poll flag' in o.name or 'poll rear oval' in o.name):
            l=o.data;coll=o.light_linking.receiver_collection
            lamps[o.name]=[list(o.matrix_world.translation),l.energy,list(l.color),l.shape,l.size,l.size_y,l.spread,[o.name for o in coll.objects] if coll else None]
    return {'rows':rows,'lamps':lamps,'native_vertices':len(a),'evaluated_vertices':len(vs),'native_bounds':[a.min(0).tolist(),a.max(0).tolist()]}
if __name__=='__main__':
    key=sys.argv[-1];s=load(key+'.blend');data=survey(s);(D/f'surface-{key}.json').write_text(json.dumps(data,indent=2)+'\n')
    print(data['lamps'],data['native_bounds'],data['native_vertices'],data['evaluated_vertices'])
