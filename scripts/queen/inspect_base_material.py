"""Isolate pigment and relief around the upper-base notch; do not save a model."""
from pathlib import Path
import bpy,numpy as np,sys,json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
p=argparse.ArgumentParser();p.add_argument('--out',default='base-material-012');p.add_argument('--source',default='models/queen/queen-rebuilt.blend');p.add_argument('--crop',nargs=4,type=int,default=[450,740,660,940]);args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);source=ROOT/args.source;digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;mat=editable_mesh(s).data.materials[0];ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=ns.get('Principled BSDF');output=next(n for n in ns if n.type=='OUTPUT_MATERIAL');bump=bs.inputs['Normal'].links[0].from_node;out=ROOT/'build/queen-mission'/args.out;out.mkdir(parents=True,exist_ok=True)
x1,y1,x2,y2=args.crop;W=s.render.resolution_x;H=s.render.resolution_y;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=(x1+.01)/W;s.render.border_max_x=(x2+.01)/W;s.render.border_min_y=(H-y2+.01)/H;s.render.border_max_y=(H-y1+.01)/H;s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA';s.render.use_persistent_data=True;s.cycles.samples=256;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
def render(name):
 path=out/(name+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);im=bpy.data.images.load(str(path),check_existing=False);w,h=im.size;a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);np.save(out/(name+'.npy'),a.reshape(h,w,4)[::-1].copy());s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(out/(name+'.png')),scene=s);s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32'
render('actual-wood')
for sock in ['Normal','Coat Normal']:
 for link in list(bs.inputs[sock].links):ls.remove(link)
render('without-relief')
em=ns.new('ShaderNodeEmission');ls.new(bs.inputs['Base Color'].links[0].from_socket,em.inputs['Color']);ls.new(em.outputs[0],output.inputs['Surface']);render('pigment-only')
ls.new(bump.inputs['Height'].links[0].from_socket,em.inputs['Color']);render('relief-height')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest;(out/'manifest.json').write_text(json.dumps({'source_sha256':digest,'source_unchanged':True,'crop':[x1,y1,x2,y2],'samples':256,'pixel_boundary_epsilon':.01,'note':'Diagnostic BSDF/emission crops only. No public render or model replaced.'},indent=2));print('BASE_MATERIAL_INSPECTION_DONE',flush=True)
