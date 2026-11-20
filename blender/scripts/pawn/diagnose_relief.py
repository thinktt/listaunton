"""Render separate normal-layer ablations without changing the saved pawn."""
import argparse, json, sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source
from mission_render import BUILD, render, save_json, sha
from validate_contact_checkpoint import graph

def run(cfg):
    scene,body=open_source(cfg)
    out=BUILD/cfg['measurement'];out.mkdir(parents=True,exist_ok=True)
    x0,y0,x1,y1=cfg['crop']
    scene.render.use_border=True;scene.render.use_crop_to_border=False
    scene.render.border_min_x=x0/1254;scene.render.border_max_x=x1/1254
    scene.render.border_min_y=1-y1/1254;scene.render.border_max_y=1-y0/1254
    nodes=body.data.materials[0].node_tree.nodes
    layers=[n for n in nodes if n.type=='BUMP' or (n.type=='NORMAL_MAP' and n.inputs['Color'].is_linked)]
    strengths={n.name:n.inputs['Strength'].default_value for n in layers}
    output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
    live=output.inputs['Surface'].links[0].from_socket
    original=graph(live,ignored_images=())
    poses={'baseline':{},**{n.name:{n.name:0} for n in layers},'all-relief-off':{n.name:0 for n in layers}}
    record={'config':cfg,'layer_strengths':strengths,'poses':poses,'renders':{},'material_graph':original}
    for index,(name,changes) in enumerate(poses.items()):
        for n in layers:n.inputs['Strength'].default_value=changes.get(n.name,strengths[n.name])
        path=out/(str(index).zfill(2)+'.png');render(scene,path)
        record['renders'][name]={'file':path.name,'sha256':sha(path)}
    for n in layers:n.inputs['Strength'].default_value=strengths[n.name]
    assert graph(live,ignored_images=())==original
    save_json(out/'measurement.json',record)
    print('RELIEF_DIAGNOSTIC_COMPLETE',cfg['measurement'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(json.loads(a.config.read_text(encoding='utf8')))
