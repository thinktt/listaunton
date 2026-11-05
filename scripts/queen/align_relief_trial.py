"""Test relief aligned to the accepted pigment instead of the early source atlas."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
p=argparse.ArgumentParser();p.add_argument('--variant',default='120-aligned-relief');p.add_argument('--source',default='models/queen/queen-rebuilt.blend');p.add_argument('--strength',type=float);p.add_argument('--distance',type=float);p.add_argument('--pore-scale',type=float);args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/args.source;digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest=='2cb513a71cf36e6bbaa3619b95cc53208e1245f9dbefebc745470e582fc11a9b'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;mat=editable_mesh(s).data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF');pigment=bs.inputs['Base Color'].links[0].from_socket;assert pigment.node.type=='TEX_IMAGE'
height=n['RGB to BW.002'];previous=height.inputs['Color'].links[0].from_node.image.name;l.new(pigment,height.inputs['Color']);bump=bs.inputs['Normal'].links[0].from_node;assert bump.type=='BUMP'
if args.strength is not None:bump.inputs['Strength'].default_value=args.strength
if args.distance is not None:bump.inputs['Distance'].default_value=args.distance
if args.pore_scale is not None:n['Noise Texture.003'].inputs['Scale'].default_value=args.pore_scale
cfg=json.loads(s['mission_material_config']);cfg['variant']=args.variant;cfg['aligned_relief']={'source_sha256':digest,'previous_height_image':previous,'new_height_image':pigment.node.image.name,'texture':cfg['texture'],'bump_strength':bump.inputs['Strength'].default_value,'bump_distance':bump.inputs['Distance'].default_value,'pore_scale':n['Noise Texture.003'].inputs['Scale'].default_value,'hypothesis':'The early color atlas no longer matches accepted pigment detail. Align material relief with the current pigment while preserving the actual BSDF, geometry and light rig.'};s['mission_material_config']=json.dumps(cfg);s['mission_variant']=args.variant
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(parents=True,exist_ok=True);s.cycles.samples=128;s.cycles.use_denoising=True;s.render.use_persistent_data=True;s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2));print('ALIGNED_RELIEF_DONE',flush=True)
