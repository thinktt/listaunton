"""Isolated first rook wood study; never overwrites accepted assets."""
from pathlib import Path
import sys, hashlib, json, math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts/king'))
from mission_trial import gpu, procedural_material

source = ROOT/'models/rook/rook-rebuilt.blend'
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
assert source_hash == '23abce50f4a7bd6544f7844534e69a02e3a337a64ee7ce214e81acc353a26f2c'
out = ROOT/'build/rook-mission/001-procedural-baseline'
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
scene = bpy.context.scene
camera = scene.camera
axis = camera.matrix_world.to_3x3() @ Vector((0,0,1))
elevation = math.degrees(math.asin(axis.z))
assert abs(elevation-54)<.001
geometry = {ob.name: hashlib.sha256(bytes(str([(tuple(v.co)) for v in ob.data.vertices]),'utf8')).hexdigest() for ob in scene.objects if ob.type=='MESH'}
mat = procedural_material({'roughness':.25,'coat':.35,'coat_roughness':.15})
mat.name = 'Rook walnut initial procedural study'
for ob in scene.objects:
    if ob.type=='MESH':
        ob.data.materials.clear()
        ob.data.materials.append(mat)
scene.cycles.samples=64
scene.render.resolution_percentage=60
scene.render.image_settings.color_mode='RGBA'
gpu(scene)
devices=[{'name':d.name,'type':d.type} for d in bpy.context.preferences.addons['cycles'].preferences.devices if d.use]
assert any(d['type']=='OPTIX' for d in devices)
scene.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False)
scene=bpy.context.scene
gpu(scene)
bpy.ops.render.render(write_still=True)
camera=scene.camera
camera.data.shift_x=0
camera.data.shift_y=0
camera.data.ortho_scale=4.5
camera.location=(0,-12,1.4)
camera.rotation_euler=(Vector((0,0,1.4))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(out/'side.png')
bpy.ops.render.render(write_still=True)
report={'source_sha256':source_hash,'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest(),'elevation':elevation,'devices':devices,'geometry':geometry,'status':'experimental; not accepted','notes':'Unchanged geometry and reference camera; procedural wood baseline using existing lighting. Side camera change is not saved.'}
(out/'report.json').write_text(json.dumps(report,indent=2))
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
print('ROOK_WOOD_STUDY_COMPLETE')
