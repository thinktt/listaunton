"""Reshape specified real reflector cards from fixed-view surface landmarks."""
import argparse,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import Surface
from polish_trial import open_source,save_trial
from fit_lighting import shape


def apply(scene,body,cfg):
    surface=Surface(scene,body);record=[]
    for spec in cfg['reflectors']:
        ob=scene.objects[spec['name']];d=ob.data
        assert ob.type=='LIGHT' and d.type=='AREA' and d.shape=='ELLIPSE'
        assert not ob.visible_diffuse and ob.visible_glossy
        before={'position':list(ob.location),'rotation':list(ob.rotation_euler),'size':d.size,'size_y':d.size_y,
                'spread':d.spread,'energy':d.energy,'color':list(d.color)}
        row=shape(surface,spec);ob.location=row['position'];ob.rotation_euler=row['rotation']
        d.size=row['size'];d.size_y=row['size_y']
        import math
        d.spread=math.radians(row['spread']);d.color=row['color'];d.energy=before['energy']*spec.get('energy_gain',1)
        record.append({'specification':spec,'before':before,'after':{**row,'energy':d.energy}})
    scene['pawn_reshaped_reflectors']=json.dumps(record,sort_keys=True)
    return record


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(a.config.read_text(encoding='utf8'))
    scene,body=open_source(cfg);print(json.dumps(apply(scene,body,cfg)),flush=True);save_trial(scene,cfg)
