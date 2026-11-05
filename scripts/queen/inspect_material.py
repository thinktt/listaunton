from pathlib import Path
import bpy,json
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'history/queen-mission-001/queen-rebuilt.blend'),load_ui=False)
s=bpy.context.scene;o=next(o for o in s.objects if o.type=='MESH' and not o.hide_render)
d={'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'res':[s.render.resolution_x,s.render.resolution_y],'world':s.world.node_tree.nodes['Background'].inputs['Strength'].default_value,'lights':[]}
for x in s.objects:
 if x.type=='LIGHT':d['lights'].append({'name':x.name,'energy':x.data.energy,'size':x.data.size,'pos':list(x.location)})
bs=o.data.materials[0].node_tree.nodes.get('Principled BSDF')
d['socket_names']=[i.name for i in bs.inputs]
d['bsdf']={n:bs.inputs[n].default_value for n in ['Roughness','Coat Weight','Coat Roughness','Specular IOR Level','IOR','Metallic']}
d['object_matrix']=[list(row) for row in o.matrix_world];d['camera_matrix']=[list(row) for row in s.camera.matrix_world]
print(json.dumps(d,indent=2));(ROOT/'build/queen-mission/material-inspection.json').write_text(json.dumps(d,indent=2))
