"""Render a registered side-study view; saved reference camera remains untouched."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];out=root/'assets/knight'
bpy.ops.wm.open_mainfile(filepath=str(root/'models/knight/knight-rebuilt.blend'))
scene=bpy.context.scene;cam=scene.camera
scene.cycles.samples=20
scene.render.resolution_x=scene.render.resolution_y=1254
cam.data.ortho_scale=1254/(565/3);cam.data.shift_x=3/1254;cam.data.shift_y=0
e=math.radians(7)
# Align the physical lowest projected point, rather than the center of the base.
graph=bpy.context.evaluated_depsgraph_get();min_up=float('inf')
for ob in scene.objects:
 if ob.type!='MESH' or ob.hide_render:continue
 ev=ob.evaluated_get(graph);me=ev.to_mesh()
 for vert in me.vertices:
  p=ob.matrix_world@vert.co;min_up=min(min_up,p.y*math.sin(e)+p.z*math.cos(e))
 ev.to_mesh_clear()
target=Vector((0,0,(min_up+(1127-627)/(565/3))/math.cos(e)))
cam.location=target+Vector((0,-12*math.cos(e),12*math.sin(e)))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(out/'guide-render.png')
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type=='CUDA'
 if any(dev.type=='CUDA' for dev in prefs.devices):scene.cycles.device='GPU'
except Exception:pass
bpy.ops.render.render(write_still=True)
(out/'guide-camera.json').write_text(json.dumps({'elevation':7,'azimuth':0,'guideBaseWidth':565,'guideBaseCenterX':624,'guideFloorY':1127,'pixelsPerWorldUnit':565/3,'target':list(target),'orthoScale':cam.data.ortho_scale,'shiftX':cam.data.shift_x,'note':'Approximate inferred study camera; fixed base width and physical floor. No rotation, warp, or anisotropic fit of the source image.'},indent=2))
