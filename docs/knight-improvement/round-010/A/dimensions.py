"""Bind the evaluated dimensions to the two saved scenes in head-rest coordinates."""
from pathlib import Path
import json,sys,hashlib
import bpy,numpy as np
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from lower_carving_fit import rest_coords
from mission_scene import visible_meshes
report={}
for tag,source in [('parent',D/'parent.blend'),('candidate',D/'knight.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;p=json.loads(s['knight_mission_pose'])
    pose=[p[k] for k in ('dx','dy','twist_degrees')];g=bpy.context.evaluated_depsgraph_get()
    data={'source':hashlib.sha256(source.read_bytes()).hexdigest(),'parts':{}};full=[]
    for obj in visible_meshes(s):
        ev=obj.evaluated_get(g);me=ev.to_mesh();xs=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',xs.ravel())
        mat=np.asarray(ev.matrix_world);w=xs@mat[:3,:3].T+mat[:3,3];full.append(w)
        if 'mane' in obj.name or 'swept ear' in obj.name:
            v=rest_coords(w,pose)
            data['parts'][obj.name]={'rest_min':v.min(0).tolist(),'rest_max':v.max(0).tolist(),'rest_dimensions':np.ptp(v,axis=0).tolist()}
        ev.to_mesh_clear()
    world=np.vstack(full);data['world_dimensions']=np.ptp(world,axis=0).tolist();report[tag]=data
(D/'dimensions.json').write_text(json.dumps(report,indent=2)+'\n')
print([(k,v['world_dimensions'],v['parts']['Knight | swept rounded mane']['rest_dimensions']) for k,v in report.items()])
