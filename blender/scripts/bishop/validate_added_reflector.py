"""Audit a lighting-only checkpoint against its declared archived source."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--model',required=True);p.add_argument('--out',required=True)
p.add_argument('--disabled-existing',action='append',default=[],help='Explicitly permit only energy=0 on this existing lamp; preserve every other property.')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads((ROOT/a.config).read_text());source=ROOT/cfg['source'];model=ROOT/a.model
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()

def plain(value):
    if isinstance(value,(str,float,int,bool)) or value is None:return value
    try:return list(value)
    except TypeError:return str(value)

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
            data=ob.data
            entry={k:plain(getattr(data,k)) for k in ['type','energy','color','size','size_y','shape','spread','spot_size','spot_blend','shadow_soft_size','use_nodes'] if hasattr(data,k)}
            entry.update(matrix=[float(v) for row in ob.matrix_world for v in row],diffuse=ob.visible_diffuse,glossy=ob.visible_glossy)
            c=ob.light_linking.receiver_collection;entry['receivers']=sorted(o.name for o in c.objects) if c else None
            if data.use_nodes:entry['nodes']=nodes(data.node_tree)
            lights[ob.name]=entry
    render_path={key:getattr(s.cycles,key) for key in ['max_bounces','diffuse_bounces','glossy_bounces','transmission_bounces','volume_bounces','transparent_max_bounces','use_light_tree']}
    return {'camera':camera,'meshes_and_uvs':meshes,'materials':mats,'lights':lights,'world':nodes(s.world.node_tree),'render_path':render_path,
            'color_management':[s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma]}

bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);before=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);after=snapshot()
for key in ['camera','meshes_and_uvs','materials','world','color_management']:assert before[key]==after[key],key
expected_path=dict(before['render_path'])
if 'glossy_bounces' in cfg:expected_path['glossy_bounces']=cfg['glossy_bounces']
assert after['render_path']==expected_path,'Undeclared render-path change.'
disabled=set(a.disabled_existing)
assert disabled<=set(before['lights'])
specifications={spec['name']:spec for spec in cfg['lights']}
assert disabled<=set(specifications)
added=set(after['lights'])-set(before['lights']);assert added==set(specifications)-disabled
assert set(before['lights'])<=set(after['lights']), 'No existing lamp may be removed.'
for name,prior in before['lights'].items():
    current=after['lights'][name]
    if name in disabled:
        assert specifications[name]=={'name':name,'energy':0}
        assert current['energy']==0
        assert {k:v for k,v in prior.items() if k!='energy'}=={k:v for k,v in current.items() if k!='energy'},name
    else:assert current==prior,name
effective={}
for spec in cfg['lights']:
    if spec['name'] in disabled:continue
    ob=bpy.data.objects[spec['name']];data=ob.data
    assert data.type==spec['type']=='SPOT'
    for key in ['energy','color','spot_size','spot_blend','shadow_soft_size']:
        assert np.allclose(getattr(data,key),spec[key],rtol=2e-6,atol=1e-7),key
    assert np.allclose(ob.location,spec['position'],rtol=0,atol=1e-6)
    aim=(Vector(spec['target'])-ob.location).normalized();axis=ob.rotation_euler.to_matrix()@Vector((0,0,-1))
    assert (aim-axis).length<1e-6
    assert not ob.visible_diffuse and ob.visible_glossy
    assert ob.light_linking.receiver_collection.name=='Bishop light receiver body'
    effective[spec['name']]=after['lights'][spec['name']]
report={'passed':True,'source':cfg['source'],'source_sha256':sha(source),'model':a.model,'model_sha256':sha(model),
        'config':a.config,'config_sha256':sha(ROOT/a.config),'camera_controls_uvs_material_pixels_world_unchanged':True,
        'original_lights_unchanged':not disabled,'existing_lights_disabled_only':sorted(disabled),
        'new_lights':effective,'only_declared_lights_added':True,'source_geometry_and_light_scope_checked':True}
report['camera_controls_uvs_material_pixels_world_and_original_lights_unchanged']=not disabled
report['only_declared_light_added']=True
report['render_path']={'before':before['render_path'],'after':after['render_path'],'declared_glossy_bounces':cfg.get('glossy_bounces')}
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
print('ADDED_REFLECTOR_SCOPE_PASSED',flush=True)
