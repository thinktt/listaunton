"""Adjust base varnish locally, keeping one usable material on the closed model."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from render_regions import controls,regenerate
from base_reflection_trial import main as render_trial
def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;objects=controls(s)
    for ob in objects:
        values=np.zeros(len(ob.data.vertices),dtype=np.float32)
        if 'body' in ob.name:
            ring=np.arange(len(values))//96;t=np.clip((ring-18)/4,0,1);values[:]=1-t*t*(3-2*t)
        attr=ob.data.attributes.get('Base finish mask') or ob.data.attributes.new('Base finish mask','FLOAT','POINT');attr.data.foreach_set('value',values)
    mat=objects[0].data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Principled BSDF'];attr=n.new('ShaderNodeAttribute');attr.attribute_name='Base finish mask'
    changes=[(bs.inputs['Roughness'],cfg['roughness']),(bs.inputs['Coat Roughness'],cfg['coat_roughness']),(n['Fine varnish relief'].inputs['Strength'],cfg['coat_relief_strength'])]
    for socket,value in changes:
        assert not socket.is_linked
        node=n.new('ShaderNodeMapRange');node.label='Local base '+socket.name;node.inputs['From Min'].default_value=0;node.inputs['From Max'].default_value=1;node.inputs['To Min'].default_value=socket.default_value;node.inputs['To Max'].default_value=value;l.new(attr.outputs['Fac'],node.inputs['Value']);l.new(node.outputs['Result'],socket)
    regenerate(s);out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rendercfg=dict(cfg);rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256((out/'prepared.blend').read_bytes()).hexdigest(),original_material_source=cfg['source'],original_material_source_sha256=digest);render_trial(rendercfg)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(a.config).read_text(encoding='utf-8')))
