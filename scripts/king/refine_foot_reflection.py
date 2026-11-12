"""Retarget a foot reflector and add masked physical coat relief."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run
from focused_reflections import target
from render_regions import controls,regenerate,clear_light_path

def prepare(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    objects=controls(s)
    if cfg.get('detail'):
        detail=cfg['detail'];name='Foot shoulder detail'
        for ob in objects:
            values=np.zeros(len(ob.data.vertices),dtype=np.float32)
            if 'body' in ob.name:
                ring=np.arange(len(values))//96
                a,b=detail['lower_fade'];t=np.clip((ring-a)/(b-a),0,1);values[:]=t*t*(3-2*t)
                a,b=detail['upper_fade'];t=np.clip((ring-a)/(b-a),0,1);values*=1-t*t*(3-2*t)
            attr=ob.data.attributes.get(name) or ob.data.attributes.new(name,'FLOAT','POINT');attr.data.foreach_set('value',values)
        mat=objects[0].data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links
        attr=n.get('Foot detail mask') or n.new('ShaderNodeAttribute');attr.name='Foot detail mask';attr.attribute_name=name
        strength=n.get('Foot detail strength') or n.new('ShaderNodeMath');strength.name='Foot detail strength';strength.operation='MULTIPLY';strength.inputs[1].default_value=detail['strength'];l.new(attr.outputs['Fac'],strength.inputs[0])
        noise=n.get('Foot fine pores') or n.new('ShaderNodeTexNoise');noise.name='Foot fine pores';noise.inputs['Scale'].default_value=detail['scale'];noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.65
        l.new(n['Texture Coordinate'].outputs['Object'],noise.inputs['Vector'])
        bump=n.get('Foot coat microtexture') or n.new('ShaderNodeBump');bump.name='Foot coat microtexture';bump.inputs['Distance'].default_value=detail['distance']
        l.new(strength.outputs[0],bump.inputs['Strength']);l.new(noise.outputs['Fac'],bump.inputs['Height'])
        socket=n['Principled BSDF'].inputs['Coat Normal'];assert socket.is_linked
        if socket.links[0].from_node!=bump:l.new(socket.links[0].from_socket,bump.inputs['Normal'])
        l.new(bump.outputs['Normal'],socket)
        regenerate(s)
    row=cfg['reflector'];light=bpy.data.objects[row['name']]
    ob,point,direction,normal=target(s,*row['pixel'])
    assert ob.get('king_render_region')=='foot'
    assert clear_light_path(s,point,normal,direction,row.get('distance',6))
    light.location=point+direction*row.get('distance',6)
    light.rotation_euler=(point-light.location).to_track_quat('-Z','Y').to_euler()
    light.data.energy=row['energy']
    cfg['reflector_probe']=dict(pixel=row['pixel'],point=list(point),normal=list(normal),position=list(light.location),rotation=list(light.rotation_euler),clear_reflected_ray=True)
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rc=dict(cfg);rc.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256((out/'prepared.blend').read_bytes()).hexdigest(),original_source=cfg['source'],original_source_sha256=digest)
    run(rc)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);prepare(json.loads(Path(a.config).read_text(encoding='utf-8-sig')))
