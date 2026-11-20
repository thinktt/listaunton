"""Keep visible floor grain registered after the six-pixel depth change."""
from pathlib import Path
import bpy,sys,json,math,hashlib
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'build/rook-mission/043-floor-reflection/rook.blend';out=ROOT/'build/rook-mission/044-floor-grain-registration';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;body=next(o for o in s.objects if o.get('rook_editable_control'));mat=body.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes['Principled BSDF'];original=bs.inputs['Base Color'].links[0].from_socket;atlas=nodes['Floor transition donor'].image
uv=nodes.new('ShaderNodeUVMap');uv.uv_map='Pigment atlas';sep=nodes.new('ShaderNodeSeparateXYZ');links.new(uv.outputs[0],sep.inputs[0])
def op(kind,*args):
 n=nodes.new('ShaderNodeMath');n.operation=kind
 for i,arg in enumerate(args):
  if isinstance(arg,(int,float)):n.inputs[i].default_value=arg
  else:links.new(arg,n.inputs[i])
 return n.outputs[0]
# Original floor atlas radius/V slope. Shift only pigment coordinates, not mesh UVs.
slope=(.99-.8743657261435638)/.5321428557976784;dy=6/(280*math.sin(math.radians(54)))
theta=op('MULTIPLY',op('SUBTRACT',sep.outputs['X'],.01),math.tau/.74);radius=op('DIVIDE',op('SUBTRACT',.99,sep.outputs['Y']),slope);x=op('MULTIPLY',radius,op('COSINE',theta));y=op('SUBTRACT',op('MULTIPLY',radius,op('SINE',theta)),dy);angle=op('DIVIDE',op('ARCTAN2',y,x),math.tau);fraction=op('SUBTRACT',angle,op('FLOOR',angle));r=op('SQRT',op('ADD',op('MULTIPLY',x,x),op('MULTIPLY',y,y)))
coord=nodes.new('ShaderNodeCombineXYZ');links.new(op('ADD',.01,op('MULTIPLY',fraction,.74)),coord.inputs[0]);links.new(op('SUBTRACT',.99,op('MULTIPLY',r,slope)),coord.inputs[1]);tex=nodes.new('ShaderNodeTexImage');tex.image=atlas;tex.name='Floor registered pigment';links.new(coord.outputs[0],tex.inputs[0]);ramp=nodes.new('ShaderNodeMapRange');ramp.clamp=True;ramp.interpolation_type='SMOOTHERSTEP';ramp.inputs['From Min'].default_value=.874;ramp.inputs['From Max'].default_value=.883;links.new(sep.outputs['Y'],ramp.inputs['Value']);gate=op('MULTIPLY',ramp.outputs['Result'],op('LESS_THAN',sep.outputs['X'],.76));mix=nodes.new('ShaderNodeMixRGB');links.new(gate,mix.inputs[0]);links.new(original,mix.inputs[1]);links.new(tex.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],bs.inputs['Base Color'])
s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
(out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest(),'floor_pigment_y_shift':-dy,'radius_v_slope':slope,'blend_v':[.874,.883],'u_gate':.76,'method':'Polar floor pigment coordinate shift; geometry, mesh UVs, lights and reference camera unchanged from 043.'},indent=2)+'\n')
