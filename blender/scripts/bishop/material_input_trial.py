"""Save and render an isolated experiment with declared material inputs/links."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('config')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads((ROOT/a.config).read_text())
source=ROOT/cfg['source'];out=ROOT/'build/bishop-mission'/cfg['variant']
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
out.mkdir(parents=True,exist_ok=True);digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
changes=[]
for edit in cfg.get('inputs',[]):
    mat=bpy.data.materials[edit['material']];node=mat.node_tree.nodes[edit['node']]
    socket=node.inputs[edit['input']];assert not socket.is_linked
    before=socket.default_value
    assert isinstance(before,float) and isinstance(edit['value'],(int,float))
    if 'expected_before' in edit:assert abs(before-edit['expected_before'])<1e-6,(edit,before)
    socket.default_value=edit['value']
    changes.append(dict(edit,before=before,effective=socket.default_value))
for edit in cfg.get('links',[]):
    mat=bpy.data.materials[edit['material']];nodes=mat.node_tree.nodes;links=mat.node_tree.links
    target=nodes[edit['to_node']].inputs[edit['to_socket']]
    assert len(target.links)==1
    old=target.links[0]
    assert [old.from_node.name,old.from_socket.name]==edit['expected_from']
    links.new(nodes[edit['from_node']].outputs[edit['from_socket']],target)
s['bishop_material_input_trial']=json.dumps(cfg,sort_keys=True)
s.cycles.samples=cfg.get('samples',256);s.cycles.use_adaptive_sampling=False
s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'bishop.blend'))
# The beauty is made from the reopened artifact, never the transient shader state.
bpy.ops.wm.open_mainfile(filepath=str(out/'bishop.blend'),load_ui=False);s=bpy.context.scene
for edit in changes:
    value=bpy.data.materials[edit['material']].node_tree.nodes[edit['node']].inputs[edit['input']].default_value
    assert value==edit['effective']
for edit in cfg.get('links',[]):
    target=bpy.data.materials[edit['material']].node_tree.nodes[edit['to_node']].inputs[edit['to_socket']]
    assert len(target.links)==1
    assert [target.links[0].from_node.name,target.links[0].from_socket.name]==[edit['from_node'],edit['from_socket']]
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'parameters.json').write_text(json.dumps({'config':cfg,'source_sha256':digest,'source_unchanged':True,
 'saved_model_sha256':hashlib.sha256((out/'bishop.blend').read_bytes()).hexdigest(),
 'render_sha256':hashlib.sha256((out/'wood.png').read_bytes()).hexdigest(),
 'reopened_before_render':True,'changes':changes},indent=2)+'\n')
print('MATERIAL_INPUT_TRIAL_COMPLETE',cfg['variant'],flush=True)
