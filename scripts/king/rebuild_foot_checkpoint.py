"""Reproduce the accepted foot shoulder from the archived sixth king."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run
from render_regions import controls,regenerate,link,clear_light_path
from focused_reflections import target

def offsets(body,rows):
    co=np.array([v.co[:] for v in body.data.vertices]).reshape(-1,96,3)
    for index,offset in rows.items():
        j=int(index);radius=np.linalg.norm(co[j,:,:2],axis=1)
        co[j,:,:2]*=((radius+offset[0])/radius)[:,None];co[j,:,2]+=offset[1]
    body.data.vertices.foreach_set('co',co.reshape(-1));body.data.update()

def finish(scene,cfg):
    objects=controls(scene);name=cfg['attribute'];start,end=cfg['ring_fade']
    for ob in objects:
        values=np.zeros(len(ob.data.vertices),dtype=np.float32)
        if 'body' in ob.name:
            ring=np.arange(len(values))//96;t=np.clip((ring-start)/(end-start),0,1);values[:]=1-t*t*(3-2*t)
            lo,hi=cfg['lower_fade'];t=np.clip((ring-lo)/(hi-lo),0,1);values*=t*t*(3-2*t)
        attr=ob.data.attributes.new(name,'FLOAT','POINT');attr.data.foreach_set('value',values)
    mat=objects[0].data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links
    attr=n.new('ShaderNodeAttribute');attr.attribute_name=name
    for node_name,input_name,value in cfg['inputs']:
        socket=n[node_name].inputs[input_name];mix=n.new('ShaderNodeMixRGB');mix.label=name+' '+input_name
        l.new(attr.outputs['Fac'],mix.inputs[0]);mix.inputs[2].default_value=(value,value,value,1)
        if socket.is_linked:l.new(socket.links[0].from_socket,mix.inputs[1])
        else:mix.inputs[1].default_value=(socket.default_value,)*3+(1,)
        l.new(mix.outputs[0],socket)

def build(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    body=next(o for o in controls(s) if 'body' in o.name)
    offsets(body,cfg['geometry_first']);regenerate(s)
    row=cfg['reflector'];ob,point,direction,normal=target(s,*row['pixel'])
    assert ob.get('king_render_region')=='foot' and clear_light_path(s,point,normal,direction,row['distance'])
    data=bpy.data.lights.new(row['name'],'AREA');data.shape='RECTANGLE';data.size=row['size'];data.size_y=row['size_y'];data.color=row['color'];data.energy=cfg['fitted_energy']
    light=bpy.data.objects.new(row['name'],data);s.collection.objects.link(light)
    light.location=point+direction*row['distance'];light.rotation_euler=(point-light.location).to_track_quat('-Z','Y').to_euler()
    light.visible_diffuse=False;light.visible_glossy=True;link(light,[ob],row['name'])
    bpy.data.objects['Foot left reflection'].data.energy=0
    finish(s,cfg['finish']);offsets(body,cfg['geometry_final'])
    if cfg.get('geometry_registration'):offsets(body,cfg['geometry_registration'])
    regenerate(s)
    s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.use_adaptive_sampling=True
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rc=dict(cfg);rc.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256((out/'prepared.blend').read_bytes()).hexdigest(),original_source=cfg['source'],original_source_sha256=digest,neutral=True,profile=True)
    run(rc);assert hashlib.sha256(source.read_bytes()).hexdigest()==digest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');p.add_argument('--variant');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);c=json.loads(Path(a.config).read_text(encoding='utf-8-sig'))
    if a.variant:c['variant']=a.variant
    build(c)
