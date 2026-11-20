"""Repair only the contaminated floor-transition pigment with adjacent inner-wall wood."""
from pathlib import Path
import bpy,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'));from mission_trial import gpu
source=ROOT/'history/rook-mission-037/models/rook/rook-rebuilt.blend';assert hashlib.sha256(source.read_bytes()).hexdigest()=='a667b97122b3c188d93040279660ef947d91ba12b442442a71b4ba97a133e484'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s);body=next(o for o in s.objects if o.get('rook_editable_control'));mat=body.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes['Principled BSDF'];original=bs.inputs['Base Color'].links[0].from_socket;atlas=original.node.image
uv=nodes.new('ShaderNodeUVMap');uv.uv_map='Pigment atlas';sep=nodes.new('ShaderNodeSeparateXYZ');links.new(uv.outputs[0],sep.inputs[0])
def op(kind,*args):
 n=nodes.new('ShaderNodeMath');n.operation=kind
 for i,arg in enumerate(args):
  if isinstance(arg,(int,float)):n.inputs[i].default_value=arg
  else:links.new(arg,n.inputs[i])
 return n.outputs[0]
t=op('DIVIDE',op('SUBTRACT',sep.outputs['Y'],.863),.016);sample=nodes.new('ShaderNodeCombineXYZ');links.new(sep.outputs['X'],sample.inputs[0]);links.new(op('ADD',.851,op('MULTIPLY',t,.012)),sample.inputs[1]);tex=nodes.new('ShaderNodeTexImage');tex.image=atlas;tex.name='Floor transition donor';links.new(sample.outputs[0],tex.inputs[0]);ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='EASE';ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1]);ramp.color_ramp.elements[0].position=0;ramp.color_ramp.elements[0].color=(0,0,0,1)
for pos,color in [(.2,1),(.8,1),(1,0)]:e=ramp.color_ramp.elements.new(pos);e.color=(color,color,color,1)
links.new(t,ramp.inputs[0]);gate=op('MULTIPLY',ramp.outputs['Color'],op('LESS_THAN',sep.outputs['X'],.76));mix=nodes.new('ShaderNodeMixRGB');mix.name='Floor transition repair';links.new(gate,mix.inputs[0]);links.new(original,mix.inputs[1]);links.new(tex.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],bs.inputs['Base Color'])
out=ROOT/'build/rook-mission/041-floor-pigment';out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
(out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest(),'destination_v':[.863,.879],'donor_v':[.851,.863],'u_gate':.76,'method':'Smoothly blended UV-space adjacent inner-wall sampling; geometry/UVs/lights unchanged.'},indent=2)+'\n')
print('FLOOR_PIGMENT_SAVED')
