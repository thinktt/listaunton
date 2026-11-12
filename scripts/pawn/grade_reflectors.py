"""Change measured reflector colors by explicit linear RGB gains."""
import argparse,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source,save_trial


def apply(scene,cfg):
    report=[]
    for entry in cfg['reflector_grades']:
        lamp=scene.objects[entry['name']]
        assert lamp.type=='LIGHT' and lamp.visible_glossy and not lamp.visible_diffuse
        old={'energy':lamp.data.energy,'color':list(lamp.data.color)}
        color=[x*y for x,y in zip(old['color'],entry['linear_rgb_gain'])]
        scale=max(color)
        lamp.data.color=[x/scale for x in color];lamp.data.energy=old['energy']*scale
        report.append({'name':lamp.name,'before':old,
                       'after':{'energy':lamp.data.energy,'color':list(lamp.data.color)}})
    scene['pawn_reflector_grades']=json.dumps(report,sort_keys=True)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(a.config.read_text(encoding='utf8'))
    scene,body=open_source(cfg);report=apply(scene,cfg)
    print(json.dumps(report),flush=True);save_trial(scene,cfg)
