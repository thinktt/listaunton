"""Layer local roughness onto the shared material without changing other regions."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run
from render_regions import controls,regenerate
def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;objects=controls(s)
    for light,power in cfg.get('existing_light_power',{}).items():bpy.data.objects[light].data.energy=power
    name=cfg['attribute'];start,end=cfg['ring_fade']
    for ob in objects:
        values=np.zeros(len(ob.data.vertices),dtype=np.float32)
        if 'body' in ob.name:
            ring=np.arange(len(values))//96
            t=np.clip((ring-start)/(end-start),0,1);values[:]=1-t*t*(3-2*t)
            if cfg.get('lower_fade'):
                lo,hi=cfg['lower_fade'];t=np.clip((ring-lo)/(hi-lo),0,1);values*=t*t*(3-2*t)
        attr=ob.data.attributes.get(name) or ob.data.attributes.new(name,'FLOAT','POINT');attr.data.foreach_set('value',values)
    mat=objects[0].data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;attr=n.new('ShaderNodeAttribute');attr.attribute_name=name
    for node_name,input_name,value in cfg['inputs']:
        socket=n[node_name].inputs[input_name];mix=n.new('ShaderNodeMixRGB');mix.label=name+' '+input_name;l.new(attr.outputs['Fac'],mix.inputs[0]);mix.inputs[2].default_value=(value,value,value,1)
        if socket.is_linked:l.new(socket.links[0].from_socket,mix.inputs[1])
        else:mix.inputs[1].default_value=(socket.default_value,)*3+(1,)
        l.new(mix.outputs[0],socket)
    regenerate(s);out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rendercfg=dict(cfg);rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256((out/'prepared.blend').read_bytes()).hexdigest(),original_source=cfg['source'],original_source_sha256=digest);run(rendercfg)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(a.config).read_text(encoding='utf-8-sig')))
