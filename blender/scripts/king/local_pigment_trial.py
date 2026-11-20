"""Test a bounded linear pigment grade on real king material; references stay intact."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run
from render_regions import controls,regenerate


def mask_values(ob,cfg):
    values=np.zeros(len(ob.data.vertices),dtype=np.float32)
    if 'body' not in ob.name:return values
    co=np.array([v.co[:] for v in ob.data.vertices]);ring=np.arange(len(values))//96
    def fade(x,lo,hi):
        t=np.clip((x-lo)/(hi-lo),0,1);return t*t*(3-2*t)
    values[:]=fade(ring,*cfg['lower_fade'])*(1-fade(ring,*cfg['upper_fade']))
    radius=np.maximum(np.linalg.norm(co[:,:2],axis=1),1e-8);angle=np.degrees(np.arccos(np.clip(-co[:,1]/radius,-1,1)))
    values*=1-fade(angle,*cfg['angular_fade'])
    return values


def apply_grade(s,cfg):
    obs=controls(s);name=cfg['attribute']
    for ob in obs:
        assert not ob.data.attributes.get(name)
        attr=ob.data.attributes.new(name,'FLOAT','POINT');attr.data.foreach_set('value',mask_values(ob,cfg))
    mat=obs[0].data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes['Principled BSDF']
    old=bs.inputs['Base Color'].links[0].from_socket
    attr=nodes.new('ShaderNodeAttribute');attr.name=name+' mask';attr.attribute_name=name
    grade=nodes.new('ShaderNodeMixRGB');grade.name=name+' grade';grade.blend_type='MULTIPLY';grade.inputs[0].default_value=1
    links.new(old,grade.inputs[1]);grade.inputs[2].default_value=(*cfg['linear_multiplier'],1)
    mix=nodes.new('ShaderNodeMixRGB');mix.name=name+' blend';links.new(attr.outputs['Fac'],mix.inputs[0]);links.new(old,mix.inputs[1]);links.new(grade.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],bs.inputs['Base Color'])
    regenerate(s)
    return dict(attribute=name,linear_multiplier=cfg['linear_multiplier'],lower_fade=cfg['lower_fade'],upper_fade=cfg['upper_fade'],angular_fade=cfg['angular_fade'],geometry_lights_and_reference_pixels_unchanged=True)


def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;report=apply_grade(s,cfg)
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rendercfg=dict(cfg);rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256((out/'prepared.blend').read_bytes()).hexdigest(),original_source=cfg['source'],original_source_sha256=digest,pigment_grade=report)
    run(rendercfg);assert hashlib.sha256(source.read_bytes()).hexdigest()==digest


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(a.config).read_text(encoding='utf-8-sig')))
