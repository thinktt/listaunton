from pathlib import Path
import sys,math,json,bpy
from mathutils import Vector
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D));from diagnostic_views import *
s=open_model('knight.blend');configure_render(s,24);s.render.resolution_x=s.render.resolution_y=430
render(s,D/'board-trial.png')
for name,az in [('near-quarter',232),('back',270),('far-quarter',308),('near',0),('far',180)]:
    angle=json.loads(s['knight_mission_pose'])['twist_degrees']+az
    orbit(s,angle,11,Vector((0,0,2.63)));render(s,D/f'turn-{name}.png')
