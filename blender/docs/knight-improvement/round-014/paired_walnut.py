"""Render the two walnut flanks with a single studio symmetrical about the head."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
p=argparse.ArgumentParser()
p.add_argument('root',type=Path);p.add_argument('source',type=Path);p.add_argument('out',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(a.root.resolve()/'scripts/knight'))
from mission_scene import configure_render,render
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
source=sha(a.source)
bpy.ops.wm.open_mainfile(filepath=str(a.source.resolve()),load_ui=False)
s=bpy.context.scene
pose=json.loads(s['knight_mission_pose'])
theta=math.radians(pose['twist_degrees'])
long_axis=Vector((math.cos(theta),math.sin(theta),0))
cross_axis=Vector((-math.sin(theta),math.cos(theta),0))
up=Vector((0,0,1));target=Vector((pose['dx'],pose['dy'],3.0))
for obj in s.objects:
    if obj.type=='LIGHT':obj.hide_render=True
def area(name,x,y,z,power,diameter):
    lamp=bpy.data.lights.new(name,'AREA');lamp.energy=power;lamp.shape='DISK';lamp.size=diameter
    obj=bpy.data.objects.new(name,lamp);s.collection.objects.link(obj)
    obj.location=target+x*long_axis+y*cross_axis+z*up
    obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler()
for sign in (-1,1):
    area(f'Walnut key {sign}',2.8,sign*4.5,4.7,540,4.0)
    area(f'Walnut edge {sign}',-3.5,sign*2.3,2.9,270,2.0)
s.world=bpy.data.worlds.new('Neutral wood studio')
s.world.use_nodes=True
bg=s.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value=(.55,.55,.55,1)
bg.inputs['Strength'].default_value=.28
configure_render(s,32)
s.render.resolution_x=s.render.resolution_y=640
cam=s.camera;cam.data.shift_x=cam.data.shift_y=0;cam.data.ortho_scale=5.6
cam.data.type='ORTHO'
a.out=a.out.resolve()
a.out.mkdir(exist_ok=True,parents=True)
for name,sign in [('near',-1),('far',1)]:
    elev=math.radians(8)
    cam.location=target+12*(math.cos(elev)*sign*cross_axis+math.sin(elev)*up)
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    render(s,a.out/(name+'.png'))
assert sha(a.source)==source
(a.out/'source.json').write_text(json.dumps({'source_sha256':source,'width':640,'ortho_scale':5.6,'elevation':8,'head_yaw':pose['twist_degrees'],'outputs':{n:sha(a.out/(n+'.png')) for n in ['near','far']},'method':'Real walnut on the saved mesh. One symmetrical four-area-light studio. Camera views are equally spaced on the two sides of the upper head at 8 degrees. The far render is horizontally reversed only in the comparison sheet.'},indent=2)+'\n')
