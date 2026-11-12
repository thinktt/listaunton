from pathlib import Path
import sys,json
import bpy
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'build/king-mission/083-broad-foot-reflector/king.blend'),load_ui=False)
s=bpy.context.scene;gpu(s);s.cycles.samples=128;s.cycles.use_denoising=True;s.render.use_persistent_data=True
out=ROOT/'build/king-mission/084-foot-normal-diagnostic';out.mkdir(parents=True,exist_ok=True)
foot=next(o for o in s.objects if o.get('king_render_region')=='foot');mat=foot.data.materials[0].copy();foot.data.materials[0]=mat
bs=mat.node_tree.nodes['Principled BSDF'];links=mat.node_tree.links
(out/'graph.json').write_text(json.dumps(dict(links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in links]),indent=2)+'\n',encoding='utf-8')
w=s.render.resolution_x;h=s.render.resolution_y
s.render.use_border=True;s.render.use_crop_to_border=False
s.render.border_min_x=200/w;s.render.border_max_x=805/w;s.render.border_min_y=1-1110/h;s.render.border_max_y=1-945/h
for i in list(bs.inputs['Coat Normal'].links):links.remove(i)
s.render.filepath=str(out/'coat-geometric.png');bpy.ops.render.render(write_still=True)
for i in list(bs.inputs['Normal'].links):links.remove(i)
s.render.filepath=str(out/'all-geometric.png');bpy.ops.render.render(write_still=True)
bs.inputs['Coat Roughness'].default_value=.4
s.render.filepath=str(out/'rough-coat.png');bpy.ops.render.render(write_still=True)
print('NORMAL_DIAGNOSTICS_DONE')
