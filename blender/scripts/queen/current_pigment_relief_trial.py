"""Test relief driven by current color grain, retaining the accepted shape/rig."""
from pathlib import Path
import hashlib,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
source=ROOT/'history/queen-mission-008/queen-rebuilt.blend'
digest='c32bccbf33e5e137d982bdeafd881a783b006f62e644dbd5db2df57d02801004'
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene;obj=editable_mesh(scene)
nodes=obj.data.materials[0].node_tree.nodes;links=obj.data.materials[0].node_tree.links
bs=nodes.get('Principled BSDF');bump=bs.inputs['Normal'].links[0].from_node
assert bump.type=='BUMP'
mix=bump.inputs['Height'].links[0].from_node;assert mix.type=='MIX_RGB'
height=mix.inputs[1].links[0].from_node;assert height.type=='MAP_RANGE'
old_gray=height.inputs['Value'].links[0].from_node
old_atlas=old_gray.inputs[0].links[0].from_node.image.name
gray=nodes.new('ShaderNodeRGBToBW');gray.label='Relief from current v4 pigment'
links.new(bs.inputs['Base Color'].links[0].from_socket,gray.inputs[0])
links.new(gray.outputs[0],height.inputs['Value'])
cfg=json.loads(scene['mission_material_config'])
cfg['variant']='090-current-pigment-relief'
cfg['current_pigment_relief_trial']={'baseline':source.relative_to(ROOT).as_posix(),'source_sha256':digest,'previous_relief_atlas':old_atlas,'new_relief_source':'Current Base Color, v4 pigment atlas','all_relief_scalars_and_lighting_unchanged':True,'hypothesis':'Replace coarse invented relief lines with the finer grain already used by the current pigment.'}
scene['mission_material_config']=json.dumps(cfg,sort_keys=True)
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
scene.render.filepath=str(out/'wood.png');scene.cycles.samples=64;scene.cycles.use_denoising=True
scene.render.use_persistent_data=True;bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('CURRENT_PIGMENT_RELIEF_TRIAL_DONE',flush=True)
