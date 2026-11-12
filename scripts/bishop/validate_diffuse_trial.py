"""Audit declared real diffuse lights while preserving source material and form."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from validate_render_receivers import snapshot,check
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fit',required=True);p.add_argument('--model',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);fit=json.loads((ROOT/a.fit).read_text());source=ROOT/fit['source'];model=ROOT/a.model
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)==fit['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);before=snapshot()
world_output=next(n for n in bpy.context.scene.world.node_tree.nodes if n.type=='OUTPUT_WORLD')
old_link=world_output.inputs['Surface'].links[0];old_world_from=[old_link.from_node.name,old_link.from_socket.identifier]
output_name=world_output.name
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);s=bpy.context.scene;after=snapshot()
assert json.loads(s['bishop_diffuse_study'])==fit
for key in ['meshes','materials','camera','color_management','render_path']:
    assert json.dumps(before[key],sort_keys=True)==json.dumps(after[key],sort_keys=True),key
new_names={v['name'] for v in fit['lights']}
assert set(after['lights'])==set(before['lights'])|new_names
assert sorted(after['objects'])==sorted(before['objects']+[(name,'LIGHT') for name in new_names])
for name,old in before['lights'].items():
    old['visibility']['visible_diffuse']=False
    assert old==after['lights'][name],name
lamp_errors={}
for spec in fit['lights']:
    ob=bpy.data.objects[spec['name']];d=ob.data
    assert d.type=='SUN' and d.use_shadow and not ob.hide_render
    # Blender 5.2 creates every new light with its neutral emission tree enabled.
    # Check that exact tree instead of assuming the deprecated flag is false.
    assert d.use_nodes
    assert set(d.node_tree.nodes.keys())=={'Emission','Light Output'}
    emission=d.node_tree.nodes['Emission'];output=d.node_tree.nodes['Light Output']
    assert emission.type=='EMISSION' and output.type=='OUTPUT_LIGHT'
    assert list(emission.inputs['Color'].default_value)==[1,1,1,1]
    defaults={v.identifier:v.default_value for v in emission.inputs if hasattr(v,'default_value')}
    assert set(defaults)=={'Color','Strength','Weight'}
    assert defaults['Strength']==1 and defaults['Weight']==0
    assert len(d.node_tree.links)==1
    link=d.node_tree.links[0]
    assert (link.from_node.name,link.from_socket.identifier,link.to_node.name,link.to_socket.identifier)==('Emission','Emission','Light Output','Surface')
    assert d.exposure==0 and not d.use_temperature
    assert ob.visible_diffuse and not ob.visible_glossy and ob.light_linking.receiver_collection is None
    assert d.energy==float(np.float32(spec['energy']))
    assert list(d.color)==[float(np.float32(v)) for v in spec['color']]
    assert abs(d.angle-math.radians(fit['basis']['sun_angle_degrees']))<1e-6
    e,az=map(math.radians,spec['direction'])
    expected=Vector((math.sin(az)*math.cos(e),-math.cos(az)*math.cos(e),math.sin(e)))
    actual=ob.matrix_world.to_3x3()@Vector((0,0,1));error=(actual-expected).length
    assert error<1e-6 and (ob.location-(Vector((0,0,2.3))+10*expected)).length<2e-6
    lamp_errors[ob.name]=error
nodes=s.world.node_tree.nodes
extra={'Study diffuse ray','Study unlit diffuse environment','Study preserve glossy environment'}
assert set(after['world']['nodes'])==set(before['world']['nodes'])|extra
for name,row in before['world']['nodes'].items():assert row==after['world']['nodes'][name],name
assert nodes['Study diffuse ray'].type=='LIGHT_PATH'
assert nodes['Study unlit diffuse environment'].type=='BACKGROUND' and nodes['Study unlit diffuse environment'].inputs['Strength'].default_value==0
mix=nodes['Study preserve glossy environment'];assert mix.type=='MIX_SHADER'
def incoming(socket):
    assert len(socket.links)==1
    link=socket.links[0];return [link.from_node.name,link.from_socket.identifier]
assert incoming(mix.inputs[0])==['Study diffuse ray','Is Diffuse Ray']
assert incoming(mix.inputs[1])==old_world_from
assert incoming(mix.inputs[2])==['Study unlit diffuse environment','Background']
assert incoming(nodes[output_name].inputs['Surface'])==['Study preserve glossy environment','Shader']
old_links=[l for l in before['world']['links'] if l[2:]!=(output_name,'Surface')]
actual_old_links=[l for l in after['world']['links'] if l[0] not in extra and l[2] not in extra]
assert old_links==actual_old_links and len(after['world']['links'])==len(before['world']['links'])+3
receivers=check(s,json.loads(s['bishop_receiver_trial']))
record={'passed':True,'source':fit['source'],'source_sha256':sha(source),'model':a.model,'model_sha256':sha(model),
 'fit':a.fit,'new_diffuse_lights':len(new_names),'new_light_direction_max_errors':lamp_errors,
 'geometry_material_pixels_uvs_relief_camera_and_render_path_preserved':True,
 'existing_light_data_and_glossy_visibility_preserved':True,'only_old_diffuse_visibility_disabled':True,
 'original_glossy_environment_preserved':True,'diffuse_environment_disabled_by_explicit_ray_switch':True,
 'render_receivers':receivers,'reopened_audit':True}
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(record,indent=2)+'\n')
print('DIFFUSE_STUDY_SCOPE_PASSED',flush=True)
