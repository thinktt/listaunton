"""Render the actual sockets from both sides under one symmetrical studio."""
import hashlib,json,math,sys
sys.dont_write_bytecode=True
from pathlib import Path
import bpy
from mathutils import Vector

root,model,out=map(lambda arg:Path(arg).resolve(),sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(root/'scripts/knight'))
from mission_scene import configure_render,render,visible_meshes
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
source=digest(model)
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
s=bpy.context.scene
yaw=math.radians(json.loads(s['knight_mission_pose'])['twist_degrees'])
axis=Vector((math.cos(yaw),math.sin(yaw),0))
across=Vector((-axis.y,axis.x,0))
up=Vector((0,0,1))
eyes={name:bpy.data.objects['Knight | '+name+' eye'].matrix_world.translation.copy() for name in ('near','far')}
center=(eyes['near']+eyes['far'])/2
for obj in s.objects:
    if obj.type=='LIGHT': obj.hide_render=True
def lamp(label,location,power,size):
    l=bpy.data.lights.new(label,'AREA');l.energy=power;l.shape='DISK';l.size=size
    o=bpy.data.objects.new(label,l);s.collection.objects.link(o)
    o.location=location;o.rotation_euler=(center-location).to_track_quat('-Z','Y').to_euler()
for side in (-1,1):
    lamp(f'Key {side}',center-1.8*axis+side*3.4*across+4.0*up,250,2.6)
    lamp(f'Fill {side}',center+2.2*axis+side*2.8*across+1.2*up,75,3.5)
s.world=bpy.data.worlds.new('Soft portrait ambient')
s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.24
configure_render(s,40)
s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=4
s.render.resolution_x=512;s.render.resolution_y=360
cam=s.camera;cam.data.type='ORTHO';cam.data.ortho_scale=1.42;cam.data.shift_x=cam.data.shift_y=0
plain=bpy.data.materials.new('Untextured eye carving')
plain.use_nodes=True
bs=plain.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.4,.42,.43,1);bs.inputs['Roughness'].default_value=.62
out.mkdir(parents=True,exist_ok=True)
views={}
for finish in ('walnut','clay'):
    if finish=='clay':
        for obj in visible_meshes(s):
            for slot in obj.material_slots: slot.material=plain
    for name,side in [('near',-1),('far',1)]:
        aim=eyes[name]
        cam.location=aim+7*(side*across+.09*axis+.12*up)
        cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler()
        file=out/f'{finish}-{name}.png'
        render(s,file);views[file.name]=digest(file)
assert source==digest(model)
(out/'source.json').write_text(json.dumps({'model':source,'views':views,'method':'Real left and right eyes framed at their object centers with the same orthographic width (1.42 units), symmetrical lamps, and native walnut or common neutral clay.'},indent=2)+'\n')
