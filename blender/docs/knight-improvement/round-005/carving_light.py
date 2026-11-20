"""Render each mesh under the same plain clay and light for the owner's carving review."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector

p=argparse.ArgumentParser()
p.add_argument('root',type=Path)
p.add_argument('model',type=Path)
p.add_argument('output',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(a.root.resolve()/'scripts/knight'))
from mission_scene import configure_render,render,use_side_camera,visible_meshes
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
source=sha(a.model)
bpy.ops.wm.open_mainfile(filepath=str(a.model.resolve()),load_ui=False)
scene=bpy.context.scene
for obj in scene.objects:
    if obj.type=='LIGHT':obj.hide_render=True
clay=bpy.data.materials.new('Untextured carving check')
clay.diffuse_color=(.46,.465,.47,1)
clay.use_nodes=True
bs=clay.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=clay.diffuse_color
bs.inputs['Roughness'].default_value=.60
bs.inputs['Metallic'].default_value=0
for obj in visible_meshes(scene):
    for slot in obj.material_slots:slot.material=clay
scene.world=bpy.data.worlds.new('Carving review ambient')
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value=(.58,.58,.58,1);bg.inputs['Strength'].default_value=.23
target=Vector((-.2,0,3.2))
def light(name,pos,power,size):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj)
    obj.location=pos;obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler()
light('Carving key',(-3.8,-5.8,9.3),750,3.0)
light('Carving fill',(3,2,6.8),350,4.8)
light('Carving rim',(-3.7,3.5,5.8),280,3.2)
configure_render(scene,48)
out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
scene.render.resolution_x=scene.render.resolution_y=960
render(scene,out/'fixed.png')
use_side_camera(scene);render(scene,out/'side.png')
cam=scene.camera;target=Vector((-.1,0,2.7))
for name,deg,el in [('rear-quarter',224,13),('far-side',188,7)]:
    angle=math.radians(deg);elev=math.radians(el)
    cam.location=target+Vector((12*math.cos(elev)*math.sin(angle),-12*math.cos(elev)*math.cos(angle),12*math.sin(elev)))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.shift_x=cam.data.shift_y=0;cam.data.ortho_scale=6.18
    render(scene,out/(name+'.png'))
if source!=sha(a.model):
    raise ValueError('The model changed while its diagnostic renders were running.')
(out/'scene.json').write_text(json.dumps({'model':source,'views':{v:sha(out/(v+'.png')) for v in ('fixed','side','far-side','rear-quarter')}},indent=2)+'\n')
