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
visibility=('visible_camera','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter','visible_shadow')
groups={}
states={}
for oname,_,_ in lamps:
    obj=s.objects[oname]
    links={}
    for role in ('receiver_collection','blocker_collection'):
        col=getattr(obj.light_linking,role)
        links[role]=col.name if col else None
        if col and col.name not in groups:
            assert len(col.children)==0,('unexpected nested light group',col.name)
            groups[col.name]=[(item.name,child.light_linking.link_state) for item,child in zip(col.objects,col.collection_objects)]
    states[oname]={'links':links,'ray_visibility':{prop:getattr(obj,prop) for prop in visibility}}
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
    local_groups={}
    for cname,members in groups.items():
        col=bpy.data.collections.new('Common studio / '+cname)
        for member,_ in members:col.objects.link(s.objects[member])
        by_name=dict(members)
        for obj,child in zip(col.objects,col.collection_objects):
            child.light_linking.link_state=by_name[obj.name]
        local_groups[cname]=col
    for oname,lname,transform in lamps:
        lamp=s.objects[oname]
        lamp.data=lights[lname]
        lamp.matrix_world=Matrix(transform)
        for role,cname in states[oname]['links'].items():
            setattr(lamp.light_linking,role,local_groups[cname] if cname else None)
        for prop,value in states[oname]['ray_visibility'].items():setattr(lamp,prop,value)
configure_render(s,96)
s.render.use_border=True;s.render.use_crop_to_border=False
side=s.render.resolution_x
s.render.border_min_x=410/side;s.render.border_max_x=599/side
s.render.border_min_y=1-552/side;s.render.border_max_y=1-405/side
dest.mkdir(parents=True,exist_ok=True);file=dest/'fixed.png';render(s,file)
assert source==digest(model) and parent_sha==digest(parent)
(dest/'source.json').write_text(json.dumps({'model':source,'parent_studio':parent_sha,'render':digest(file),'lights':states,'light_groups':groups,'method':'The parent lamp data, world, transforms, ray visibility and per-object Cycles light links are applied to the saved candidate mesh, material and reference camera. This 96-sample exposure uses the same cropped film gate for all three models.'},indent=2)+'\n')
