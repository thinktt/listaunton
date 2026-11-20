"""Independently audit saved exact receivers and the declared light-only edits."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
BODY='Bishop - continuous turned body'
REGIONS={'body-rest','socket-lip'}
VISIBILITY=['visible_camera','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter','visible_shadow']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def serial(value):
    if isinstance(value,(str,int,float,bool)) or value is None:return value
    if isinstance(value,bpy.types.ID):return value.name
    try:return [serial(v) for v in value]
    except TypeError:return str(value)

def properties(obj):
    return {p.identifier:serial(getattr(obj,p.identifier)) for p in obj.bl_rna.properties
            if p.type in {'BOOLEAN','INT','FLOAT','STRING','ENUM'} and not p.is_readonly
            and p.identifier not in {'name','label','select','show_options','show_preview','show_texture','hide','width','height'}}

def array(collection,key,width=1,dtype=np.float32):
    result=np.empty(len(collection)*width,dtype=dtype);collection.foreach_get(key,result)
    return result.reshape(-1,width) if width>1 else result

def tree_state(tree):
    nodes={}
    for n in tree.nodes:
        image=getattr(n,'image',None)
        row={'type':n.bl_idname,'properties':properties(n),
             'inputs':[(v.identifier,serial(v.default_value)) for v in n.inputs if hasattr(v,'default_value')]}
        if image:
            row['image']={'name':image.name,'colorspace':image.colorspace_settings.name,'size':list(image.size),
                          'packed':bool(image.packed_file),'pixels':hashlib.sha256(np.array(image.pixels[:],dtype='<f4').tobytes()).hexdigest()}
        ramp=getattr(n,'color_ramp',None)
        if ramp:row['ramp']=[properties(ramp),[(e.position,list(e.color)) for e in ramp.elements]]
        nodes[n.name]=row
    return {'nodes':nodes,'links':sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in tree.links)}

def mesh_state(mesh):
    arrays={'positions':array(mesh.vertices,'co',3),'loops':array(mesh.loops,'vertex_index',dtype=np.int32),
            'starts':array(mesh.polygons,'loop_start',dtype=np.int32),'counts':array(mesh.polygons,'loop_total',dtype=np.int32),
            'materials':array(mesh.polygons,'material_index',dtype=np.int32),'smooth':array(mesh.polygons,'use_smooth',dtype=bool),
            'normals':array(mesh.corner_normals,'vector',3)}
    for uv in mesh.uv_layers:arrays['uv:'+uv.name]=array(uv.data,'uv',2)
    for attr in mesh.attributes:
        if attr.data_type=='FLOAT' and attr.domain in {'POINT','CORNER'}:arrays['float:'+attr.name+':'+attr.domain]=array(attr.data,'value')
    return {'hashes':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in arrays.items()},
            'uv_active_index':mesh.uv_layers.active_index,'uv_render':[l.active_render for l in mesh.uv_layers],
            'material_slots':[m.name if m else None for m in mesh.materials]}

def snapshot():
    s=bpy.context.scene;result={'meshes':{},'lights':{},'materials':{},'objects':sorted((o.name,o.type) for o in s.objects)}
    for ob in s.objects:
        common={'matrix':serial(ob.matrix_world),'hide_render':ob.hide_render,
                'visibility':{k:getattr(ob,k) for k in VISIBILITY}}
        if ob.type=='MESH':
            mods=[]
            for m in ob.modifiers:
                mods.append({'type':m.type,'properties':properties(m),
                             'object':m.object.name if m.type=='BOOLEAN' and m.object else None})
            result['meshes'][ob.name]=dict(common,mesh=mesh_state(ob.data),modifiers=mods)
            for mat in ob.data.materials:
                if mat and mat.name not in result['materials']:result['materials'][mat.name]=tree_state(mat.node_tree)
        if ob.type=='LIGHT':
            receiver=ob.light_linking.receiver_collection
            result['lights'][ob.name]=dict(common,data=properties(ob.data),
              receivers=sorted(o.name for o in receiver.objects) if receiver else None,
              nodes=tree_state(ob.data.node_tree) if ob.data.use_nodes else None)
    cam=s.camera
    result['camera']={'matrix':serial(cam.matrix_world),'data':properties(cam.data)}
    result['world']=tree_state(s.world.node_tree)
    result['color_management']=[properties(s.view_settings),properties(s.display_settings)]
    result['render_path']={k:getattr(s.cycles,k) for k in ['max_bounces','diffuse_bounces','glossy_bounces','transmission_bounces','volume_bounces','transparent_max_bounces','use_light_tree']}
    return result

def check(scene,cfg):
    parts=[o for o in scene.objects if o.get('bishop_render_region')]
    assert len(parts)==2 and {o['bishop_render_region'] for o in parts}==REGIONS
    body=bpy.data.objects[BODY];assert body.hide_render and body.get('bishop_editable_control')
    for m in body.modifiers:
        if m.type=='SUBSURF':assert m.levels==m.render_levels
    bpy.context.view_layer.update();evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    xyz=array(mesh.vertices,'co',3);indices=array(mesh.loops,'vertex_index',dtype=np.int32)
    starts=array(mesh.polygons,'loop_start',dtype=np.int32);counts=array(mesh.polygons,'loop_total',dtype=np.int32)
    normals=array(mesh.corner_normals,'vector',3);covered=[];reports=[]
    lower,upper=cfg['socket_z_band']
    centers=np.add.reduceat(xyz[indices],starts,axis=0)/counts[:,None]
    for part in parts:
        name=part['bishop_render_region'];me=part.data
        assert not part.hide_render and not part.modifiers and part.matrix_world==body.matrix_world
        assert all(getattr(part,k)==getattr(body,k) for k in VISIBILITY)
        assert list(me.materials)==list(body.data.materials) and all(me.materials)
        faces=array(me.attributes['bishop_source_face'].data,'value',dtype=np.int32)
        vertices=array(me.attributes['bishop_source_vertex'].data,'value',dtype=np.int32)
        assert len(np.unique(faces))==len(faces) and faces.min()>=0 and faces.max()<len(mesh.polygons)
        assert len(np.unique(vertices))==len(vertices) and vertices.min()>=0 and vertices.max()<len(mesh.vertices)
        assert np.array_equal(array(me.vertices,'co',3),xyz[vertices])
        loops=np.concatenate([np.arange(starts[f],starts[f]+counts[f]) for f in faces])
        assert np.array_equal(array(me.polygons,'loop_total',dtype=np.int32),counts[faces])
        assert np.array_equal(vertices[array(me.loops,'vertex_index',dtype=np.int32)],indices[loops])
        for key,dtype in [('material_index',np.int32),('use_smooth',bool)]:
            assert np.array_equal(array(me.polygons,key,dtype=dtype),array(mesh.polygons,key,dtype=dtype)[faces])
        assert me.uv_layers.keys()==mesh.uv_layers.keys()
        assert me.uv_layers.active_index==mesh.uv_layers.active_index
        uv_errors={}
        for layer in mesh.uv_layers:
            actual_uv=array(me.uv_layers[layer.name].data,'uv',2);expected_uv=array(layer.data,'uv',2)[loops]
            # Re-evaluating the Boolean after reopening changes 440 projection
            # components by one float32 ULP. Control UVs remain byte-identical;
            # this bound is <0.0005 texel even on a 4096px atlas.
            uv_errors[layer.name]=float(np.max(np.abs(actual_uv-expected_uv)))
            assert uv_errors[layer.name]<1e-7,(name,layer.name,'UV difference',uv_errors[layer.name])
            assert me.uv_layers[layer.name].active_render==layer.active_render
        for attr in mesh.attributes:
            if attr.data_type=='FLOAT' and attr.domain in {'POINT','CORNER'} and not attr.name.startswith('.'):
                actual=me.attributes[attr.name];assert actual.domain==attr.domain
                assert np.array_equal(array(actual.data,'value'),array(attr.data,'value')[vertices if attr.domain=='POINT' else loops])
        error=float(np.max(np.abs(array(me.corner_normals,'vector',3)-normals[loops])))
        assert error<2e-4,(name,error)
        membership=(centers[faces,2]>=lower)&(centers[faces,2]<upper)
        assert np.all(membership if name=='socket-lip' else ~membership)
        covered.extend(faces.tolist());reports.append({'region':name,'faces':len(faces),'vertices':len(vertices),'normal_max_component_error':error,'uv_max_component_errors':uv_errors})
    assert sorted(covered)==list(range(len(mesh.polygons))),'Every evaluated face must occur exactly once.'
    evaluated.to_mesh_clear()
    return {'passed':True,'surface_positions_faces_attributes_material_indices_and_slots_exact':True,'evaluated_uv_error_below_1e_7':True,
            'closed_editable_control_retained':True,'regions':reports,'all_faces_once':True}

def audit(model,cfg):
    source=ROOT/cfg['source'];assert sha(source)==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);before=snapshot()
    expected=json.loads(json.dumps(before));expected['meshes'][BODY]['hide_render']=True
    part_names=['Bishop receiver body-rest','Bishop receiver socket-lip']
    expected['objects']=sorted(expected['objects']+[[name,'MESH'] for name in part_names])
    for name,row in expected['lights'].items():
        receivers=row['receivers']
        if receivers and BODY in receivers:row['receivers']=sorted(receivers+part_names)
        if name.startswith('socket arc '):
            row['data']['shadow_soft_size']=float(np.float32(cfg['arc_shadow_soft_size']))
            row['data']['spot_size']=float(np.float32(math.radians(cfg['arc_spot_degrees'])))
            row['receivers']=['Bishop receiver socket-lip']
        elif name in cfg['exclude_from_socket']:row['receivers']=['Bishop receiver body-rest']
    bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);s=bpy.context.scene
    assert json.loads(s['bishop_receiver_trial'])==cfg
    after=snapshot()
    for name in part_names:after['meshes'].pop(name)
    for key in expected:
        assert json.dumps(expected[key],sort_keys=True)==json.dumps(after[key],sort_keys=True),('Undeclared state change',key)
    result=check(s,cfg)
    result.update(source=cfg['source'],source_sha256=sha(source),model=str(model.relative_to(ROOT)),model_sha256=sha(model),
      only_declared_light_parameters_and_links_changed=True,geometry_controls_cutter_uvs_modifiers_and_material_pixels_preserved=True,
      camera_world_display_render_path_preserved=True,reopened_audit=True,config=cfg)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True);p.add_argument('--model',required=True);p.add_argument('--out',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads((ROOT/a.config).read_text())
    report=audit(ROOT/a.model,cfg);out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+'\n');print('BISHOP_RENDER_RECEIVERS_PASSED',json.dumps(report),flush=True)
