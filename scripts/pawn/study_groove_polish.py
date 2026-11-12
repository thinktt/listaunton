"""Diagnose the existing groove-polish mask separately from its low reflector."""
import argparse,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source
from mission_render import BUILD,render,save_json,sha

def apply_knots(body,rows):
    ramp=body.data.materials[0].node_tree.nodes['Polish accessible to the lathe groove'].color_ramp
    for row in rows:
        element=min(ramp.elements,key=lambda e:abs(e.position-row['position']))
        assert abs(element.position-row['position'])<1e-6
        element.color=(*([row['gain']]*3),1)

def run(cfg):
    scene,body=open_source(cfg);out=BUILD/cfg['measurement'];out.mkdir(parents=True,exist_ok=True)
    x0,y0,x1,y1=cfg['crop'];scene.render.use_border=True;scene.render.use_crop_to_border=False
    scene.render.border_min_x=x0/1254;scene.render.border_max_x=x1/1254
    scene.render.border_min_y=1-y1/1254;scene.render.border_max_y=1-y0/1254
    ramp=body.data.materials[0].node_tree.nodes['Polish accessible to the lathe groove'].color_ramp
    old=[{'position':e.position,'gain':e.color[0]} for e in ramp.elements]
    lamp=scene.objects[cfg['light']];power=lamp.data.energy;record={'config':cfg,'baseline_knots':old,'renders':{}}
    for row in cfg['poses']:
        apply_knots(body,old);apply_knots(body,row.get('knots',[]));lamp.data.energy=power*row.get('energy_gain',1)
        path=out/(row['name']+'.png');render(scene,path);record['renders'][row['name']]=sha(path)
    save_json(out/'measurement.json',record)
    print('Groove diagnostic complete; no scene saved.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(json.loads(a.config.read_text(encoding='utf8')))
