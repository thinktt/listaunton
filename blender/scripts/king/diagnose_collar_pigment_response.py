"""Read-only separation of king pigment and real-BSDF reflection response."""
from pathlib import Path
import argparse, hashlib, json, sys
import bpy
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mission_trial import ROOT, gpu
from render_regions import controls

p = argparse.ArgumentParser()
p.add_argument('source'); p.add_argument('response'); p.add_argument('output')
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
source = ROOT / a.source; out = ROOT / a.output; out.mkdir(parents=True, exist_ok=True)
digest = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
s = bpy.context.scene; gpu(s)
mat = controls(s)[0].data.materials[0]; n = mat.node_tree.nodes; l = mat.node_tree.links
report = {'source_sha256': digest, 'nodes': {}, 'principled_inputs': {}}
for node in n:
    report['nodes'][node.name] = {'type': node.bl_idname, 'inputs': {sock.name: (str(sock.default_value[:]) if hasattr(sock.default_value, '__len__') else sock.default_value) for sock in node.inputs if hasattr(sock, 'default_value') and not sock.is_linked}}
bs = n['Principled BSDF']
for sock in bs.inputs:
    if sock.is_linked: report['principled_inputs'][sock.name] = [(x.from_node.name, x.from_socket.name) for x in sock.links]
s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGBA'
for name in ['black', 'white']:
    im = bpy.data.images.load(str(ROOT / a.response / (name + '.exr')), check_existing=False)
    im.save_render(str(out / (name + '-response.png')), scene=s)
output = next(node for node in n if node.type == 'OUTPUT_MATERIAL')
emission = n.new('ShaderNodeEmission')
l.new(bs.inputs['Base Color'].links[0].from_socket, emission.inputs['Color'])
l.new(emission.outputs[0], output.inputs['Surface'])
s.cycles.samples = 32
s.render.filepath = str(out / 'pigment-diagnostic.png'); bpy.ops.render.render(write_still=True)
(out / 'material.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
print('KING_FINISH_DIAGNOSTIC_PASS', flush=True)
