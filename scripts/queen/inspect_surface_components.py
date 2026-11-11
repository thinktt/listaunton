"""Native material-component diagnostics; never modify the accepted source."""
from pathlib import Path
import bpy,json,hashlib,sys,numpy as np,argparse
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
p=argparse.ArgumentParser();p.add_argument('--source',default='models/queen/queen-rebuilt.blend');p.add_argument('--out',default='surface-components-016');p.add_argument('--sha256',default='fcb5255f30f89090b5c7fb3b422d15fab2d70c3db4ec478f8bd50e0367c59d94');p.add_argument('--clean-linear',action='store_true');p.add_argument('--modes',nargs='+',default=['pigment-only','reflection-only','relief-height']);args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/args.source;digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==args.sha256
out=ROOT/'build/queen-mission'/args.out;out.mkdir(exist_ok=True,parents=True)
report={'source_sha256':digest,'samples':64,'clean_linear_capture':args.clean_linear,'render_view':'Saved 54-degree camera, AgX, original resolution. Emission views are material diagnostics, not beauty candidates.'}
for mode in args.modes:
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;o=editable_mesh(s);mat=o.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes['Principled BSDF'];surface=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');bump=nodes['Bump.001']
 if mode=='reflection-only':
  for edge in list(bs.inputs['Base Color'].links):links.remove(edge)
  bs.inputs['Base Color'].default_value=(0,0,0,1)
 else:
  emit=nodes.new('ShaderNodeEmission');emit.inputs['Strength'].default_value=1
  links.new(bs.inputs['Base Color'].links[0].from_socket if mode=='pigment-only' else bump.inputs['Height'].links[0].from_socket,emit.inputs['Color']);links.new(emit.outputs[0],surface.inputs['Surface'])
 if mode=='relief-height':
  remap=nodes['Map Range.005'];report['height_remap']={'data_type':remap.data_type,'interpolation_type':remap.interpolation_type,'clamp':remap.clamp,'inputs':[{'index':i,'name':v.name,'identifier':v.identifier,'value':list(v.default_value) if hasattr(v.default_value,'__iter__') else v.default_value} for i,v in enumerate(remap.inputs)]}
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in prefs.devices):s.cycles.device='GPU'
 s.cycles.samples=64;s.cycles.use_denoising=not (args.clean_linear and mode!='reflection-only');s.render.use_persistent_data=False;s.render.filepath=str(out/(mode+'.png'));bpy.ops.render.render(write_still=True)
 s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';bpy.data.images['Render Result'].save_render(filepath=str(out/(mode+'.exr')),scene=s)
 image=bpy.data.images.load(str(out/(mode+'.exr')),check_existing=False);w,h=image.size;pixels=np.empty(w*h*4,dtype=np.float32);image.pixels.foreach_get(pixels);np.save(out/(mode+'.npy'),pixels.reshape(h,w,4)[::-1].copy());bpy.data.images.remove(image)

assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
print('SURFACE_COMPONENTS_DONE',flush=True)
