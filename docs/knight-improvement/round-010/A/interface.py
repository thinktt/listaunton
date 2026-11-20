"""Map the frontmost physical part at the forehead interface in both cameras."""
from pathlib import Path
import json,sys
import numpy as np
import bpy
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from mission_scene import use_side_camera,sha
from probe_carving import point_probe,rest
def main():
    label='candidate' if '--candidate' in sys.argv else 'parent'
    source=D/('knight.blend' if label=='candidate' else 'parent.blend')
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;pose=json.loads(s['knight_mission_pose'])
    meta={'source_sha256':sha(source)};images={}
    names=['swept rounded mane','near swept ear','far swept ear','continuous horse head and neck']
    for key,box,step in [('fixed',[250,280,515,426],2),('side',[300,96,748,340],3)]:
        if key=='side':use_side_camera(s)
        probe=point_probe(s);x,y,u,v=box
        xs=np.arange(x,u,step);ys=np.arange(y,v,step)
        ids=np.zeros((len(ys),len(xs)),np.int8);xyz=np.zeros((*ids.shape,3),np.float32)
        for j,yy in enumerate(ys):
            for i,xx in enumerate(xs):
                h=probe(xx+.5,yy+.5)
                if h:
                    name=h[1].split(' | ')[-1];ids[j,i]=1+names.index(name) if name in names else 5
                    xyz[j,i]=rest(h[2],pose)
        images[key]=ids;images[key+'-rest']=xyz;meta[key]={'box':box,'step':step,'names':names}
    np.savez_compressed(D/(label+'-interface.npz'),**images)
    (D/(label+'-interface.json')).write_text(json.dumps(meta,indent=2))
if __name__=='__main__':main()
