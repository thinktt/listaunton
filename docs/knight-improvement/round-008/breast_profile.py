"""Slice the actual untwisted chest across both sides and down its center."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
import numpy as np
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser()
p.add_argument('root',type=Path);p.add_argument('scene',type=Path);p.add_argument('out',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(a.root.resolve()/'scripts/knight'))
from lower_carving_fit import rest_coords
bpy.ops.wm.open_mainfile(filepath=str(a.scene.resolve()),load_ui=False)
s=bpy.context.scene
info=json.loads(s['knight_mission_pose'])
pose=[info[k] for k in ('dx','dy','twist_degrees')]
dg=bpy.context.evaluated_depsgraph_get()
obj=s.objects['Knight | continuous horse head and neck'].evaluated_get(dg)
me=obj.to_mesh()
try:
    coords=np.empty((len(me.vertices),3),np.float32)
    me.vertices.foreach_get('co',coords.ravel())
    mx=np.asarray(obj.matrix_world)
    vs=rest_coords(coords@mx[:3,:3].T+mx[:3,3],pose)
    me.calc_loop_triangles()
    tri=np.empty((len(me.loop_triangles),3),np.int32)
    me.loop_triangles.foreach_get('vertices',tri.ravel())
    tree=BVHTree.FromPolygons(vs.tolist(),tri.tolist(),all_triangles=True)
finally:
    obj.to_mesh_clear()
def front(y,z):
    point=tree.ray_cast((4,float(y),float(z)),(-1,0,0),8)[0]
    return round(float(point.x),5) if point is not None and point.x>0 else None
widths=np.linspace(-.85,.85,171)
levels=np.linspace(1.76,3.1,135)
profiles={f'{z:.2f}':[[round(float(y),3),v] for y in widths if (v:=front(y,z)) is not None] for z in (1.92,2.12,2.36,2.58,2.84)}
center=[[round(float(z),3),v] for z in levels if (v:=front(0,z)) is not None]
report={'source_sha256':hashlib.sha256(a.scene.read_bytes()).hexdigest(),'pose':pose,'method':'First hit on the evaluated untwisted head and neck looking rearward from +X. Rows give [lateral coordinate, anterior coordinate] for transverse sections and [height, anterior coordinate] for the center profile.','horizontal':profiles,'center':center}
a.out.parent.mkdir(exist_ok=True,parents=True)
a.out.write_text(json.dumps(report,indent=2)+'\n')
print(report['source_sha256'],[(k,len(v)) for k,v in profiles.items()])
