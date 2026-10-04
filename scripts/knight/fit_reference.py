"""Small bounded camera study; Blender renders only, fitting is a separate script."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];out=root/'assets/knight/reference-fit';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'models/knight/knight-rebuilt.blend'))
scene=bpy.context.scene;cam=scene.camera
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=scene.render.resolution_y=600
scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
scene.display.shading.light='STUDIO';scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=False
cfg=json.loads((root/'scripts/knight/profile.json').read_text());e=math.radians(54);target=Vector((0,0,(cfg['y0']-150)/(cfg['scale']*math.cos(e))))
cam.data.ortho_scale=300/cfg['scale'];cam.data.shift_x=(150-cfg['cx'])/300;cam.data.shift_y=0
for yaw in [-12,-6,0,6,12]:
 a=math.radians(yaw);cam.location=target+Vector((12*math.sin(a)*math.cos(e),-12*math.cos(a)*math.cos(e),12*math.sin(e)))
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(out/f'yaw-{yaw:+d}.png');bpy.ops.render.render(write_still=True)
