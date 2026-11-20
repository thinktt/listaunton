"""Test whether two pigment-atlas bakes soften the fine reference grain."""
from pathlib import Path
import hashlib,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
source=ROOT/'history/queen-mission-008/queen-rebuilt.blend'
digest='c32bccbf33e5e137d982bdeafd881a783b006f62e644dbd5db2df57d02801004'
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;o=editable_mesh(s);n=o.data.materials[0].node_tree.nodes;l=o.data.materials[0].node_tree.links
bs=n.get('Principled BSDF');projection=n.get('Mix (Legacy).007');grade=n.get('Vector Math.007')
assert projection.inputs[2].links[0].from_node.image.name=='Queen linear inferred pigment'
assert grade.operation=='MULTIPLY' and grade.inputs[0].links[0].from_node.image.name=='Queen pigment atlas.002'
l.new(projection.outputs[0],grade.inputs[0]);l.new(grade.outputs[0],bs.inputs['Base Color'])
cfg=json.loads(s['mission_material_config']);cfg['variant']='093-direct-pigment-graph'
cfg['direct_pigment_graph']={'baseline':source.relative_to(ROOT).as_posix(),'source_sha256':digest,'method':'Reconnect the packed full-resolution inferred pigment, original fallback/coverage and accepted regional grade before the v3/v4 atlas bakes. No image pixels, geometry, relief, camera or lights change.','hypothesis':'Repeated 2048-square atlas filtering may attenuate fine grain while retaining coarser markings.'}
s['mission_material_config']=json.dumps(cfg,sort_keys=True)
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
s.render.filepath=str(out/'wood.png');s.cycles.samples=64;s.cycles.use_denoising=True;s.render.use_persistent_data=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('DIRECT_PIGMENT_GRAPH_TRIAL_DONE',flush=True)
