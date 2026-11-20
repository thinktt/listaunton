"""Reference anchors on the actual surfaces, plus transverse sections in the billet."""
from pathlib import Path
import json,sys,bpy,numpy as np
from mathutils.bvhtree import BVHTree
D=Path(__file__).resolve().parent;sys.dont_write_bytecode=True
sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from probe_carving import point_probe,rest
from lower_carving_fit import rest_coords
from mission_scene import world_vertices,sha
axis=np.array([1.,-.76])/np.hypot(1,.76);up=np.array([-axis[1],axis[0]]);center=np.array([.412,4.158])
def chart(p):q=p[..., [0,2]]-center;return np.stack((q@axis,q@up),-1)
def tree(ob,pose):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles()
    v=np.empty((len(m.vertices),3),np.float32);m.vertices.foreach_get('co',v.ravel())
    mat=np.array(ob.matrix_world);p=rest_coords(v@mat[:3,:3].T+mat[:3,3],pose)
    tri=np.empty((len(m.loop_triangles),3),np.int32);m.loop_triangles.foreach_get('vertices',tri.ravel())
    out=BVHTree.FromPolygons(p.tolist(),tri.tolist(),all_triangles=True);ev.to_mesh_clear();return out
def main():
    name='knight' if '--candidate' in sys.argv else 'parent';path=D/(name+'.blend')
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);s=bpy.context.scene
    p=json.loads(s['knight_mission_pose']);pose=[p[k] for k in ('dx','dy','twist_degrees')]
    points=point_probe(s);land=[]
    for x,y in json.loads((D/'source-anchors.json').read_bytes())['anchor_points']:
        h=points(x+.5,y+.5);xyz=rest(h[2],p);land.append({'xy':[x,y],'part':h[1],'xyz':xyz,'uv':chart(np.array(xyz)).tolist()})
    u=np.linspace(-.52,.83,271);v=np.linspace(-.28,.34,125);U,V=np.meshgrid(u,v);xz=center+U[...,None]*axis+V[...,None]*up
    blocks={}
    for prefix,sign in [('near',-1),('far',1)]:
        for k,part in [('eye',prefix+' eye'),('ear',prefix+' swept ear'),('head','continuous horse head and neck')]:
            ob=s.objects['Knight | '+part];t=tree(ob,pose);y=np.full(U.shape,np.nan)
            for i,j in np.ndindex(y.shape):
                x,z=xz[i,j];h=t.ray_cast((x,2*sign,z),(0,-sign,0))[0]
                if h is not None:y[i,j]=h.y*sign
            blocks[prefix+'_'+k]=y
    np.savez_compressed(D/(name+'-sections.npz'),u=u,v=v,**blocks)
    (D/(name+'-landmarks.json')).write_text(json.dumps({'model':sha(path),'landmarks':land},indent=2)+'\n')
    print([(a['xy'],a['part'],np.around(a['uv'],3).tolist()) for a in land])
    print([(k,len(s.objects['Knight | '+k].data.vertices),[(m.name,m.type) for m in s.objects['Knight | '+k].modifiers]) for k in ['continuous horse head and neck','near eye','near swept ear']])
if __name__=='__main__':main()
