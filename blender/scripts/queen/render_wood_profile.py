"""Render the saved queen from the same side camera as the neutral profile."""
from pathlib import Path
import hashlib
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/'models/queen/queen-rebuilt.blend'
before=hashlib.sha256(MODEL.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(MODEL),load_ui=False)
scene=bpy.context.scene;camera=scene.camera
camera.data.shift_x=0;camera.data.shift_y=0;camera.data.sensor_fit='VERTICAL';camera.data.ortho_scale=6.6
camera.location=(0,-16,2.55)
camera.rotation_euler=(Vector((0,0,2.55))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=600;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.cycles.samples=48;scene.cycles.use_denoising=True
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    gpu=False
    for device in prefs.devices:
        device.use=device.type=='OPTIX';gpu|=device.use
    if gpu:scene.cycles.device='GPU'
except Exception as error:print('CPU fallback:',error)
scene.render.filepath=str(ROOT/'assets/queen/queen-wood-profile.png')
bpy.ops.render.render(write_still=True)
assert hashlib.sha256(MODEL.read_bytes()).hexdigest()==before,'Rendering modified the model file'
print('WOOD_PROFILE_RENDERED')
