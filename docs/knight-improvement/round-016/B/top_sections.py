"""Measure transverse profiles across the actual crown of the mane and the head beneath it."""
from pathlib import Path
import argparse,hashlib,json,sys
sys.dont_write_bytecode=True
import bpy
import numpy as np
from mathutils.bvhtree import BVHTree

parser=argparse.ArgumentParser()
parser.add_argument('root',type=Path)
parser.add_argument('model',type=Path)
parser.add_argument('out',type=Path)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(args.root.resolve()/'scripts/knight'))
from lower_carving_fit import rest_coords
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
source=sha(args.model)
bpy.ops.wm.open_mainfile(filepath=str(args.model.resolve()),load_ui=False)
scene=bpy.context.scene
p=json.loads(scene['knight_mission_pose'])
pose=[p[k] for k in ('dx','dy','twist_degrees')]
deps=bpy.context.evaluated_depsgraph_get()
def tree(name):
    obj=scene.objects['Knight | '+name].evaluated_get(deps)
    mesh=obj.to_mesh()
    try:
        xyz=np.empty(len(mesh.vertices)*3,np.float32)
        mesh.vertices.foreach_get('co',xyz)
        m=np.array(obj.matrix_world)
        xyz=rest_coords(xyz.reshape(-1,3)@m[:3,:3].T+m[:3,3],pose)
        mesh.calc_loop_triangles()
        tris=np.empty(len(mesh.loop_triangles)*3,np.int32)
        mesh.loop_triangles.foreach_get('vertices',tris)
        return BVHTree.FromPolygons(xyz.tolist(),tris.reshape(-1,3).tolist(),all_triangles=True)
    finally:
        obj.to_mesh_clear()
def top(mesh,x,y):
    pt=mesh.ray_cast((x,y,6),(0,0,-1),1.52)[0]
    return round(float(pt.z),5) if pt is not None else None
parts={'mane':'swept rounded mane','head':'continuous horse head and neck','near ear':'near swept ear','far ear':'far swept ear'}
trees={k:tree(label) for k,label in parts.items()}
profiles={}
for x in (-.8,-.6,-.4,-.2,0,.14):
    section=[]
    for iy in range(-65,66):
        y=iy/100
        hits={k:z for k,t in trees.items() if (z:=top(t,x,y)) is not None}
        if hits:section.append({'y':y,'top':max(hits,key=hits.get),'surfaces':hits})
    profiles[x]=section
assert sha(args.model)==source
args.out.parent.mkdir(exist_ok=True,parents=True)
args.out.write_text(json.dumps({'source_sha256':source,'pose':pose,'method':'Downward rays on the native evaluated meshes after undoing the whole-head pose. Six fixed stations along the length of the poll. Samples give lateral position, surface heights and the foremost surface from above. A 0.01 model-unit step resolves the major ridges, narrower bevels may fall between steps.','profiles':profiles},indent=2)+'\n')
print({x:len(cut) for x,cut in profiles.items()})
