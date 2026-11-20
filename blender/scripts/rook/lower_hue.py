"""Local hue-floor studies preserve grain coordinates and maximum RGB value."""
from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'models/rook/rook-rebuilt.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)=='77221a063a8dbdd5f01545312c98e5bf31d4f86f3d6cbe0ea169ff198060a33e'
for num,hue in [(48,.018),(49,.026),(50,.034)]:
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;body=next(o for o in s.objects if o.get('rook_editable_control'));mat=body.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Principled BSDF'];original=bs.inputs['Base Color'].links[0].from_socket
 rows={}
 for loop,uvrow in zip(body.data.loops,body.data.uv_layers['Pigment atlas'].data):rows.setdefault(loop.vertex_index//128,[]).append(uvrow.uv.y)
 low=float(np.mean(rows[15]));high=float(np.mean(rows[32]));uv=n.new('ShaderNodeUVMap');uv.uv_map='Pigment atlas';sep=n.new('ShaderNodeSeparateXYZ');l.new(uv.outputs[0],sep.inputs[0])
 def op(kind,*args):
  node=n.new('ShaderNodeMath');node.operation=kind
  for i,arg in enumerate(args):
   if isinstance(arg,(int,float)):node.inputs[i].default_value=arg
   else:l.new(arg,node.inputs[i])
  return node.outputs[0]
 t=op('DIVIDE',op('SUBTRACT',sep.outputs['Y'],low),high-low);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='EASE';ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1]);ramp.color_ramp.elements[0].position=0;ramp.color_ramp.elements[0].color=(0,0,0,1)
 for pos,c in [(.15,1),(.85,1),(1,0)]:e=ramp.color_ramp.elements.new(pos);e.color=(c,c,c,1)
 l.new(t,ramp.inputs[0]);gate=op('MULTIPLY',ramp.outputs['Color'],op('LESS_THAN',sep.outputs['X'],.76))
 hsv=n.new('ShaderNodeSeparateColor');hsv.mode='HSV';l.new(original,hsv.inputs[0]);combine=n.new('ShaderNodeCombineColor');combine.mode='HSV';l.new(op('MAXIMUM',hsv.outputs[0],hue),combine.inputs[0]);l.new(hsv.outputs[1],combine.inputs[1]);l.new(hsv.outputs[2],combine.inputs[2]);mix=n.new('ShaderNodeMixRGB');mix.name='Lower body hue repair';l.new(gate,mix.inputs[0]);l.new(original,mix.inputs[1]);l.new(combine.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
 out=ROOT/f'build/rook-mission/{num:03d}-lower-hue';out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
 (out/'parameters.json').write_text(json.dumps({'source_sha256':sha(source),'model_sha256':sha(out/'rook.blend'),'hue_floor_linear_rgb_hsv':hue,'destination_v':[low,high],'control_rows':[15,32],'method':'Smooth local hue floor only; saturation/value, grain sample coordinates, geometry, UVs and lighting unchanged.'},indent=2)+'\n');print('HUE_TRIAL_SAVED',num,flush=True)
