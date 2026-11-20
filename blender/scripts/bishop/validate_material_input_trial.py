"""Independently reopen and audit only declared material scalar/link changes."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--config',required=True);p.add_argument('--model',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads((ROOT/a.config).read_text())
source=ROOT/cfg['source'];model=ROOT/a.model
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def plain(v):
    if isinstance(v,(str,int,float,bool)) or v is None:return v
    try:return list(v)
    except TypeError:return str(v)
def tree_state(tree):
    rows={}
    for node in tree.nodes:
        image=getattr(node,'image',None)
        rows[node.name]={'type':node.bl_idname,
          'inputs':[(v.name,plain(v.default_value)) for v in node.inputs if hasattr(v,'default_value')],
          'operation':getattr(node,'operation',None),
          'pixels':sha_bytes(np.array(image.pixels[:],dtype='<f4').tobytes()) if image else None}
    return {'nodes':rows,'links':sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in tree.links)}
def sha_bytes(v):return hashlib.sha256(v).hexdigest()
def snapshot():
    s=bpy.context.scene;meshes={};materials={};lights={}
    for ob in s.objects:
        if ob.type=='MESH':
            payload=np.array([list(v.co) for v in ob.data.vertices],dtype='<f4').tobytes()
            payload+=json.dumps([list(f.vertices) for f in ob.data.polygons]).encode()
            payload+=np.array([list(r) for r in ob.matrix_world],dtype='<f4').tobytes()
            for layer in ob.data.uv_layers:payload+=np.array([list(v.uv) for v in layer.data],dtype='<f4').tobytes()
            meshes[ob.name]={'hash':sha_bytes(payload),'hide_render':ob.hide_render,
                             'materials':[m.name if m else None for m in ob.data.materials]}
            for mat in ob.data.materials:
                if mat and mat.use_nodes:materials[mat.name]=tree_state(mat.node_tree)
        if ob.type=='LIGHT':
            data=ob.data
            entry={k:plain(getattr(data,k)) for k in ['type','energy','color','size','size_y','shape','spread','spot_size','spot_blend','shadow_soft_size','use_nodes'] if hasattr(data,k)}
            entry.update(matrix=[float(v) for row in ob.matrix_world for v in row],diffuse=ob.visible_diffuse,
                         glossy=ob.visible_glossy,hide_render=ob.hide_render)
            c=ob.light_linking.receiver_collection;entry['receivers']=sorted(o.name for o in c.objects) if c else None
            if data.use_nodes:entry['nodes']=tree_state(data.node_tree)
            lights[ob.name]=entry
    cam=s.camera
    return {'meshes_and_uvs':meshes,'materials':materials,'lights':lights,'world':tree_state(s.world.node_tree),
      'camera':[float(v) for r in cam.matrix_world for v in r]+[cam.data.ortho_scale,cam.data.shift_x,cam.data.shift_y],
      'color_management':[s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma],
      'render_path':{k:getattr(s.cycles,k) for k in ['max_bounces','diffuse_bounces','glossy_bounces','transmission_bounces','volume_bounces','transparent_max_bounces','use_light_tree']}}
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);before=snapshot()
expected=json.loads(json.dumps(before));declared=[]
for spec in cfg.get('inputs',[]):
    # Only the named scalar default is permitted to differ; nodes, links and image
    # pixels must compare identically, as do all other scene controls below.
    entries=expected['materials'][spec['material']]['nodes'][spec['node']]['inputs']
    socket=bpy.data.materials[spec['material']].node_tree.nodes[spec['node']].inputs[spec['input']]
    matches=[i for i,(name,val) in enumerate(entries) if name==socket.name]
    assert len(matches)==1
    i=matches[0];prior=entries[i][1]
    assert isinstance(prior,(float,int)) and isinstance(spec['value'],(float,int))
    entries[i][1]=float(np.float32(spec['value']))
    declared.append(dict(spec,before=prior,expected_saved_value=entries[i][1]))
declared_links=[]
for spec in cfg.get('links',[]):
    links=expected['materials'][spec['material']]['links']
    old=spec['expected_from']+[spec['to_node'],spec['to_socket']]
    assert old in links
    assert len([link for link in links if link[2:]==[spec['to_node'],spec['to_socket']]])==1
    links.remove(old);links.append([spec['from_node'],spec['from_socket'],spec['to_node'],spec['to_socket']]);links.sort()
    declared_links.append(spec)
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);after=snapshot()
for key in expected:assert json.dumps(expected[key],sort_keys=True)==json.dumps(after[key],sort_keys=True),key
report={'passed':True,'source':cfg['source'],'source_sha256':sha(source),'model':a.model,'model_sha256':sha(model),
 'config':a.config,'config_sha256':sha(ROOT/a.config),'declared_changes':declared,
 'declared_link_changes':declared_links,
 'only_declared_material_inputs_and_links_changed':True,
 'geometry_uvs_camera_lights_world_image_pixels_and_undeclared_material_state_preserved':True,
 'render_path_preserved':True,'reopened_audit':True}
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
print('MATERIAL_INPUT_SCOPE_PASSED',flush=True)
