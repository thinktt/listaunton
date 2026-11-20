"""Report real surface normals and geometric reflected rays at foot landmarks."""
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source
from mission_render import ROOT,Surface,save_json

def run(cfg,output):
    scene,body=open_source(cfg);surface=Surface(scene,body);rows=[]
    points=cfg.get('pixels',[(560,y) for y in [932,935,937,939,941,942,943,945,948,952,956]])
    for x,y in points:
        pos,normal=surface.hit(x,y);ray=(-surface.back).reflect(normal)
        occluder,_,_,distance=surface.tree.ray_cast(pos+normal*.0001,ray,10)
        rows.append({'pixel':[x,y],'position':list(pos),'normal':list(normal),'reflected_ray':list(ray),
                     'occluded':occluder is not None,'occluder_distance':distance})
    nodes=body.data.materials[0].node_tree.nodes
    ramps={n.name:[[e.position,*e.color] for e in n.color_ramp.elements] for n in nodes if n.type=='VALTORGB'}
    report={'source':cfg['source'],'source_sha256':cfg['source_sha256'],'rays':rows,'ramps':ramps,
            'profile_xyz':[list(v.co) for v in list(body.data.vertices)[::96]],
            'lights':[{'name':o.name,'position':list(o.location),'energy':o.data.energy,'color':list(o.data.color)} for o in scene.objects if o.type=='LIGHT' and o.name.startswith('Foot')],
            'note':'Smooth geometric normals. The actual material also adds bounded wood relief; use actual renders to judge reflection placement.'}
    output.parent.mkdir(parents=True,exist_ok=True);save_json(output,report)
    print('Groove-ray inspection saved:',output,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(json.loads(a.config.read_text(encoding='utf8')),ROOT/a.output)
