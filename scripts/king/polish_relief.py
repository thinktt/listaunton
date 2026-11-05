"""Apply fine pigment relief to the varnish while preserving the base BSDF."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run,meshes

def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    mat=meshes(s)[0].data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links
    base=n['Pigment microrelief'];coat=n.new('ShaderNodeBump');coat.name='Fine varnish relief'
    l.new(base.inputs['Height'].links[0].from_socket,coat.inputs['Height'])
    coat.inputs['Strength'].default_value=cfg['strength'];coat.inputs['Distance'].default_value=cfg['distance']
    l.new(coat.outputs['Normal'],n['Principled BSDF'].inputs['Coat Normal'])
    for name,factor in cfg.get('light_multipliers',{}).items():bpy.data.objects[name].data.energy*=factor
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(exist_ok=True,parents=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rendercfg={k:v for k,v in cfg.items() if k!='source_sha256'};rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),original_source=cfg['source'],original_source_sha256=digest)
    run(rendercfg)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(args.config).read_text(encoding='utf-8')))
