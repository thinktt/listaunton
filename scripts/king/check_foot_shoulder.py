"""Verify the exact scope of king checkpoint 007 against checkpoint 006."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from render_regions import controls
from check_base_light_checkpoint import snapshot,graph,digest
from inspect_foot_profile import inspect

def extra():
    return dict(positions={o.name:np.array([v.co[:] for v in o.data.vertices]) for o in controls(bpy.context.scene)},relief={o.name:digest([v.value for v in o.data.attributes['Lower flare relief mask'].data]) for o in controls(bpy.context.scene)},packed={im.name:hashlib.sha256(bytes(im.packed_file.data)).hexdigest() for im in bpy.data.images if im.packed_file},shadows={o.name:o.data.use_shadow for o in bpy.context.scene.objects if o.type=='LIGHT'})

def check(source,after,config,output):
    cfg=json.loads((ROOT/config).read_text(encoding='utf-8'));a,old,_=snapshot(source);ae=extra();b,new,receivers=snapshot(after);be=extra()
    name=cfg['finish']['attribute'];modified=[]
    for ob in controls(bpy.context.scene):
        expected=ae['positions'][ob.name].copy()
        if 'body' in ob.name:
            steps=[cfg['geometry_first'],cfg['geometry_final']]+([cfg['geometry_registration']] if cfg.get('geometry_registration') else [])
            for step in steps:
                co=expected.reshape(-1,96,3)
                for key,off in step.items():
                    row=co[int(key)];radius=np.linalg.norm(row[:,:2],axis=1);row[:,:2]*=((radius+off[0])/radius)[:,None];row[:,2]+=off[1]
                expected=co.reshape(-1,3).astype(np.float32).astype(float)
            modified=sorted(set(int(k) for step in steps for k in step))
        assert np.array_equal(expected,be['positions'][ob.name]),('Unexpected control edit',ob.name)
        expected_mask=np.zeros(len(ob.data.vertices),dtype=np.float32)
        if 'body' in ob.name:
            ring=np.arange(len(expected_mask))//96;lo,hi=cfg['finish']['ring_fade'];t=np.clip((ring-lo)/(hi-lo),0,1);expected_mask[:]=1-t*t*(3-2*t)
            lo,hi=cfg['finish']['lower_fade'];t=np.clip((ring-lo)/(hi-lo),0,1);expected_mask*=t*t*(3-2*t)
        actual=np.array([v.value for v in ob.data.attributes[name].data],dtype=np.float32);assert np.array_equal(actual,expected_mask)
        b['objects'][ob.name]['attributes'].pop(name)
        b['objects'][ob.name]['positions']=a['objects'][ob.name]['positions']
    material=controls(bpy.context.scene)[0].data.materials[0];nodes=material.node_tree.nodes;links=material.node_tree.links;remove=set()
    for node_name,input_name,value in cfg['finish']['inputs']:
        socket=nodes[node_name].inputs[input_name];mix=socket.links[0].from_node;assert mix.type=='MIX_RGB' and mix.blend_type=='MIX'
        assert np.allclose(mix.inputs[2].default_value,[value,value,value,1],atol=1e-8)
        attr=mix.inputs[0].links[0].from_node;assert attr.attribute_name==name
        old_socket=mix.inputs[1].links[0].from_socket;links.new(old_socket,socket);remove.update([mix,attr])
    assert len(remove)==4
    for node in remove:nodes.remove(node)
    for ob in controls(bpy.context.scene):b['objects'][ob.name]['material']=graph(ob.data.materials[0].node_tree)
    assert a==b,'Undeclared geometry, material, camera, pigment, UV or world change'
    assert ae['packed']==be['packed'] and ae['relief']==be['relief']
    for key,row in old.items():
        expected=dict(row)
        if key=='Foot left reflection':expected['energy']=0
        assert new[key]==expected,('Unexpected old light change',key)
        assert ae['shadows'][key]==be['shadows'][key]
    added=sorted(set(new)-set(old));assert added==['Foot broad crescent']
    lamp=new[added[0]];assert lamp['receivers']==['foot'] and lamp['type']=='AREA' and not lamp['diffuse'] and lamp['glossy']
    assert abs(lamp['energy']-cfg['fitted_energy'])<.0001
    assert np.allclose(lamp['color'],cfg['reflector']['color']) and lamp['size']==cfg['reflector']['size'] and lamp['size_y']==cfg['reflector']['size_y'] and be['shadows'][added[0]]
    section=inspect(after);assert section['crossings']==[]
    report=dict(before=source,after=after,model_sha256=hashlib.sha256((ROOT/after).read_bytes()).hexdigest(),modified_profile_rows=modified,all_other_controls_exact=True,all_original_uvs_topology_attributes_and_packed_images_exact=True,foot_finish=cfg['finish'],remaining_material_graph_exact=True,old_lights_exact_except_disabled_foot=True,new_reflector=lamp,shadowing_enabled=True,camera_world_color_management_light_paths_exact=True,closed_profile_crossings=section['crossings'],render_receivers=receivers,profile=section['control_profile'])
    dest=ROOT/output;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('KING_FOOT_SHOULDER_SCOPE_PASS')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('config');p.add_argument('output');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);check(a.before,a.after,a.config,a.output)
