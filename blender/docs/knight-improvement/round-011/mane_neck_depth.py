"""Compare the two saved surfaces underneath the source shadow at the registered camera."""
from pathlib import Path
import hashlib,json,sys
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root,model,out=map(Path,sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(root.resolve()/'scripts/knight'))
from probe_carving import rest
bpy.ops.wm.open_mainfile(filepath=str(model.resolve()),load_ui=False)
s=bpy.context.scene
pose=json.loads(s['knight_mission_pose'])
cam=s.camera;graph=bpy.context.evaluated_depsgraph_get()
matrix=np.asarray(cam.matrix_world);proj=np.asarray(cam.calc_matrix_camera(graph,x=1254,y=1254))
ray=cam.matrix_world.to_quaternion()@Vector((0,0,-1))
parts={}
for key,name in [('mane','Knight | swept rounded mane'),('head','Knight | continuous horse head and neck')]:
    obj=s.objects[name]
    parts[key]=(obj.matrix_world,obj.matrix_world.inverted(),BVHTree.FromObject(obj,graph))
def surfaces(x,y):
    camera_start=[((2*(x+.5)/1254-1)-proj[0,3])/proj[0,0],((1-2*(y+.5)/1254)-proj[1,3])/proj[1,1],0,1]
    start=Vector((matrix@camera_start)[:3]);hits={}
    for key,(mat,inv,tree) in parts.items():
        loc,normal,_,_=tree.ray_cast(inv@start,inv.to_3x3()@ray)
        if loc is None:continue
        pos=mat@loc
        hits[key]={'depth':round((pos-start).length,4),'pre_pose':[round(c,4) for c in rest(pos,pose)]}
    return hits
rows=json.loads((out/'mane-hollow.json').read_bytes())['Black 2']['samples']
record=[]
for y,target,current,lum in rows[::8]:
    samples={}
    for label,x in [('source_left',target-10),('source_shadow',target),('source_right',target+10),('model_edge',current)]:
        samples[label]={'x':x,'hits':surfaces(x,y)}
    record.append({'y':y,'samples':samples})
    hits=samples['source_shadow']['hits']
    dz=round(hits['head']['depth']-hits['mane']['depth'],4) if len(hits)==2 else None
    print(y,target,current,dz)
(out/'mane-neck-depth.json').write_text(json.dumps({'model':hashlib.sha256(model.read_bytes()).hexdigest(),'note':'Distances along the registered camera ray. Positive head depth minus mane depth means the mane surface lies in front of the neck. The source shadow is a visual landmark and has no measured physical depth.','sections':record},indent=2)+'\n')
