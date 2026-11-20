"""Test spatially restricted groove reflections without changing accepted assets."""
import argparse,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source
from mission_render import BUILD,Surface,render,save_json,sha
from fit_lighting import shape,make_light
from study_groove_polish import apply_knots

def run(cfg):
    scene,body=open_source(cfg);out=BUILD/cfg['measurement'];out.mkdir(parents=True,exist_ok=True)
    surface=Surface(scene,body);x0,y0,x1,y1=cfg['crop']
    scene.render.use_border=True;scene.render.use_crop_to_border=False
    scene.render.border_min_x=x0/1254;scene.render.border_max_x=x1/1254
    scene.render.border_min_y=1-y1/1254;scene.render.border_max_y=1-y0/1254
    ramp=body.data.materials[0].node_tree.nodes['Polish accessible to the lathe groove'].color_ramp
    original=[{'position':e.position,'gain':e.color[0]} for e in ramp.elements]
    record={'config':cfg,'baseline_knots':original,'renders':{},'lights':{},
            'note':'Real area-light crops at fixed camera. No accepted asset is saved or replaced.'}
    for pose in cfg['poses']:
        apply_knots(body,original);apply_knots(body,pose.get('groove_knots',[]));light=None
        if 'landmark' in pose:
            row=shape(surface,pose['landmark']);row.update(pose['physical'])
            light=make_light(scene,row);record['lights'][pose['name']]=row
        path=out/(pose['name']+'.png');render(scene,path)
        record['renders'][pose['name']]=sha(path)
        if light is not None:bpy.data.objects.remove(light,do_unlink=True)
    save_json(out/'measurement.json',record)
    print('Inner-reflector study complete; accepted assets unchanged.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(json.loads(a.config.read_text(encoding='utf8')))
