"""Separate the varnish micro-normal from the unchanged wood relief."""
from pathlib import Path
import sys,json,hashlib
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
source=ROOT/'models/queen/queen-rebuilt.blend';digest='1eb382aa47117ded52c6bb32a576fb16c24980d8f68e2f923cf9d0bcc03f19ab';assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;mat=editable_mesh(s).data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links;b=nodes.get('Principled BSDF');wood=b.inputs['Normal'].links[0].from_node;assert wood.type=='BUMP' and b.inputs['Coat Normal'].links[0].from_node==wood
height=wood.inputs['Height'].links[0].from_socket;mix=wood.inputs['Height'].links[0].from_node;pores=mix.inputs[2].links[0].from_socket
coat=nodes.new('ShaderNodeBump');coat.label='Independent polished varnish relief';links.new(coat.outputs['Normal'],b.inputs['Coat Normal'])
original=json.loads(s['mission_material_config']);s.cycles.samples=128;s.cycles.use_denoising=True;s.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.context.preferences.filepaths.save_version=0
for variant,src,strength,distance in [('114-thin-coat-relief',height,.06,.004),('115-fine-coat-pores',pores,.1,.001)]:
 links.new(src,coat.inputs['Height']);coat.inputs['Strength'].default_value=strength;coat.inputs['Distance'].default_value=distance
 cfg=json.loads(json.dumps(original));cfg['variant']=variant;cfg['independent_coat_relief']={'source_sha256':digest,'wood_relief_unchanged':True,'coat_height_source':src.node.name,'strength':strength,'distance':distance,'hypothesis':'A polished clear coat can smooth underlying wood relief without removing pigment detail or the wood micro-normal.'};s['mission_material_config']=json.dumps(cfg);s['mission_variant']=variant
 out=ROOT/'build/queen-mission'/variant;out.mkdir(exist_ok=True,parents=True);s.render.filepath=str(out/'wood.png');bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'));bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2));print('COAT_TRIAL_DONE',variant,flush=True)
