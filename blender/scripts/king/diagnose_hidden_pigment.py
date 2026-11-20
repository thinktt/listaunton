from pathlib import Path
import sys,json
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts/king'))
from mission_trial import gpu
from render_regions import controls
for rel,label in [('history/king-mission-005/king-rebuilt.blend','accepted005'),('build/king-mission/077-hidden-coverage-completion/king.blend','trial077')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/rel),load_ui=False);s=bpy.context.scene;gpu(s)
 body=next(o for o in controls(s) if 'body' in o.name);n=body.data.materials[0].node_tree.nodes;l=body.data.materials[0].node_tree.links;bs=n['Principled BSDF'];out=next(x for x in n if x.type=='OUTPUT_MATERIAL')
 em=n.new('ShaderNodeEmission');l.new(bs.inputs['Base Color'].links[0].from_socket,em.inputs['Color']);l.new(em.outputs[0],out.inputs['Surface'])
 cam=s.camera;cam.data.shift_x=cam.data.shift_y=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=6
 s.render.resolution_x=600;s.render.resolution_y=900;s.cycles.samples=16
 for name,pos in [('side',(16,0,2.65)),('rear',(0,16,2.65))]:
  cam.location=pos;cam.rotation_euler=(Vector((0,0,2.65))-cam.location).to_track_quat('-Z','Y').to_euler()
  s.render.filepath=str(R/'build/king-mission/077-hidden-coverage-completion'/f'{label}-pigment-{name}.png');bpy.ops.render.render(write_still=True)
print('HIDDEN_EMISSION_DIAGNOSTIC_DONE')
