"""Extract native mane triangles, reserved UVs and fixed-camera physical sample positions."""
from pathlib import Path
import json, math, sys
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent; R=D.parents[2]
sys.path.insert(0,str(R/'scripts/knight'))
from lower_carving_fit import rest_coords
from mission_scene import visible_meshes
def main():
    bpy.ops.wm.open_mainfile(filepath=str(D/'parent.blend'),load_ui=False)
    s=bpy.context.scene; deps=bpy.context.evaluated_depsgraph_get()
    pose=json.loads(s['knight_mission_pose']); keys=['dx','dy','twist_degrees']
    out={}; protect=[]
    for obj in visible_meshes(s):
        ob=obj.evaluated_get(deps); m=ob.to_mesh();m.calc_loop_triangles()
        uv=np.empty((len(m.loops),2),np.float32);m.uv_layers['Knight wood atlas'].data.foreach_get('uv',uv.ravel())
        tri=np.empty((len(m.loop_triangles),3),np.int32);m.loop_triangles.foreach_get('loops',tri.ravel())
        if obj.name=='Knight | swept rounded mane':
            ids=np.empty(len(m.loops),np.int32);m.loops.foreach_get('vertex_index',ids)
            xyz=np.empty((len(m.vertices),3),np.float32);m.vertices.foreach_get('co',xyz.ravel())
            mat=np.array(ob.matrix_world);world=xyz@mat[:3,:3].T+mat[:3,3]
            rest=rest_coords(world,[pose[k] for k in keys]);out.update(uv=uv[tri],xyz=rest[ids[tri]].astype(np.float32))
            tree=BVHTree.FromPolygons(world.tolist(),ids[tri].tolist(),all_triangles=True)
            cam=s.camera;frame=cam.data.view_frame(scene=s);cw=cam.matrix_world
            origin=Vector((0,0,0));dir=(cw.to_quaternion()@Vector((0,0,-1))).normalized();samples=[]
            for y in range(365,690,15):
                for x in range(180,651,3):
                    corner=frame[2]+(frame[1]-frame[2])*((x+.5)/s.render.resolution_x)+(frame[3]-frame[2])*(1-(y+.5)/s.render.resolution_y)
                    point,normal,k,dist=tree.ray_cast(cw@Vector((corner.x,corner.y,.1)),dir)
                    if point is None:continue
                    q=rest_coords(np.array([point]),[pose[k] for k in keys])[0]
                    samples.append([x,y,*q])
            np.save(D/'fixed-native-samples.npy',np.array(samples))
        else:protect.append(uv[tri])
        ob.to_mesh_clear()
    out['reserved']=np.concatenate(protect)
    np.savez_compressed(D/'native-uv.npz',**out)
    print('mane triangles',len(out['uv']),'reserved',len(out['reserved']),'bounds',out['xyz'].reshape(-1,3).min(0),out['xyz'].reshape(-1,3).max(0))
if __name__=='__main__':main()
