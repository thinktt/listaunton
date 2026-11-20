"""Use the released parent’s actual studio on every eye while keeping the candidate’s wood and carving."""
import hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Matrix

root,parent,model,dest=map(lambda arg:Path(arg).resolve(),sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(root/'scripts/knight'))
from mission_scene import configure_render,render
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=digest(model);parent_sha=digest(parent)
bpy.ops.wm.open_mainfile(filepath=str(parent),load_ui=False)
s=bpy.context.scene
lamps=[(o.name,o.data.name,[list(row) for row in o.matrix_world]) for o in s.objects if o.type=='LIGHT' and not o.hide_render]
world=s.world.name
if model!=parent:
    bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
    s=bpy.context.scene
    parent_light_names={name for name,_,_ in lamps}
    for o in s.objects:
        if o.type=='LIGHT':o.hide_render=o.name not in parent_light_names
    data_names=sorted({name for _,name,_ in lamps})
    with bpy.data.libraries.load(str(parent),link=False) as (incoming,chosen):
        assert all(name in incoming.lights for name in data_names)
        chosen.lights=list(data_names)
        chosen.worlds=[world]
    lights=dict(zip(data_names,chosen.lights))
    s.world=chosen.worlds[0]
    for oname,lname,transform in lamps:
        # The original objects carry Cycles receiver and blocker links.
        lamp=s.objects[oname]
        lamp.data=lights[lname]
        lamp.matrix_world=Matrix(transform)
configure_render(s,96)
s.render.use_border=True;s.render.use_crop_to_border=False
side=s.render.resolution_x
s.render.border_min_x=410/side;s.render.border_max_x=599/side
s.render.border_min_y=1-552/side;s.render.border_max_y=1-405/side
dest.mkdir(parents=True,exist_ok=True);file=dest/'fixed.png';render(s,file)
assert source==digest(model) and parent_sha==digest(parent)
(dest/'source.json').write_text(json.dumps({'model':source,'parent_studio':parent_sha,'render':digest(file),'lights':[row[0] for row in lamps],'method':'Every actual candidate receives the same original 10B lamp datablocks, world and world transforms in its own saved reference camera. 96 samples on a cropped film gate.'},indent=2)+'\n')
