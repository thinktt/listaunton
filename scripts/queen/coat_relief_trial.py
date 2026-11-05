"""Separate varnish microrelief from the underlying wood relief."""
from pathlib import Path
import bpy,argparse,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
p=argparse.ArgumentParser();p.add_argument('--factor',type=float,required=True);p.add_argument('--wood-factor',type=float,default=1);p.add_argument('--variant',required=True);p.add_argument('--source',default='models/queen/queen-rebuilt.blend');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
assert 0<=a.factor<=1 and 0<=a.wood_factor<=1
source=ROOT/a.source;digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest=='fcb5255f30f89090b5c7fb3b422d15fab2d70c3db4ec478f8bd50e0367c59d94'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;obj=editable_mesh(s);mat=obj.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes['Principled BSDF'];wood=nodes['Bump.001']
assert bs.inputs['Normal'].links[0].from_node==wood and bs.inputs['Coat Normal'].links[0].from_node==wood
assert abs(wood.inputs['Strength'].default_value-.45)<1e-6 and abs(wood.inputs['Distance'].default_value-.007)<1e-6
wood.inputs['Distance'].default_value*=a.wood_factor
coat=nodes.new('ShaderNodeBump');coat.name='Queen varnish microrelief';coat.label='Varnish fills part of the wood grain';coat.invert=wood.invert
for k in ['Strength','Distance','Filter Width']:coat.inputs[k].default_value=wood.inputs[k].default_value
coat.inputs['Distance'].default_value*=a.factor
links.new(wood.inputs['Height'].links[0].from_socket,coat.inputs['Height']);links.new(coat.outputs['Normal'],bs.inputs['Coat Normal'])
cfg=json.loads(s['mission_material_config']);cfg['variant']=a.variant
cfg['coat_relief_refinement']={'source_sha256':digest,'height_factor':a.factor,'wood_height_factor':a.wood_factor,'original_wood_distance':.007,'wood_strength':wood.inputs['Strength'].default_value,'wood_distance':wood.inputs['Distance'].default_value,'coat_strength':coat.inputs['Strength'].default_value,'coat_distance':coat.inputs['Distance'].default_value,'method':'Multiply original wood-bump distance by wood_height_factor; independently scale varnish relief relative to that wood distance. Color atlas, roughness, geometry, UVs, camera and lights unchanged.'}
s['mission_material_config']=json.dumps(cfg);s['mission_variant']=a.variant
out=ROOT/'build/queen-mission'/a.variant;out.mkdir(exist_ok=True,parents=True);s.cycles.samples=64;s.cycles.use_denoising=True;s.render.filepath=str(out/'wood.png');s.render.use_persistent_data=True;bpy.context.preferences.filepaths.save_version=0
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'));bpy.ops.wm.open_mainfile(filepath=str(out/'queen.blend'),load_ui=False);bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print('COAT_RELIEF_TRIAL_DONE',a.variant,flush=True)
