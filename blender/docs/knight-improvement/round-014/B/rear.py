"""Photograph the hanging mane from behind and from both rear quarters."""
from pathlib import Path
import hashlib,json,math,sys
import bpy,numpy as np
from mathutils import Vector
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
args=sys.argv[sys.argv.index('--')+1:]
root,model,out=map(lambda x:Path(x).resolve(),args[:3])
opts=args[3:];pigment_only='--pigment-only' in opts
quick='--quick' in opts
sys.path.insert(0,str(root/'scripts/knight'))
from mission_scene import configure_render,render,visible_meshes
from mission_pose import posed
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=sha(model)
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);s=bpy.context.scene
if '--atlas' in opts:
    from candidate import install
    install(s,D/f"atlas-{opts[opts.index('--atlas')+1]}.png")
pose=json.loads(s['knight_mission_pose'])
args=[pose[k] for k in ('dx','dy','twist_degrees')]
positions=posed(np.array([[-.72,0,3.38],[.28,0,3.38]]),*args)
center=Vector(positions[0]);axis=Vector(positions[1]-positions[0]).normalized()
up=Vector((0,0,1));across=up.cross(axis).normalized()
for obj in s.objects:
    if obj.type=='LIGHT':obj.hide_render=True
def area(name,relative,power,width):
    l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=width
    ob=bpy.data.objects.new(name,l);s.collection.objects.link(ob)
    ob.location=center+relative;ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler()
for sign in (-1,1):
    area(f'Front softbox {sign}',2.9*axis+sign*3.8*across+4*up,290,3.2)
    area(f'Back strip {sign}',-2.9*axis+sign*2.0*across+2.6*up,185,1.8)
s.world=bpy.data.worlds.new('Quiet studio');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.23
clay=bpy.data.materials.new('Matte relief check');clay.use_nodes=True
bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.41,.425,.428,1);bs.inputs['Roughness'].default_value=.62
configure_render(s,28);s.render.resolution_x=412;s.render.resolution_y=480
s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=4
if quick:s.render.resolution_percentage=70;s.cycles.samples=16
cam=s.camera;cam.data.type='ORTHO';cam.data.shift_x=cam.data.shift_y=0;cam.data.ortho_scale=2.97
out.mkdir(parents=True,exist_ok=True);views={}
for finish in (('pigment',) if pigment_only else ('walnut',) if quick else ('walnut','clay')):
    if finish=='pigment':
        for mat in {slot.material for obj in visible_meshes(s) for slot in obj.material_slots if slot.material}:
            nodes=mat.node_tree.nodes;links=mat.node_tree.links
            base=nodes['Principled BSDF'].inputs['Base Color'].links[0].from_socket
            emission=nodes.new('ShaderNodeEmission');links.new(base,emission.inputs['Color'])
            output=next(node for node in nodes if node.type=='OUTPUT_MATERIAL' and node.is_active_output)
            links.new(emission.outputs[0],output.inputs['Surface'])
    if finish=='clay':
        for obj in visible_meshes(s):
            for slot in obj.material_slots:slot.material=clay
    for name,deg in [('near-quarter',-59),('back',0),('far-quarter',59)]:
        angle=math.radians(deg)
        ray=math.cos(angle)*(-axis)+math.sin(angle)*across+.16*up
        cam.location=center+10*ray.normalized();cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
        file=out/f'{finish}-{name}.png';render(s,file);views[file.name]=sha(file)
assert sha(model)==source
(out/'source.json').write_text(json.dumps({'source_sha256':source,'views':views,'center':list(center),'method':'Rear and opposed 59-degree rear quarters of the actual mesh at the height of the neck. Same paired lights, scale and framing for walnut and matte clay. The optional pigment-only exposure routes the saved base color directly to emission.'},indent=2)+'\n')
