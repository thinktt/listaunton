"""Audit declared changes to existing lights after saving and reopening a scene."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--model',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads((ROOT/a.config).read_text());source=ROOT/cfg['source'];model=ROOT/a.model
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def plain(v):
    if isinstance(v,(str,float,int,bool)) or v is None:return v
    try:return list(v)
    except TypeError:return str(v)
def nodes(tree):
    values=[]
    for n in tree.nodes:
        inputs=[(v.name,plain(v.default_value)) for v in n.inputs if hasattr(v,'default_value')]
        im=getattr(n,'image',None)
        pixels=hashlib.sha256(np.array(im.pixels[:],dtype='<f4').tobytes()).hexdigest() if im else None
        values.append([n.name,n.bl_idname,inputs,pixels])
    return [values,sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in tree.links)]
def snapshot():
    s=bpy.context.scene;meshes={};mats={};lights={}
    camera=[float(x) for row in s.camera.matrix_world for x in row]+[s.camera.data.ortho_scale,s.camera.data.shift_x,s.camera.data.shift_y]
    for ob in s.objects:
        if ob.type=='MESH':
            ar=np.array([list(v.co) for v in ob.data.vertices],dtype='<f4').tobytes()
            ar+=json.dumps([list(f.vertices) for f in ob.data.polygons]).encode()
            ar+=np.array([list(row) for row in ob.matrix_world],dtype='<f4').tobytes()
            for uv in ob.data.uv_layers:ar+=np.array([list(v.uv) for v in uv.data],dtype='<f4').tobytes()
            meshes[ob.name]=hashlib.sha256(ar).hexdigest()
            for mat in ob.data.materials:
                if mat and mat.use_nodes:mats[mat.name]=nodes(mat.node_tree)
        elif ob.type=='LIGHT':
            d=ob.data
            entry={k:plain(getattr(d,k)) for k in ['type','energy','color','size','size_y','shape','spread','spot_size','spot_blend','shadow_soft_size','use_nodes'] if hasattr(d,k)}
            entry.update(matrix=[float(v) for row in ob.matrix_world for v in row],diffuse=ob.visible_diffuse,glossy=ob.visible_glossy,hide_render=ob.hide_render)
            c=ob.light_linking.receiver_collection;entry['receivers']=sorted(o.name for o in c.objects) if c else None
            if d.use_nodes:entry['nodes']=nodes(d.node_tree)
            lights[ob.name]=entry
    return {'camera':camera,'meshes_and_uvs':meshes,'materials':mats,'lights':lights,'world':nodes(s.world.node_tree),
            'color_management':[s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma]}
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);before=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);after=snapshot()
for key in ['camera','meshes_and_uvs','materials','world','color_management']:assert before[key]==after[key],key
assert set(before['lights'])==set(after['lights']), 'No light may be added or removed.'
declared={spec['name']:spec for spec in cfg['lights']};changes={}
data_keys={'energy','color','size','size_y','shape','spot_size','spot_blend','shadow_soft_size'}
for name,prior in before['lights'].items():
    current=after['lights'][name]
    if name not in declared:
        assert prior==current,name;continue
    spec=declared[name];assert set(spec)<={'name','position','target','spread_degrees'}|data_keys
    ob=bpy.data.objects[name];d=ob.data;allowed=set()
    for key in data_keys&set(spec):
        actual=getattr(d,key);desired=spec[key]
        assert actual==desired if isinstance(desired,str) else np.allclose(actual,desired,rtol=2e-6,atol=1e-7),(name,key)
        allowed.add(key)
    if 'spread_degrees' in spec:
        assert math.isclose(d.spread,math.radians(spec['spread_degrees']),rel_tol=2e-6);allowed.add('spread')
    if 'position' in spec:
        assert np.allclose(ob.location,spec['position'],atol=1e-6,rtol=0);allowed.add('matrix')
    if 'target' in spec:
        aim=(Vector(spec['target'])-ob.location).normalized();axis=ob.rotation_euler.to_matrix()@Vector((0,0,-1))
        assert (aim-axis).length<1e-6;allowed.add('matrix')
    assert {k:v for k,v in prior.items() if k not in allowed}=={k:v for k,v in current.items() if k not in allowed},name
    changes[name]={'declared_keys':sorted(allowed),'before':prior,'after':current}
report={'passed':True,'source':cfg['source'],'source_sha256':sha(source),'model':a.model,'model_sha256':sha(model),
 'config':a.config,'config_sha256':sha(ROOT/a.config),'camera_controls_uvs_material_pixels_world_unchanged':True,
 'only_declared_existing_light_properties_changed':True,'changes':changes}
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
print('LIGHT_PATCH_SCOPE_PASSED',flush=True)
