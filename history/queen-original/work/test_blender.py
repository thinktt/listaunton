import bpy
import sys
import json
from pathlib import Path

out = Path(r'C:\Users\toby\Documents\Codex\2026-10-01\go-x20\work\blender-test')
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=False)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 16
scene.render.resolution_x = 384
scene.render.resolution_y = 384
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(out / 'python-test.png')
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'python-test.blend'))
bpy.ops.render.render(write_still=True)
report = {'blender': bpy.app.version_string, 'python': sys.version, 'blend_file': str(out / 'python-test.blend'), 'render': scene.render.filepath, 'render_exists': Path(scene.render.filepath).is_file()}
(out / 'result.json').write_text(json.dumps(report, indent=2))
print('PYTHON_TEST_SUCCESS ' + json.dumps(report))
