"""Test medium-scale reference grain while retaining broad pigment and real BSDF."""
from pathlib import Path
import sys,json,hashlib,argparse
import bpy,numpy as np,PyOpenColorIO as ocio
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from image_math import blur
p=argparse.ArgumentParser();p.add_argument('--variant',default='112-medium-grain');p.add_argument('--radius',type=int,default=7);p.add_argument('--strength',type=float,default=.9);args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
assert Path(args.variant).name==args.variant and args.variant not in ('.','..')
source=ROOT/'models/queen/queen-rebuilt.blend';digest='1eb382aa47117ded52c6bb32a576fb16c24980d8f68e2f923cf9d0bcc03f19ab';assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;o=editable_mesh(s);mat=o.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF')
projection=n.get('Mix (Legacy).007');grade=n.get('Vector Math.007');tex=n.get('Image Texture.004')
assert projection.inputs[2].links[0].from_node==tex and grade.operation=='MULTIPLY'
im=tex.image;assert im.is_float and im.file_format=='OPEN_EXR';w,h=im.size;old=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(old);old=old.reshape(h,w,4)[::-1].copy()
srgb=np.load(ROOT/'build/queen-mission/grain-band-011/reference-srgb.npy');assert srgb.shape[:2]==old.shape[:2]
ref=srgb.copy();cfg=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'));transform=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX');transform.setDirection(ocio.TRANSFORM_DIR_INVERSE);cfg.getProcessor(transform).getDefaultCPUProcessor().applyRGB(ref)
mask=((old[:,:,:3].max(2)>.001)&(srgb.max(2)>.05)).astype(np.float32)
broad=blur(old[:,:,:3]*mask[:,:,None],r=18,passes=3)/np.maximum(blur(mask,r=18,passes=3)[:,:,None],1e-6)
lum=np.maximum(ref@np.array([.2126,.7152,.0722],dtype=np.float32),0);log=np.log(lum+.003)
local=blur(log*mask,r=args.radius,passes=3)/np.maximum(blur(mask,r=args.radius,passes=3),1e-6)
detail=np.clip(log-local,-.45,.45);confidence=blur(np.clip((.35-srgb.min(2))/.18,0,1),r=2,passes=2)
rgba=np.dstack([np.clip(broad*np.exp(detail*confidence*args.strength)[:,:,None],0,.95),np.ones_like(lum)]).astype(np.float32)
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(exist_ok=True,parents=True)
image=bpy.data.images.new('Queen medium-scale inferred pigment',width=w,height=h,alpha=False,float_buffer=True);image.colorspace_settings.name='Linear Rec.709';image.pixels.foreach_set(rgba[::-1].copy().reshape(-1));image.file_format='OPEN_EXR';image.filepath_raw=str(out/'pigment.exr');image.save();image.pack();tex.image=image
l.new(projection.outputs[0],grade.inputs[0]);l.new(grade.outputs[0],bs.inputs['Base Color'])
output=next(node for node in n if node.type=='OUTPUT_MATERIAL');assert output.inputs['Surface'].links[0].from_node==bs
settings=json.loads(s['mission_material_config']);settings['variant']=args.variant
settings['medium_grain']={'source_sha256':digest,'source_packed_image':im.name,'source_packed_pixel_sha256':hashlib.sha256(old.tobytes()).hexdigest(),'broad_blur_radius':18,'detail_radius':args.radius,'detail_strength':args.strength,'detail_log_bounds':[-.45,.45],'highlight_suppression_min_channel':[.17,.35],'reference_sha256':hashlib.sha256((ROOT/'assets/queen/reference.png').read_bytes()).hexdigest(),'method':'Smooth coarse pigment, inject bounded fine-to-medium reference luminance grain outside highlights. Preserve regional color grade, projection coverage, hidden-surface fallback, relief, geometry and physical lighting. The image is inferred pigment, not a beauty composite.'}
s['mission_material_config']=json.dumps(settings);s['mission_variant']=args.variant;s.cycles.samples=128;s.cycles.use_adaptive_sampling=True;s.cycles.use_denoising=True;s.render.use_persistent_data=True;s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(settings,indent=2));print('MEDIUM_GRAIN_DONE',flush=True)
