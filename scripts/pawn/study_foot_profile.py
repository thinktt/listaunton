"""Render small meridian alternatives with the current foot finish held fixed."""
import argparse,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source
from mission_render import BUILD,render,save_json,sha
from shape_trial import edit

def run(cfg):
    scene,body=open_source(cfg);out=BUILD/cfg['measurement'];out.mkdir(parents=True,exist_ok=True)
    original=np.array([v.co[:] for v in body.data.vertices],dtype=np.float32)
    x0,y0,x1,y1=cfg['crop'];scene.render.use_border=True;scene.render.use_crop_to_border=False
    scene.render.border_min_x=x0/1254;scene.render.border_max_x=x1/1254
    scene.render.border_min_y=1-y1/1254;scene.render.border_max_y=1-y0/1254
    report={'config':cfg,'renders':{},'edited_controls':{},'note':'Cropped geometry diagnosis under unchanged material, lights and camera. A full model render and original-sprite audit are required before acceptance.'}
    for row in cfg['poses']:
        body.data.vertices.foreach_set('co',original.ravel());body.data.update();edit(body,row['profiles'])
        path=out/(row['name']+'.png');render(scene,path);report['renders'][row['name']]=sha(path)
        report['edited_controls'][row['name']]={key:list(body.data.vertices[int(key)*96].co) for key in row['profiles']}
    save_json(out/'measurement.json',report)
    print('Foot profile study complete; accepted scene was not saved.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(json.loads(a.config.read_text(encoding='utf8')))
