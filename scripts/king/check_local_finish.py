"""Check a local finish edit against a saved king, without changing either file."""
from pathlib import Path
import argparse, hashlib, json, sys
import bpy
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from render_regions import controls
from check_base_light_checkpoint import snapshot, graph
from check_socket_checkpoint import extra

def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def remaining_settings():
    s = bpy.context.scene
    return {'shadows': {o.name:o.data.use_shadow for o in s.objects if o.type == 'LIGHT'},
            'cycles': {key:getattr(s.cycles,key) for key in ('samples','use_adaptive_sampling','adaptive_threshold','use_denoising','use_light_tree','max_bounces','diffuse_bounces','glossy_bounces')},
            'engine':s.render.engine}

def check(before, after, config, output, identity=False, sampling_only=False):
    hashes = [sha(before),sha(after)]
    a, al, ar = snapshot(before); ae = extra(); aset = remaining_settings()
    b, bl, br = snapshot(after); be = extra(); bset = remaining_settings()
    if sampling_only:
        cfg=json.loads((ROOT/config).read_text(encoding='utf-8-sig'))
        assert cfg['source_sha256']==hashes[0] and cfg['use_light_tree'] is False
        aset['cycles']['use_light_tree']=False
    if not identity and not sampling_only:
        cfg = json.loads((ROOT/config).read_text(encoding='utf-8-sig'))
        assert cfg['source_sha256'] == hashes[0]
        if 'use_light_tree' in cfg:aset['cycles']['use_light_tree']=cfg['use_light_tree']
        assert not cfg.get('existing_light_power'), 'This validator requires unchanged lights'
        name = cfg['attribute']
        for ob in controls(bpy.context.scene):
            expected = np.zeros(len(ob.data.vertices),dtype=np.float32)
            if 'body' in ob.name:
                rings=np.arange(len(expected))//96
                lo,hi=cfg['ring_fade'];t=np.clip((rings-lo)/(hi-lo),0,1);expected[:]=1-t*t*(3-2*t)
                lo,hi=cfg['lower_fade'];t=np.clip((rings-lo)/(hi-lo),0,1);expected*=t*t*(3-2*t)
            actual=np.array([v.value for v in ob.data.attributes[name].data],dtype=np.float32)
            assert np.array_equal(actual,expected),('Finish region mismatch',ob.name)
            assert name not in a['objects'][ob.name]['attributes']
            b['objects'][ob.name]['attributes'].pop(name)
            be['all_float_attributes'][ob.name].pop(name)
        mat=controls(bpy.context.scene)[0].data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links;remove=set()
        for node_name,input_name,value in cfg['inputs']:
            socket=nodes[node_name].inputs[input_name];assert len(socket.links)==1
            mix=socket.links[0].from_node;assert mix.type=='MIX_RGB' and mix.blend_type=='MIX'
            assert np.allclose(mix.inputs[2].default_value,[value,value,value,1],rtol=0,atol=3e-8)
            attr=mix.inputs[0].links[0].from_node;assert attr.type=='ATTRIBUTE' and attr.attribute_name==name
            old=mix.inputs[1].links
            if old: links.new(old[0].from_socket,socket)
            else:
                links.remove(socket.links[0]);socket.default_value=mix.inputs[1].default_value[0]
            remove.update((mix,attr))
        assert len(remove)==len(cfg['inputs'])+1
        for node in remove:nodes.remove(node)
        for ob in controls(bpy.context.scene):b['objects'][ob.name]['material']=graph(ob.data.materials[0].node_tree)
    assert a==b,'Unexpected geometry, UV, material, camera, pigment, or world change'
    assert ae==be,'Unexpected original attribute or packed-image change'
    assert al==bl and aset==bset,'Light, shadow, or render setting changed'
    assert ar==br and br['receiverCount']==9,'Receiver partition or routing changed'
    assert hashes == [sha(before),sha(after)]
    report={'before':before,'after':after,'source_sha256':hashes[0],'model_sha256':hashes[1],
            'identity_check':identity,'sampling_only':sampling_only,'geometry_topology_original_uvs_and_attributes_exact':True,
            'all_packed_images_exact':True,'remaining_material_graph_exact':True,
            'lights_shadows_camera_world_exact':True,'remaining_render_settings_exact':True,
            'declared_light_tree_setting':None if identity else cfg.get('use_light_tree'), 'render_receivers':br,
            'declared_finish':None if identity or sampling_only else {k:cfg[k] for k in ('attribute','lower_fade','ring_fade','inputs')}}
    path=ROOT/output;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('KING_LOCAL_FINISH_SCOPE_PASS',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('config');p.add_argument('output');p.add_argument('--identity',action='store_true');p.add_argument('--sampling-only',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);check(a.before,a.after,a.config,a.output,a.identity,a.sampling_only)
