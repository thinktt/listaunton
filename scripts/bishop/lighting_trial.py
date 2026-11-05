"""Isolated bishop lighting trials with unchanged geometry, pigment and camera."""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('config',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
cfg=json.loads(a.config.read_text());source=ROOT/cfg['source']
out=ROOT/'build/bishop-mission'/cfg['variant']
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene

def unchanged_state():
    camera=[float(x) for row in s.camera.matrix_world for x in row]
    camera += [s.camera.data.ortho_scale,s.camera.data.shift_x,s.camera.data.shift_y]
    meshes={};materials={}
    for ob in s.objects:
        if ob.type!='MESH':continue
        values=np.array([list(v.co) for v in ob.data.vertices],dtype='<f4').tobytes()
        values+=json.dumps([list(f.vertices) for f in ob.data.polygons]).encode()
        values+=np.array([list(row) for row in ob.matrix_world],dtype='<f4').tobytes()
        for uv in ob.data.uv_layers:values+=np.array([list(v.uv) for v in uv.data],dtype='<f4').tobytes()
        meshes[ob.name]=hashlib.sha256(values).hexdigest()
        for material in ob.data.materials:
            if not material or material.name in materials or not material.use_nodes:continue
            values=[]
            for node in material.node_tree.nodes:
                inputs=[]
                for socket in node.inputs:
                    if not hasattr(socket,'default_value'):continue
                    value=socket.default_value
                    if not isinstance(value,(str,float,int,bool)):
                        try:value=list(value)
                        except TypeError:value=str(value)
                    inputs.append([socket.name,value])
                image=getattr(node,'image',None)
                packed_hash=hashlib.sha256(image.packed_file.data).hexdigest() if image and image.packed_file else None
                values.append([node.name,node.bl_idname,inputs,packed_hash])
            values.append([[link.from_node.name,link.from_socket.name,link.to_node.name,link.to_socket.name] for link in material.node_tree.links])
            materials[material.name]=hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()
    return {'camera':camera,'meshes_and_uvs':meshes,'material_inputs_links_and_packed_images':materials}

before=unchanged_state()
if 'world' in cfg:s.world.node_tree.nodes['Background'].inputs[1].default_value=cfg['world']
for spec in cfg.get('lights',[]):
    name=spec['name'];ob=bpy.data.objects.get(name)
    if ob is None:
        data=bpy.data.lights.new(name,spec.get('type','AREA'))
        ob=bpy.data.objects.new(name,data);s.collection.objects.link(ob)
    assert ob.type=='LIGHT'
    data=ob.data
    for key in ['energy','color','size','size_y','shape','spot_size','spot_blend']:
        if key in spec:setattr(data,key,spec[key])
    if 'spread_degrees' in spec:data.spread=math.radians(spec['spread_degrees'])
    if 'position' in spec:ob.location=spec['position']
    if 'target' in spec:ob.rotation_euler=(Vector(spec['target'])-ob.location).to_track_quat('-Z','Y').to_euler()
    if 'diffuse' in spec:ob.visible_diffuse=spec['diffuse']
    if 'glossy' in spec:ob.visible_glossy=spec['glossy']
    if 'receiver' in spec:
        name='Bishop light receiver '+spec['receiver']
        collection=bpy.data.collections.get(name) or bpy.data.collections.new(name)
        for receiver in [o for o in s.objects if o.type=='MESH' and not o.hide_render]:
            if ('finial' in receiver.name)==(spec['receiver']=='button') and receiver.name not in collection.objects:collection.objects.link(receiver)
        ob.light_linking.receiver_collection=collection
after=unchanged_state();assert before==after,'Lighting trial modified geometry, UVs, camera or material.'
if 'view_transform' in cfg:s.view_settings.view_transform=cfg['view_transform']
if 'look' in cfg:s.view_settings.look=cfg['look']
s.render.resolution_percentage=100;s.cycles.samples=cfg.get('samples',40)
s.render.filepath=str(out/'wood.png');s['bishop_lighting_trial']=json.dumps(cfg,sort_keys=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'bishop.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
record={'config':cfg,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'saved_model_sha256':hashlib.sha256((out/'bishop.blend').read_bytes()).hexdigest(),'render_sha256':hashlib.sha256((out/'wood.png').read_bytes()).hexdigest(),'geometry_uvs_material_and_camera_unchanged':before==after,'preserved_state':before}
(out/'parameters.json').write_text(json.dumps(record,indent=2)+'\n')
print('BISHOP_LIGHTING_TRIAL_COMPLETE',cfg['variant'],flush=True)
