"""Supplementary volume inspection without modifying the saved reference camera."""
import bpy,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(root/'models/knight/knight-rebuilt.blend'))
scene=bpy.context.scene;cam=scene.camera;scene.cycles.samples=16
scene.render.resolution_x=640;scene.render.resolution_y=640
cam.data.shift_x=0;cam.data.shift_y=0;cam.data.ortho_scale=6.4
for label,azimuth,elevation in [('side',0,16),('profile',0,0),('front',90,25),('opposite',180,40),('threequarter',45,20)]:
 a=math.radians(azimuth);e=math.radians(elevation);target=Vector((0,0,2.65))
 cam.location=target+Vector((12*math.sin(a)*math.cos(e),-12*math.cos(a)*math.cos(e),12*math.sin(e)))
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(root/'assets/knight'/('view-'+label+'.png'));bpy.ops.render.render(write_still=True)
