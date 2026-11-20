"""Move one softbox across each flank of a carving with registered cameras."""
from pathlib import Path
import hashlib,json,math,sys
import bpy
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:]
root,model,out=map(lambda x:Path(x).resolve(),args[:3])
feature=args[3] if len(args)>3 else 'eye'
assert feature in ('eye','poll')
sys.path.insert(0,str(root/'scripts/knight'))
from mission_scene import configure_render,render
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=root/'models/knight/knight-rebuilt.blend'
bpy.ops.wm.open_mainfile(filepath=str(parent),load_ui=False)
s=bpy.context.scene
yaw=math.radians(json.loads(s['knight_mission_pose'])['twist_degrees'])
axis=Vector((math.cos(yaw),math.sin(yaw),0))
across=Vector((-axis.y,axis.x,0));up=Vector((0,0,1))
aims={k:list(s.objects[f'Knight | {k} eye'].matrix_world.translation) for k in ('near','far')}
if feature=='poll':
    pose=json.loads(s['knight_mission_pose'])
    poll=Vector((pose['dx'],pose['dy'],4.78))-.44*axis
    aims={k:list(poll) for k in aims}
parent_hash=sha(parent)
if model!=parent:bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
s=bpy.context.scene
for obj in s.objects:
    if obj.type=='LIGHT':obj.hide_render=True
world=bpy.data.worlds.new('Raking light / background')
world.use_nodes=True
world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.60,.60,.60,1)
world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.22
s.world=world
data=bpy.data.lights.new('Eye study softbox','AREA')
data.shape='RECTANGLE';data.size=2.15;data.size_y=3.6;data.energy=290
light=bpy.data.objects.new('Eye study softbox',data);s.collection.objects.link(light)
configure_render(s,32);s.render.resolution_x=396;s.render.resolution_y=268
cam=s.camera;cam.data.type='ORTHO';cam.data.ortho_scale=1.20;cam.data.shift_x=0;cam.data.shift_y=0
if feature=='poll':cam.data.ortho_scale=2.30
out.mkdir(parents=True,exist_ok=True);views={};rig={}
for flank,sign in [('near',-1),('far',1)]:
    center=Vector(aims[flank])
    elevation=.70 if feature=='poll' else .14
    cam.location=center+7*(sign*across+.12*axis+elevation*up)
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    for name,azimuth in [('from-poll',-58),('across',0),('from-nose',58)]:
        a=math.radians(azimuth)
        height=4.25 if feature=='poll' else 2.0
        light.location=center+4.3*(axis*math.sin(a)+sign*across*math.cos(a)) + height*up
        light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
        f=out/f'{flank}-{name}.png';render(s,f);views[f.name]=sha(f)
        rig[f.name]={'light':list(light.location),'camera':list(cam.location)}
(out/'source.json').write_text(json.dumps({'model':sha(model),'framing_model':parent_hash,'feature':feature,'rig':rig,'views':views,'method':'Common cameras centered on the same feature on the released parent. One rectangular softbox moves from the poll through broadside to the nose. Both flanks use mirrored lamp positions, identical framing, exposure and ambient light.'},indent=2)+'\n')
