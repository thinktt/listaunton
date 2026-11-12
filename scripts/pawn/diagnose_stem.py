"""Isolate the lighting responsible for the stem/socket residuals."""
import argparse,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source
from mission_render import BUILD,render,save_json,sha


def run(cfg):
    scene,body=open_source(cfg);out=BUILD/cfg['measurement'];out.mkdir(parents=True,exist_ok=True)
    x0,y0,x1,y1=cfg['crop'];scene.render.use_border=True;scene.render.use_crop_to_border=False
    scene.render.border_min_x=x0/1254;scene.render.border_max_x=x1/1254
    scene.render.border_min_y=1-y1/1254;scene.render.border_max_y=1-y0/1254
    lamps=[o for o in scene.objects if o.type=='LIGHT'];powers={o.name:o.data.energy for o in lamps}
    groups={'socket':[o for o in lamps if o.name.startswith('Socket')],
            'base':[o for o in lamps if o.name.startswith('Base')],
            'collar':[o for o in lamps if 'collar' in o.name.lower()],
            'head':[o for o in lamps if 'head glint' in o.name.lower() or 'polish core' in o.name.lower()],
            'flare':[o for o in lamps if o.name.startswith('Flare')],
            'diffuse':[o for o in lamps if o.visible_diffuse]}
    if cfg.get('groups'):
        groups={key:[scene.objects[name] for name in names] for key,names in cfg['groups'].items()}
    record={'config':cfg,'lights':[{'name':o.name,'power':o.data.energy,'color':list(o.data.color),
                                   'diffuse':o.visible_diffuse,'glossy':o.visible_glossy} for o in lamps],
            'groups':{k:[o.name for o in v] for k,v in groups.items()},'renders':{}}
    path=out/'all.png';render(scene,path);record['renders']['all']=sha(path)
    for key,objects in groups.items():
        for o in objects:o.data.energy=0
        path=out/('without-'+key+'.png');render(scene,path);record['renders']['without-'+key]=sha(path)
        for o in objects:o.data.energy=powers[o.name]
    if cfg.get('include_world'):
        socket=scene.world.node_tree.nodes['Background'].inputs['Strength'];old_world=socket.default_value
        socket.default_value=0;path=out/'without-world.png';render(scene,path)
        record['renders']['without-world']=sha(path);socket.default_value=old_world
    old=scene.cycles.glossy_bounces;scene.cycles.glossy_bounces=0
    path=out/'direct-gloss-only.png';render(scene,path);record['renders']['direct-gloss-only']=sha(path)
    scene.cycles.glossy_bounces=old
    save_json(out/'measurement.json',record)
    print('Stem isolation complete; accepted scene was not saved or changed.',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(json.loads(a.config.read_text(encoding='utf8')))
