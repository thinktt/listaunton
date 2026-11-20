"""Carving-coordinate sections of the forehead, ear seat and paired mane shoulders."""
from pathlib import Path
import json,sys
import numpy as np
import bpy
from mathutils.bvhtree import BVHTree
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from lower_carving_fit import rest_coords
from mission_scene import world_vertices
def rest_tree(scene,pose,suffix):
    src=scene.objects['Knight | '+suffix]
    ev=src.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    coords=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',coords.ravel())
    mat=np.asarray(src.matrix_world);coords=rest_coords(coords@mat[:3,:3].T+mat[:3,3],pose)
    me.calc_loop_triangles();tris=np.empty((len(me.loop_triangles),3),np.int32)
    me.loop_triangles.foreach_get('vertices',tris.ravel())
    tree=BVHTree.FromPolygons(coords.tolist(),tris.tolist(),all_triangles=True)
    ev.to_mesh_clear()
    return tree
def skull_profile(scene,pose,suffix='continuous horse head and neck'):
    tree=rest_tree(scene,pose,suffix)
    def depth(points):
        depths=[]
        for x,y,z in points:
            pair=[tree.ray_cast((x,3*s,z),(0,-s,0))[0] for s in (-1,1)]
            depths.append(np.nan if any(h is None for h in pair) else (pair[1].y-pair[0].y)*.5)
        return np.array(depths)
    return depth
if __name__=='__main__':
    bpy.ops.wm.open_mainfile(filepath=str(D/'parent.blend'),load_ui=False)
    s=bpy.context.scene;q=json.loads(s['knight_mission_pose']);pose=[q[k] for k in ('dx','dy','twist_degrees')]
    depth=skull_profile(s,pose)
    for suffix in ['swept rounded mane','far swept ear']:
        a=rest_coords(world_vertices(s.objects['Knight | '+suffix]),pose).reshape(-1,64,3)
        y=depth(a.reshape(-1,3)).reshape(a.shape[:2])
        print(suffix,'thickness along Y above the forehead at every fourth lane',flush=True)
        print(np.round((abs(a[:,:,1])-y)[:7,::4],3))
