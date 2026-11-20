"""Audit the exact declared base-ring edit against its archived bishop source."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector,kdtree
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--model',required=True);p.add_argument('--out',required=True)
p.add_argument('--geometry-only',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
cfg=json.loads((ROOT/a.config).read_text());source=ROOT/cfg['source'];model=ROOT/a.model
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(source)==cfg['source_sha256']
profile=json.loads((ROOT/cfg['profile']).read_text())
assert cfg['declaration_key']=='mission_base_curvature' and cfg.get('button_scale_xy',1)==1
assert set(map(int,cfg['body_rings']))=={17,18}
for key,(radius,y) in cfg['body_rings'].items():
    old_r,old_y=profile['profile'][int(key)];assert y==old_y and 0<radius-old_r<=1
def serial(value):
    if isinstance(value,(str,int,float,bool)) or value is None:return value
    try:return [serial(v) for v in value]
    except TypeError:return str(value)
def material_hash(tree):
    values=[]
    for n in tree.nodes:
        im=getattr(n,'image',None)
        values.append([n.name,n.bl_idname,[[v.identifier,serial(v.default_value)] for v in n.inputs if hasattr(v,'default_value')],
         hashlib.sha256(np.array(im.pixels[:],dtype='<f4').tobytes()).hexdigest() if im else None])
    values.append(sorted([l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier] for l in tree.links))
    return hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()
def capture(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);bpy.context.view_layer.update();s=bpy.context.scene;g=bpy.context.evaluated_depsgraph_get()
    result={'controls':{},'construction':{},'materials':{},'lights':{},'evaluated':{}}
    result['camera']=[serial(s.camera.matrix_world),s.camera.data.type,s.camera.data.ortho_scale,s.camera.data.shift_x,s.camera.data.shift_y]
    result['world']=material_hash(s.world.node_tree)
    result['display']=[s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma]
    for ob in s.objects:
        if ob.type=='LIGHT':
            keys=['type','energy','color','size','size_y','shape','spread','spot_size','spot_blend','shadow_soft_size']
            result['lights'][ob.name]={'data':{k:serial(getattr(ob.data,k)) for k in keys if hasattr(ob.data,k)},'matrix':serial(ob.matrix_world),
              'diffuse':ob.visible_diffuse,'glossy':ob.visible_glossy,'receiver':sorted(o.name for o in ob.light_linking.receiver_collection.objects) if ob.light_linking.receiver_collection else None}
        if ob.type!='MESH':continue
        result['controls'][ob.name]=np.array([list(v.co) for v in ob.data.vertices])
        mods=[]
        for m in ob.modifiers:
            values={k:serial(getattr(m,k)) for k in ['type','levels','render_levels','subdivision_type','operation','solver','width','segments','limit_method','angle_limit','profile'] if hasattr(m,k)}
            if m.type=='BOOLEAN':values['cutter']=m.object.name
            mods.append(values)
        result['construction'][ob.name]={'matrix':serial(ob.matrix_world),'faces':[list(f.vertices) for f in ob.data.polygons],
         'uvs':[[list(v.uv) for v in layer.data] for layer in ob.data.uv_layers],'modifiers':mods,'hide_render':ob.hide_render}
        for mat in ob.data.materials:
            if mat and mat.use_nodes:result['materials'][mat.name]=material_hash(mat.node_tree)
        if ob.hide_render:continue
        ev=ob.evaluated_get(g);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
        assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0,ob.name
        vertices=np.array([list(v.co) for v in me.vertices]);assert np.isfinite(vertices).all()
        result['evaluated'][ob.name]={'positions':vertices,'volume':bm.calc_volume(signed=True),'count':len(vertices)}
        bm.free();ev.to_mesh_clear()
    return result
old=capture(source);new=capture(model)
for key in ['construction','camera','display']+([] if a.geometry_only else ['materials','lights','world']):assert old[key]==new[key],key
errors={}
for name,before in old['controls'].items():
    expected=before.copy()
    if name=='Bishop - continuous turned body':
        for index,(radius,y) in cfg['body_rings'].items():
            i=int(index);expected[i*128:(i+1)*128,:2]*=radius/profile['profile'][i][0]
    err=float(np.max(np.abs(new['controls'][name]-expected)));assert err<2e-7,(name,err);errors[name]=err
    assert np.array_equal(before[:,2],new['controls'][name][:,2]),(name,'height')
scope={}
body=old['controls']['Bishop - continuous turned body'];lo=float(body[14*128,2]);hi=float(body[21*128,2])
for name,before in old['evaluated'].items():
    after=new['evaluated'][name]
    for fn in [np.min,np.max]:assert np.max(np.abs(fn(before['positions'],axis=0)-fn(after['positions'],axis=0)))<1e-6
    distances=[]
    for reference,changed in [(before['positions'],after['positions']),(after['positions'],before['positions'])]:
        tree=kdtree.KDTree(len(reference))
        for i,v in enumerate(reference):tree.insert(Vector(v),i)
        tree.balance();maximum=0;count=0
        for v in changed:
            if name=='Bishop - continuous turned body' and lo<=v[2]<=hi:continue
            maximum=max(maximum,tree.find(Vector(v))[2]);count+=1
        assert maximum<5e-6,(name,maximum);distances.append({'max_distance':maximum,'samples':count})
    scope[name]={'closed_positive_volume':True,'volume':after['volume'],'evaluated_vertices':after['count'],'outside_base_bidirectional_distance':distances}
report={'passed':True,'source':cfg['source'],'source_sha256':sha(source),'model':a.model,'model_sha256':sha(model),
 'config':a.config,'declared_rings':[17,18],'max_control_error':errors,'all_control_heights_exact':True,
 'camera_topology_uvs_modifiers_cutter_and_dimensions_preserved':True,'outside_base_geometry_preserved':True,
 'materials_lights_world_preserved':all(old[k]==new[k] for k in ['materials','lights','world']),
 'material_lighting_preservation_required':not a.geometry_only,'scope':scope}
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print('BASE_CURVATURE_SCOPE_PASSED',flush=True)
