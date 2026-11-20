"""Bake corrected pigment only; restore the real Principled surface for rendering."""
from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'));from mission_trial import gpu
source=ROOT/'build/rook-mission/046-floor-annulus/rook.blend';out=ROOT/'build/rook-mission/047-floor-atlas';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s);body=next(o for o in s.objects if o.get('rook_editable_control'));mat=body.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Principled BSDF'];output=n['Material Output'];pigment=bs.inputs['Base Color'].links[0].from_socket
for ob in s.objects:ob.select_set(False)
receivers=[o for o in s.objects if o.get('rook_render_receiver')]
for ob in receivers:ob.hide_render=True
body.hide_render=False;body.hide_set(False);body.select_set(True);bpy.context.view_layer.objects.active=body;body.data.uv_layers.active=body.data.uv_layers['Pigment atlas'];body.data.uv_layers['Pigment atlas'].active_render=True
atlas=bpy.data.images.new('Rook pigment atlas v2',width=3072,height=3072,alpha=False);atlas.colorspace_settings.name='sRGB';target=n.new('ShaderNodeTexImage');target.image=atlas;target.name='Baked floor-corrected pigment'
for node in n:node.select=False
target.select=True;n.active=target;emit=n.new('ShaderNodeEmission');l.new(pigment,emit.inputs['Color']);l.new(emit.outputs[0],output.inputs['Surface']);s.cycles.samples=1;s.render.bake.margin=8;bpy.ops.object.bake(type='EMIT',use_clear=True)
atlas.file_format='PNG';atlas.filepath_raw=str(out/'pigment.png');atlas.save();atlas.pack();l.new(bs.outputs[0],output.inputs['Surface']);n.remove(emit)
uv=n.new('ShaderNodeUVMap');uv.uv_map='Pigment atlas';l.new(uv.outputs[0],target.inputs[0]);l.new(target.outputs['Color'],bs.inputs['Base Color']);body.hide_render=True;body.hide_set(True);body.select_set(False)
for ob in receivers:ob.hide_render=False
s['rook_pigment_image']=atlas.name;s['rook_pigment_atlas']='build/rook-mission/047-floor-atlas/pigment.png';s['rook_pigment_atlas_bakes_lighting']=True;s['rook_pigment_note']='Pigment-only rebake excludes current scene lights; source-derived pigment still contains inherited illumination contamination.'
s.cycles.samples=64;s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
(out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest(),'atlas_sha256':hashlib.sha256((out/'pigment.png').read_bytes()).hexdigest(),'atlas_size':[3072,3072],'bake':'EMIT diagnostic of pigment socket only; final material restored to Principled','inherited_illumination_contamination_remains':True},indent=2)+'\n');print('FLOOR_ATLAS_SAVED')
