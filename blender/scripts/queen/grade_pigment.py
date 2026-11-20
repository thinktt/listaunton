"""Test regional pigment correction in the material, leaving reference pixels alone."""
from pathlib import Path
import argparse,json,sys
import bpy

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
settings=json.loads(Path(args.config).read_text()) if args.config else {}
source=ROOT/settings.get('source','history/queen-mission-001/queen-rebuilt.blend')
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene;obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
nodes=obj.data.materials[0].node_tree.nodes;links=obj.data.materials[0].node_tree.links;bs=nodes.get('Principled BSDF');old=bs.inputs['Base Color'].links[0].from_socket
geom=nodes.new('ShaderNodeNewGeometry');pos=nodes.new('ShaderNodeSeparateXYZ');links.new(geom.outputs['Position'],pos.inputs[0])
z=nodes.new('ShaderNodeMapRange');z.inputs['From Min'].default_value=0;z.inputs['From Max'].default_value=4.5;links.new(pos.outputs['Z'],z.inputs['Value'])
zones=[(0,(.4,.55,4)),(.26,(.4,.55,4)),(.36,(.45,.55,2)),(.78,(.45,.55,2)),(.9,(.4,.55,3)),(1.18,(.4,.55,3)),(1.34,(.45,.65,4)),(2.55,(.45,.65,4)),(2.78,(.9,1.3,6)),(3.26,(.9,1.3,6)),(3.34,(.35,.55,4)),(3.9,(.35,.55,4)),(4.02,(.85,1.03,4)),(4.5,(.85,1.03,4))]
zones=settings.get('z_zones',zones);finial=settings.get('finial_factor',[.55,.6,3])
ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='LINEAR'
while len(ramp.color_ramp.elements)>1:ramp.color_ramp.elements.remove(ramp.color_ramp.elements[-1])
for i,(height,factor) in enumerate(zones):
    el=ramp.color_ramp.elements[0] if i==0 else ramp.color_ramp.elements.new(height/4.5)
    el.position=height/4.5;el.color=(*[v/8 for v in factor],1)
links.new(z.outputs[0],ramp.inputs[0])
xy=nodes.new('ShaderNodeCombineXYZ');links.new(pos.outputs['X'],xy.inputs['X']);links.new(pos.outputs['Y'],xy.inputs['Y'])
radius=nodes.new('ShaderNodeVectorMath');radius.operation='LENGTH';links.new(xy.outputs[0],radius.inputs[0])
center=nodes.new('ShaderNodeMapRange');center.inputs['From Min'].default_value=.18;center.inputs['From Max'].default_value=.30;center.inputs['To Min'].default_value=1;center.inputs['To Max'].default_value=0;links.new(radius.outputs['Value'],center.inputs['Value'])
high=nodes.new('ShaderNodeMapRange');high.inputs['From Min'].default_value=4.03;high.inputs['From Max'].default_value=4.15;links.new(pos.outputs['Z'],high.inputs['Value'])
mask=nodes.new('ShaderNodeMath');mask.operation='MULTIPLY';links.new(center.outputs[0],mask.inputs[0]);links.new(high.outputs[0],mask.inputs[1])
mix=nodes.new('ShaderNodeMixRGB');links.new(mask.outputs[0],mix.inputs[0]);links.new(ramp.outputs[0],mix.inputs[1]);mix.inputs[2].default_value=(*[v/8 for v in finial],1)
scale=nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=8;links.new(mix.outputs[0],scale.inputs[0])
multiply=nodes.new('ShaderNodeVectorMath');multiply.operation='MULTIPLY';links.new(old,multiply.inputs[0]);links.new(scale.outputs[0],multiply.inputs[1]);links.new(multiply.outputs[0],bs.inputs['Base Color'])
cfg=json.loads(scene['mission_material_config']);cfg['variant']=settings.get('variant','020-regional-color');cfg['pigment_grading']={'z_zones':zones,'finial_factor':finial,'method':'Regional median RGB discrepancies, corrected in linear pigment; artistic inference, not recovered albedo'}
scene['mission_material_config']=json.dumps(cfg,sort_keys=True)
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
scene.render.filepath=str(out/'wood.png');scene.cycles.samples=64;scene.cycles.use_denoising=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
except Exception as exc:print('CPU fallback',exc)
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');print('REGIONAL_GRADE_DONE',flush=True)
