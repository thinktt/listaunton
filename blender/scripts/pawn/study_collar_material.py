"""Separate collar pigment, geometry and studio shading without saving a model."""
import argparse,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source
from mission_render import BUILD,Surface,area,render,save_json,sha

def run(cfg):
    scene,body=open_source(cfg);out=BUILD/cfg['measurement'];out.mkdir(parents=True,exist_ok=True)
    x0,y0,x1,y1=cfg['crop'];scene.render.use_border=True;scene.render.use_crop_to_border=False
    scene.render.border_min_x=x0/1254;scene.render.border_max_x=x1/1254
    scene.render.border_min_y=1-y1/1254;scene.render.border_max_y=1-y0/1254
    surface=Surface(scene,body);rays=[]
    for x,y in cfg['pixels']:
        try:
            p,n=surface.hit(x,y);rays.append({'pixel':[x,y],'position':list(p),'normal':list(n),'reflected_ray':list((-surface.back).reflect(n))})
        except ValueError:rays.append({'pixel':[x,y],'miss':True})
    record={'config':cfg,'rays':rays,'renders':{},'note':'Pigment emission is an inspection pass only, not a replacement shaded model. Neutral clay omits wood relief. No accepted scene is saved.'}
    def capture(name):
        path=out/(name+'.png');render(scene,path);record['renders'][name]=sha(path)
    capture('baseline')
    material=body.data.materials[0];nodes=material.node_tree.nodes;links=material.node_tree.links
    output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
    previous=output.inputs['Surface'].links[0].from_socket
    emission=nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=1
    links.new(nodes['Pawn walnut pigment'].outputs['Color'],emission.inputs['Color'])
    links.new(emission.outputs[0],output.inputs['Surface']);capture('pigment-only')
    links.new(previous,output.inputs['Surface']);nodes.remove(emission)
    clay=bpy.data.materials.new('Collar shape diagnosis');clay.use_nodes=True
    bs=clay.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.3,.3,.3,1);bs.inputs['Roughness'].default_value=.45
    body.data.materials[0]=clay;capture('clay-studio')
    for lamp in list(scene.objects):
        if lamp.type=='LIGHT':bpy.data.objects.remove(lamp,do_unlink=True)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.28
    area(scene,'Broad neutral inspection light',(0,-4,5),(0,0,1.9),250,3.2,color=(1,1,1))
    capture('clay-neutral');save_json(out/'measurement.json',record)
    print('Collar material/shape inspection complete; no accepted assets changed.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    run(json.loads(a.config.read_text(encoding='utf8')))
