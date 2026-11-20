from pathlib import Path
import sys,json
import bpy
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
from inspect_foot_profile import inspect
source='history/king-mission-006/king-rebuilt.blend'
out=ROOT/'build/king-mission/081-foot-diagnostic'
(out/'profile.json').write_text(json.dumps(inspect(source),indent=2)+'\n',encoding='utf-8')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/source),load_ui=False)
s=bpy.context.scene;gpu(s);s.cycles.samples=128;s.cycles.use_denoising=True;s.render.use_persistent_data=True
foot=bpy.data.objects['Foot left reflection'];foot.data.use_shadow=False
w=s.render.resolution_x;h=s.render.resolution_y
s.render.use_border=True;s.render.use_crop_to_border=False
s.render.border_min_x=200/w;s.render.border_max_x=805/w;s.render.border_min_y=1-1110/h;s.render.border_max_y=1-945/h
s.render.filepath=str(out/'unshadowed-full.png');bpy.ops.render.render(write_still=True)
for o in s.objects:
    if o.type=='LIGHT' and o!=foot:o.data.energy=0
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
s.render.filepath=str(out/'unshadowed-only.png');bpy.ops.render.render(write_still=True)
