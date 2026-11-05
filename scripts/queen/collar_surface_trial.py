"""Test a locally broader varnish lobe while preserving pigment, shape and lights."""
from pathlib import Path
import bpy,sys,json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
p=argparse.ArgumentParser();p.add_argument('--source',default='models/queen/queen-rebuilt.blend');p.add_argument('--variant',default='147-collar-varnish');p.add_argument('--coat',type=float,default=.12);args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/args.source;digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest=='8b1c052b8c6960c6faf6760635090a7c081b04e5ad779641a4b9e49433f628c0'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;obj=editable_mesh(s);mat=obj.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF')
assert not bs.inputs['Coat Roughness'].is_linked;old=bs.inputs['Coat Roughness'].default_value
coord=n.new('ShaderNodeTexCoord');coord.label='Object-local collar finish coordinates'
xyz=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Object'],xyz.inputs[0])
def ramp(label,lo,hi,a,b):
 node=n.new('ShaderNodeMapRange');node.label=label;node.clamp=True;node.interpolation_type='SMOOTHERSTEP'
 for name,value in [('From Min',lo),('From Max',hi),('To Min',a),('To Max',b)]:node.inputs[name].default_value=value
 l.new(xyz.outputs['Z'],node.inputs['Value']);return node.outputs['Result']
lower=ramp('Smooth lower collar finish transition',2.75,2.81,0,1);upper=ramp('Smooth upper collar finish transition',3.31,3.37,1,0)
mask=n.new('ShaderNodeMath');mask.operation='MULTIPLY';mask.label='Collar finish weight';l.new(lower,mask.inputs[0]);l.new(upper,mask.inputs[1])
value=n.new('ShaderNodeMath');value.operation='MULTIPLY_ADD';value.label='Collar varnish roughness';value.inputs[1].default_value=args.coat-old;value.inputs[2].default_value=old;l.new(mask.outputs[0],value.inputs[0]);l.new(value.outputs[0],bs.inputs['Coat Roughness'])
cfg=json.loads(s['mission_material_config']);cfg['variant']=args.variant;cfg['collar_surface_finish']={'source_sha256':digest,'old_coat_roughness':old,'collar_coat_roughness':args.coat,'object_z_transitions':[[2.75,2.81],[3.31,3.37]],'method':'Object-local smooth collar mask broadens only the clear-coat microfacet lobe. Pigment, relief, base-layer roughness, geometry, camera and lights are unchanged.'}
s['mission_material_config']=json.dumps(cfg);s['mission_variant']=args.variant;s.cycles.samples=64;s.cycles.use_denoising=True;s.render.use_persistent_data=True
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(exist_ok=True,parents=True);s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True);assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');print('COLLAR_SURFACE_TRIAL_DONE',flush=True)
