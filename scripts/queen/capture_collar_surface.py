"""Capture actual surface positions and bump normals for collar-light placement."""
from pathlib import Path
import bpy,numpy as np,sys,json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
p=argparse.ArgumentParser();p.add_argument('--source',default='build/queen-mission/148-fuller-middle-lip/queen.blend');p.add_argument('--out',default='collar-surface-148');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/args.source;digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;obj=editable_mesh(s);n=obj.data.materials[0].node_tree.nodes;l=obj.data.materials[0].node_tree.links;bs=n.get('Principled BSDF');normal=bs.inputs['Normal'].links[0].from_socket;output=next(n for n in n if n.type=='OUTPUT_MATERIAL')
geometry=n.new('ShaderNodeNewGeometry');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';offset=n.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=(.5,.5,.5);l.new(scale.outputs['Vector'],offset.inputs[0]);em=n.new('ShaderNodeEmission');l.new(offset.outputs['Vector'],em.inputs['Color']);l.new(em.outputs[0],output.inputs['Surface'])
out=ROOT/'build/queen-mission'/args.out;out.mkdir(exist_ok=True,parents=True)
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=(290+.01)/1254;s.render.border_max_x=(680+.01)/1254;s.render.border_min_y=(1254-565+.01)/1254;s.render.border_max_y=(1254-350+.01)/1254
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA';s.cycles.samples=32;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
for name,socket,factor in [('position',geometry.outputs['Position'],.1),('normal',normal,.5)]:
 l.new(socket,scale.inputs[0]);scale.inputs['Scale'].default_value=factor;s.render.filepath=str(out/(name+'.exr'));bpy.ops.render.render(write_still=True)
 im=bpy.data.images.load(s.render.filepath,check_existing=False);w,h=im.size;assert(w,h)==(390,215);a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);a=a.reshape(h,w,4)[::-1].copy();a[:,:,:3]=(a[:,:,:3]-.5)/factor;np.save(out/(name+'.npy'),a)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source_sha256':digest,'source_unchanged':True,'samples':32,'crop':[290,350,680,565],'kind':'Diagnostic emitted world position and actual bump normal, not a beauty render.'},indent=2)+'\n')
print('COLLAR_SURFACE_CAPTURED',flush=True)
