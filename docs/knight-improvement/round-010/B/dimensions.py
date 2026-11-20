from pathlib import Path
import sys,json
import bpy,numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D))
from carve import sculpt,DESIGNS,load
from mission_scene import visible_meshes

def height(scene):
    dg=bpy.context.evaluated_depsgraph_get()
    bounds={}
    for ob in visible_meshes(scene):
        ev=ob.evaluated_get(dg);mesh=ev.to_mesh()
        points=np.empty((len(mesh.vertices),3),np.float32)
        mesh.vertices.foreach_get('co',points.ravel())
        wm=np.asarray(ev.matrix_world)
        z=points@wm[2,:3]+wm[2,3]
        bounds[ob.name.split(' | ')[-1]]=[float(z.min()),float(z.max())]
        ev.to_mesh_clear()
    return {'height':max(v[1] for v in bounds.values())-min(v[0] for v in bounds.values()),
            'tops':{k:bounds[k][1] for k in ('swept rounded mane','near swept ear','far swept ear','continuous horse head and neck')}}
if __name__=='__main__':
    data={}
    tests=map(int,sys.argv[sys.argv.index('--')+1:])
    for i in tests:
        scene=load('parent.blend')
        if i>=0:sculpt(scene,DESIGNS[i])
        data[str(i)]=height(scene)
        print('HEIGHT',i,data[str(i)],flush=True)
    (D/'trial-physical-height.json').write_text(json.dumps(data,indent=2)+'\n')
