from pathlib import Path
import hashlib,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
from focused_reflections import target
from render_regions import controls,clear_light_path

source=ROOT/'history/king-mission-006/king-rebuilt.blend'
expected='96f3d023c799f79fd12cc19baf5f2b3e535ec969eda7573c9bc7e464f4ea8ba5'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;gpu(s)
out=ROOT/'build/king-mission/081-foot-diagnostic';out.mkdir(parents=True,exist_ok=True)
lights=[o for o in s.objects if o.type=='LIGHT']
rows=[]
for o in lights:
    d=o.data;c=o.light_linking.receiver_collection
    rows.append(dict(name=o.name,power=d.energy,type=d.type,position=list(o.location),color=list(d.color),radius=getattr(d,'shadow_soft_size',None),size=getattr(d,'size',None),size_y=getattr(d,'size_y',None),cone=getattr(d,'spot_size',None),diffuse=o.visible_diffuse,glossy=o.visible_glossy,receivers=[p.get('king_render_region',p.name) for p in c.objects] if c else None))
probes=[]
for x,y in [(340,1018),(380,1030),(420,1040),(460,1046),(500,1048)]:
    for dy in [-4,0,4,8]:
        ob,point,direction,normal=target(s,x,y+dy)
        probes.append(dict(pixel=[x,y+dy],receiver=ob.get('king_render_region'),point=list(point),normal=list(normal),clear=clear_light_path(s,point,normal,direction,6)))
materials=[]
for ob in controls(s):
    mat=ob.data.materials[0]
    materials.append(dict(object=ob.name,nodes=[dict(name=n.name,type=n.bl_idname,inputs={i.name:list(i.default_value) if hasattr(i.default_value,'__iter__') else i.default_value for i in n.inputs if hasattr(i,'default_value') and isinstance(i.default_value,(float,int)) or hasattr(i,'default_value') and type(i.default_value).__name__=='bpy_prop_array'}) for n in mat.node_tree.nodes]))
(out/'diagnostic.json').write_text(json.dumps(dict(source_sha256=expected,lights=rows,probes=probes,materials=materials),indent=2)+'\n',encoding='utf-8')
w=s.render.resolution_x;h=s.render.resolution_y
s.render.use_border=True;s.render.use_crop_to_border=False
s.render.border_min_x=200/w;s.render.border_max_x=805/w;s.render.border_min_y=1-1110/h;s.render.border_max_y=1-945/h
s.cycles.samples=128;s.cycles.use_denoising=True;s.render.use_persistent_data=True
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
powers={o.name:o.data.energy for o in lights}
foot=bpy.data.objects['Foot left reflection'];foot.data.energy=0
s.render.filepath=str(out/'without-foot.png');bpy.ops.render.render(write_still=True)
for o in lights:o.data.energy=0
world=s.world.node_tree.nodes['Background'];world.inputs['Strength'].default_value=0
foot.data.energy=powers[foot.name]
s.render.filepath=str(out/'foot-only.png');bpy.ops.render.render(write_still=True)
foot.data.energy=powers[foot.name]*8
s.render.filepath=str(out/'foot-only-eight.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
print('FOOT_DIAGNOSTIC_COMPLETE')
