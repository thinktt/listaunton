"""Measure the actual eye, cheek, and brow in a shared bilateral carving chart."""
from pathlib import Path
import json,sys
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parents[2]
sys.path[:0]=[str(D),str(R/'scripts/knight')]
from mission_scene import world_vertices,sha
from mission_pose import posed
from lower_carving_fit import rest_coords
AX=np.array([1.,-.76])/np.hypot(1.,.76);UP=np.array([-AX[1],AX[0]])
O=np.array([.412,4.158])
HEAD='continuous horse head and neck';BUILD='coherent skull cheek and conical muzzle'
def pose(s):
    p=json.loads(s['knight_mission_pose'])
    return [p[k] for k in ('dx','dy','twist_degrees')]
def chart(a):
    q=a[:,[0,2]]-O
    return q@AX,q@UP
def mesh_tree(s,name):
    ob=s.objects['Knight | '+name].evaluated_get(bpy.context.evaluated_depsgraph_get());m=np.asarray(ob.matrix_world)
    me=ob.to_mesh();me.calc_loop_triangles();v=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',v.ravel())
    v=rest_coords(v@m[:3,:3].T+m[:3,3],pose(s))
    f=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('vertices',f.ravel())
    tr=BVHTree.FromPolygons(v.tolist(),f.tolist(),all_triangles=True)
    ob.to_mesh_clear()
    return tr
def get_surface(s):
    u=np.arange(-.545,.931,.004);v=np.arange(-.425,.366,.004)
    U,V=np.meshgrid(u,v);xz=O+U[:,:,None]*AX+V[:,:,None]*UP
    out=np.full((2,2,len(v),len(u)),np.nan,np.float32)
    hd=mesh_tree(s,HEAD)
    for j,(label,sg) in enumerate([('near eye',-1),('far eye',1)]):
        for i,tr in enumerate([hd,mesh_tree(s,label)]):
            for k,(x,z) in enumerate(xz.reshape(-1,2)):
                hit=tr.ray_cast((x,sg*2.,z),(0.,-sg,0.))[0]
                if hit is not None:out[j,i].flat[k]=sg*hit.y
    return u,v,out
def probe(s,rows=None):
    # Read the annotated line from the actual approved source and locate
    # it on the head in both image coordinates and the physical chart.
    if rows is None:rows=json.loads((D/'brow-trace.json').read_text())['anchor_points']
    m=np.asarray(s.camera.matrix_world);g=bpy.context.evaluated_depsgraph_get()
    P=np.asarray(s.camera.calc_matrix_camera(g,x=1254,y=1254))
    o=s.objects['Knight | '+HEAD];t=BVHTree.FromObject(o,g);inv=o.matrix_world.inverted()
    direction=inv.to_3x3()@(s.camera.matrix_world.to_quaternion()@Vector((0,0,-1)))
    out=[]
    for px,py in rows:
        start=Vector((m@np.array([((px*2/1254-1)-P[0,3])/P[0,0],((1-py*2/1254)-P[1,3])/P[1,1],0,1]))[:3])
        hit=t.ray_cast(inv@start,direction)[0]
        if hit is None:continue
        xyz=rest_coords(np.asarray(o.matrix_world@hit)[None,:],pose(s))
        u,v=chart(xyz);out.append([px,py,round(float(u[0]),5),round(float(v[0]),5),round(float(xyz[0,1]),5)])
    return out
def run(key):
    bpy.ops.wm.open_mainfile(filepath=str(D/(key+'.blend')),load_ui=False);s=bpy.context.scene
    u,v,f=get_surface(s);np.savez_compressed(D/f'field-{key}.npz',u=u,v=v,surfaces=f)
    p=probe(s);(D/f'brow-{key}.json').write_text(json.dumps(p,indent=2)+'\n')
    q=probe(s,json.loads((D/'lower-trace.json').read_text())['anchors'])
    (D/f'lower-{key}.json').write_text(json.dumps(q,indent=2)+'\n')
    print(p)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])
