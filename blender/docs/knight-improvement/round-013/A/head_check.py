"""View the whole native head with one plain studio on three real obliques."""
from pathlib import Path
import bpy,sys,json,math
from mathutils import Vector
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from diagnostic_views import open_model,clay_studio,configure_render,render
for n in ['parent','knight']:
    s=open_model(n+'.blend');configure_render(s,20);yaw=json.loads(s['knight_mission_pose'])['twist_degrees'];clay_studio(s,yaw)
    s.render.resolution_x=396;s.render.resolution_y=270
    cam=s.camera;cam.data.ortho_scale=3.68;cam.data.shift_x=cam.data.shift_y=0
    aim=Vector((-.14,-.03,4.04))
    for angle in [-30,0,30]:
        a=math.radians(yaw+angle);e=math.radians(9.)
        cam.location=aim+8*Vector((math.sin(a)*math.cos(e),-math.cos(a)*math.cos(e),math.sin(e)))
        cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler()
        render(s,D/f'head-{n}-{angle}.png')
