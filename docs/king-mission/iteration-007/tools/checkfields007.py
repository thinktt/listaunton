from pathlib import Path
import json,sys
import bpy
R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R/'scripts/king'))
from render_regions import controls,assign_material
from mission_trial import gpu
bpy.ops.wm.open_mainfile(filepath=str(R/'build/king-mission/091-resolved-foot-texture/king.blend'),load_ui=False);s=bpy.context.scene;gpu(s)
o=R/'build/king-mission/091-resolved-foot-texture';rows=[]
for ob in controls(s):
    at=ob.data.attributes.get('Foot shoulder detail');mat=ob.data.materials[0]
    rows.append(dict(object=ob.name,material=mat.name,mask_range=[min(x.value for x in at.data),max(x.value for x in at.data)],coat_from=mat.node_tree.nodes['Principled BSDF'].inputs['Coat Normal'].links[0].from_node.name))
(o/'fields.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8');print(json.dumps(rows,indent=2))
body=next(ob for ob in controls(s) if 'body' in ob.name);mat=body.data.materials[0].copy();assign_material(s,body,mat)
e=mat.node_tree.nodes.new('ShaderNodeEmission');mat.node_tree.links.new(mat.node_tree.nodes['Foot detail mask'].outputs['Fac'],e.inputs['Color']);mat.node_tree.links.new(e.outputs[0],mat.node_tree.nodes['Material Output'].inputs['Surface'])
s.cycles.samples=32;s.render.filepath=str(o/'detail-mask.png');bpy.ops.render.render(write_still=True)
