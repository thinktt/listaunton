"""Render an independent rear oblique view of the real mitre cut; leave saved camera unchanged."""
from pathlib import Path
import bpy,math
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(root/'models/bishop/bishop-rebuilt.blend'))
scene=bpy.context.scene;camera=scene.camera
target=Vector((0,0,2.1));e=math.radians(28);az=math.radians(120)
camera.location=target+Vector((10*math.sin(az)*math.cos(e),-10*math.cos(az)*math.cos(e),10*math.sin(e)))
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.shift_x=0;camera.data.shift_y=0;camera.data.ortho_scale=6
scene.render.resolution_x=768;scene.render.resolution_y=768;scene.cycles.samples=24
scene.render.filepath=str(root/'assets/bishop/rear-oblique.png')
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type=='CUDA'
 if any(dev.type=='CUDA' for dev in prefs.devices):scene.cycles.device='GPU'
except Exception:pass
bpy.ops.render.render(write_still=True)
