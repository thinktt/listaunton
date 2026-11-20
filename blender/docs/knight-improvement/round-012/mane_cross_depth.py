"""Measure the frontmost physical surface across the long mane-to-neck hollow."""
from pathlib import Path
import hashlib,json,sys
import bpy,numpy as np
from mathutils import Vector
root,scene_file,source_trace,dest=map(Path,sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(root.resolve()/'scripts/knight'))
from probe_carving import point_probe
bpy.ops.wm.open_mainfile(filepath=str(scene_file.resolve()),load_ui=False)
scene=bpy.context.scene
probe=point_probe(scene)
src=json.loads(source_trace.read_bytes())
rows={y:x for y,x,_,_ in src['Black 2']['samples']}
cam=scene.camera.matrix_world.to_quaternion()
right=cam@Vector((1,0,0));forward=cam@Vector((0,0,-1))
records={}
for y in [460,484,508,532,556,580,604,628]:
    cx=rows[y];row=[]
    for x in range(cx-58,cx+74):
        hit=probe(x+.5,y+.5)
        if hit is None:
            row.append([x,None,None,None,None])
        else:
            _,name,pt,normal=hit
            depth=forward.dot(pt-scene.camera.matrix_world.translation)
            row.append([x,round(depth,5),round(right.dot(normal),4),round(-forward.dot(normal),4),name.removeprefix('Knight | ')])
    records[str(y)]={'reference_shadow_x':cx,'rays':row}
dest.parent.mkdir(exist_ok=True,parents=True)
dest.write_text(json.dumps({'source_sha256':hashlib.sha256(scene_file.read_bytes()).hexdigest(),'trace_sha256':hashlib.sha256(source_trace.read_bytes()).hexdigest(),'rows':records,'method':'Nearest visible native mesh for each reference-camera ray. Distances increase away from the camera. Normals are recorded along camera right and toward the camera. A local recess can be cut in one part or at a junction between parts.'},indent=2)+'\n')
