"""Isolated local foot finish tests on the measured 082 lighting study."""
from pathlib import Path
import bpy,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'build/rook-mission/082-foot-flanks/rook.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='53e69c58d24339eb28fea503e0140f0420d6a52543494eecbd17972ce84962df'
for number,coat_bump in [(84,False),(85,True)]:
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
 s=bpy.context.scene;m=next(o.data.materials[0] for o in s.objects if o.type=='MESH');ns=m.node_tree.nodes;ls=m.node_tree.links;bs=ns['Principled BSDF']
 def node(kind,label):
  n=ns.new(kind);n.name='Foot finish '+label;return n
 geom=node('ShaderNodeNewGeometry','position');sep=node('ShaderNodeSeparateXYZ','height');ls.new(geom.outputs['Position'],sep.inputs[0])
 masks=[]
 for label,lo,hi,a,b in [('rise',.15,.18,0,1),('fall',.24,.27,1,0)]:
  n=node('ShaderNodeMapRange',label);n.interpolation_type='SMOOTHSTEP';n.clamp=True
  for k,v in [('From Min',lo),('From Max',hi),('To Min',a),('To Max',b)]:n.inputs[k].default_value=v
  ls.new(sep.outputs['Z'],n.inputs['Value']);masks.append(n)
 mask=node('ShaderNodeMath','mask');mask.operation='MULTIPLY';ls.new(masks[0].outputs['Result'],mask.inputs[0]);ls.new(masks[1].outputs['Result'],mask.inputs[1])
 for socket,target in [('Roughness',.12),('Coat Roughness',.06)]:
  base=bs.inputs[socket].default_value;n=node('ShaderNodeMath',socket);n.operation='MULTIPLY_ADD';n.inputs[1].default_value=target-base;n.inputs[2].default_value=base;ls.new(mask.outputs[0],n.inputs[0]);ls.new(n.outputs[0],bs.inputs[socket])
 if coat_bump:
  mix=node('ShaderNodeMix','coat normal');mix.data_type='VECTOR';mix.clamp_factor=True
  ls.new(mask.outputs[0],mix.inputs[0]);ls.new(geom.outputs['Normal'],mix.inputs[4]);ls.new(ns['Bump'].outputs['Normal'],mix.inputs[5]);ls.new(mix.outputs[1],bs.inputs['Coat Normal'])
 out=ROOT/f'build/rook-mission/{number:03d}-foot-finish';out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
 (out/'parameters.json').write_text(json.dumps({'source_sha256':sha(source),'model_sha256':sha(out/'rook.blend'),'roughness':.12,'coat_roughness':.06,'coat_bump':coat_bump,'height_mask':[.15,.18,.24,.27],'geometry_lights_pigment':'unchanged from isolated 082; accepted 078 is not overwritten'},indent=2)+'\n')
