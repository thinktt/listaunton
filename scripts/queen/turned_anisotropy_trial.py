"""Test directional polish along the physical circumference of the lathed body.

Use object coordinates, not the arbitrarily rotated packed-atlas UV islands.
The crown bowl and finial retain their isotropic material response.
"""
from pathlib import Path
import hashlib, json
import bpy

ROOT = Path(__file__).resolve().parents[2]
source = ROOT / 'models/queen/queen-rebuilt.blend'
source_hash = '82100ad9047426b1be46e72d01d769189b4e9f667005fd8c8bcc5d743c16526e'
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
scene = bpy.context.scene
obj = next(o for o in scene.objects if o.type == 'MESH' and not o.hide_render)
nodes, links = obj.data.materials[0].node_tree.nodes, obj.data.materials[0].node_tree.links
bsdf = nodes.get('Principled BSDF')
coords = nodes.new('ShaderNodeTexCoord')
separate = nodes.new('ShaderNodeSeparateXYZ')
links.new(coords.outputs['Object'], separate.inputs[0])
negative_y = nodes.new('ShaderNodeMath')
negative_y.operation = 'MULTIPLY'
negative_y.inputs[1].default_value = -1
links.new(separate.outputs['Y'], negative_y.inputs[0])
tangent = nodes.new('ShaderNodeCombineXYZ')
links.new(negative_y.outputs[0], tangent.inputs['X'])
links.new(separate.outputs['X'], tangent.inputs['Y'])
normalize = nodes.new('ShaderNodeVectorMath')
normalize.operation = 'NORMALIZE'
links.new(tangent.outputs[0], normalize.inputs[0])
links.new(normalize.outputs[0], bsdf.inputs['Tangent'])
anisotropy = nodes.new('ShaderNodeMapRange')
anisotropy.clamp = True
anisotropy.inputs['From Min'].default_value = 3.8
anisotropy.inputs['From Max'].default_value = 4.0
anisotropy.inputs['To Min'].default_value = .9
anisotropy.inputs['To Max'].default_value = 0
links.new(separate.outputs['Z'], anisotropy.inputs['Value'])
links.new(anisotropy.outputs[0], bsdf.inputs['Anisotropic'])
settings = json.loads(scene['mission_material_config'])
settings['variant'] = '081-circumferential-polish'
settings['circumferential_polish'] = {'source_sha256': source_hash, 'anisotropy': .9,
    'fade_z': [3.8, 4.0], 'tangent': 'normalize(-object_y, object_x, 0)',
    'hypothesis': 'Turned wood may stretch reflected glints around collars and socket while the finial retains compact spots. Packed texture atlas tangents do not reliably represent turning direction.'}
scene['mission_material_config'] = json.dumps(settings, sort_keys=True)
out = ROOT / 'build/queen-mission' / settings['variant']
out.mkdir(parents=True, exist_ok=True)
scene.render.filepath = str(out / 'wood.png')
scene.cycles.samples = 64
scene.cycles.use_denoising = True
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'queen.blend'))
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.get_devices()
for device in prefs.devices:
    device.use = device.type == 'OPTIX'
if any(device.use for device in prefs.devices):
    scene.cycles.device = 'GPU'
bpy.ops.render.render(write_still=True)
(out / 'parameters.json').write_text(json.dumps(settings, indent=2) + '\n')
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
print('CIRCUMFERENTIAL_POLISH_DONE', flush=True)
