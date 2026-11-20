"""Measure the front and side of the frozen breast in the untwisted model."""
from pathlib import Path
import json
import sys
import numpy as np
import bpy
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parents[2]/'scripts/knight'))
from lower_carving_fit import rest_coords

def sections(file):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/file),load_ui=False)
    s=bpy.context.scene
    pose=json.loads(s['knight_mission_pose'])
    ev=s.objects['Knight | continuous horse head and neck'].evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=ev.to_mesh()
    try:
        v=np.empty((len(mesh.vertices),3),np.float32)
        mesh.vertices.foreach_get('co',v.ravel())
        m=np.asarray(ev.matrix_world)
        p=rest_coords(v@m[:3,:3].T+m[:3,3],[pose[k] for k in ('dx','dy','twist_degrees')])
        mesh.calc_loop_triangles()
        tri=np.empty((len(mesh.loop_triangles),3),np.int32)
        mesh.loop_triangles.foreach_get('vertices',tri.ravel())
        tree=BVHTree.FromPolygons(p.tolist(),tri.tolist(),all_triangles=True)
    finally:
        ev.to_mesh_clear()
    out={}
    for z in np.arange(1.7,3.02,.02):
        rays=[]
        for y in np.arange(0,.901,.01):
            hit,normal,ix,dist=tree.ray_cast((4.,-y,z),(-1.,0,0),7)
            if hit is None or hit.x<0:continue
            rays.append([round(float(y),2),round(hit.x,5),[round(x,4) for x in normal]])
        if rays:
            out[f'{z:.2f}']=rays
    return out
if __name__=='__main__':
    a=sections('parent.blend')
    b=sections('knight.blend')
    data={}
    for z in a:
        if z not in b:continue
        before={s[0]:s for s in a[z]}
        after={s[0]:s for s in b[z]}
        tip=max(a[z],key=lambda s:s[1])
        tip2=max(b[z],key=lambda s:s[1])
        shared=sorted(set(before)&set(after))
        angular=[]
        for y in shared:
            if .3<y<.73:
                aa,bb=[np.array(t[y][2]) for t in (before,after)]
                angular.append((np.degrees(np.arccos(np.clip(aa@bb/(np.linalg.norm(aa)*np.linalg.norm(bb)),-1,1))),y))
        data[z]={'maximum_anterior_x_parent_B':[tip[1],tip2[1]],'where_abs_y':[tip[0],tip2[0]],
             'sagittal_x_parent_B':[before[0][1],after[0][1]],
             'change_across_flank_y_0_to_0_7':{y:round(after[y][1]-before[y][1],4) for y in shared if round(y*100)%10==0 and y<.75},
             'greatest_normal_change_degrees_at_abs_y':list(np.round(max(angular),3)) if angular else []}
    (OUT/'breast-sections.json').write_text(json.dumps(data,indent=2)+'\n')
    for z in ['1.84','1.94','2.04','2.14','2.24','2.34','2.44','2.54']:
        print(z,data[z],flush=True)
