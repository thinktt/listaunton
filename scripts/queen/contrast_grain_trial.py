"""Compare stronger reference grain with a restrained, matching relief field.

Run in Blender. Both outputs remain actual BSDF renders of the accepted mesh.
The fixed-camera grain is inferred material data, not a beauty-image overlay.
"""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser();p.add_argument('--radius',type=int,default=9);p.add_argument('--exponent',type=float,default=1.6);p.add_argument('--grain-variant',default='049-contrast-grain');p.add_argument('--relief-variant',default='050-restrained-relief');p.add_argument('--relief-distance',type=float,default=.004);p.add_argument('--relief-blend',type=float,default=.8);p.add_argument('--no-relief',action='store_true')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/'build/queen-mission/048-medium-grain/queen.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;o=next(x for x in s.objects if x.type=='MESH' and not x.hide_render)
n=o.data.materials[0].node_tree.nodes;l=o.data.materials[0].node_tree.links;b=n.get('Principled BSDF')
response=ROOT/'build/queen-mission/pigment-fit-039'
old=np.load(response/'pigment.npy');ref=np.load(response/'reference-linear.npy');srgb=np.load(response/'reference-srgb.npy')
mask=(old[:,:,3]>.995).astype(np.float32)
broad=blur(old[:,:,:3]*mask[:,:,None],r=7,passes=3)/np.maximum(blur(mask,r=7,passes=3)[:,:,None],1e-6)
lum=np.maximum(ref@np.array([.2126,.7152,.0722],dtype=np.float32),0)
log=np.log(lum+.003);rm=(ref.max(2)>.001).astype(np.float32)
local=blur(log*rm,r=args.radius,passes=3)/np.maximum(blur(rm,r=args.radius,passes=3),1e-6)
detail=np.clip(log-local,-.55,.55)
# Warm diffuse wood was incorrectly classified as highlight by the preceding
# two-chromaticity hypothesis. Suppress only bright, relatively neutral areas.
weight=blur(np.clip((.68-srgb.min(2))/.4,0,1),r=3,passes=2)
ratio=np.exp(detail*weight*args.exponent)
rgba=np.load(ROOT/'build/queen-mission/medium-grain-039/inferred-pigment.npy');confidence=rgba[:,:,3].copy()
rgba[:,:,:3]=np.clip(broad*ratio[:,:,None],0,.95)
tex=next(x for x in n if x.type=='TEX_IMAGE' and x.image and x.image.name.startswith('Queen inferred diffuse pigment'))
# Do not edit a reopened EXR's sRGB-tagged pixel buffer and pack it again:
# Blender then converts those new linear values as if they were sRGB. A fresh
# explicitly linear float image + explicit EXR save preserves the values.
destination=ROOT/'build/queen-mission'/args.grain_variant;destination.mkdir(parents=True,exist_ok=True)
rgba[:,:,3]=1
im=bpy.data.images.new('Queen linear inferred pigment',width=rgba.shape[1],height=rgba.shape[0],alpha=False,float_buffer=True)
im.colorspace_settings.name='Linear Rec.709';im.alpha_mode='STRAIGHT';im.pixels.foreach_set(rgba[::-1].copy().reshape(-1))
im.filepath_raw=str(destination/'pigment.exr');im.file_format='OPEN_EXR';im.save();im.pack();tex.image=im
np.save(destination/'expected-pigment.npy',rgba)
coverage_rgba=np.dstack([confidence,confidence,confidence,np.ones_like(confidence)]).astype(np.float32)
coverage_image=bpy.data.images.new('Queen pigment confidence',width=rgba.shape[1],height=rgba.shape[0],alpha=False,float_buffer=True)
coverage_image.colorspace_settings.name='Non-Color';coverage_image.pixels.foreach_set(coverage_rgba[::-1].copy().reshape(-1));coverage_image.filepath_raw=str(destination/'confidence.exr');coverage_image.file_format='OPEN_EXR';coverage_image.save();coverage_image.pack()
coverage_tex=n.new('ShaderNodeTexImage');coverage_tex.image=coverage_image;coverage_tex.extension='EXTEND';l.new(tex.inputs['Vector'].links[0].from_socket,coverage_tex.inputs['Vector'])
for link in list(tex.outputs['Alpha'].links):l.new(coverage_tex.outputs['Color'],link.to_socket)
cfg=json.loads(s['mission_material_config'])
cfg['grain_contrast_trial']={'source':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'pigment_blur_radius':7,'reference_blur_radius':args.radius,'detail_log_bounds':[-.55,.55],'detail_exponent':args.exponent,'bright_neutral_suppression_min_srgb':[.28,.68],'reference_sha256':hashlib.sha256((ROOT/'assets/queen/reference.png').read_bytes()).hexdigest(),'caveat':'Reference grain is inferred with bounded local shading contamination. Hidden surfaces retain continuous prior wood; source images are unchanged.'}
s.render.use_persistent_data=True;s.cycles.samples=64;s.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.context.preferences.filepaths.save_version=0
def save_render(variant):
 out=ROOT/'build/queen-mission'/variant;out.mkdir(parents=True,exist_ok=True)
 cfg['variant']=variant;s['mission_material_config']=json.dumps(cfg,sort_keys=True)
 s.render.filepath=str(out/'wood.png');bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
 bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
 print('GRAIN_VARIANT_DONE',variant,flush=True)
save_render(args.grain_variant)
if args.no_relief:raise SystemExit(0)
oldnormal=b.inputs['Normal'].links[0].from_socket
height=np.clip(.5+detail*.15,.35,.65)
rh=np.dstack([height,height,height,np.ones_like(height)]).astype(np.float32)
hi=bpy.data.images.new('Queen restrained reference relief',width=height.shape[1],height=height.shape[0],alpha=True,float_buffer=True)
hi.colorspace_settings.name='Non-Color';hi.pixels.foreach_set(rh[::-1].copy().reshape(-1));hi.pack()
ht=n.new('ShaderNodeTexImage');ht.image=hi;ht.extension='EXTEND'
uv=n.new('ShaderNodeUVMap');uv.uv_map='Inferred pigment projection';l.new(uv.outputs[0],ht.inputs['Vector'])
bu=n.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.3;bu.inputs['Distance'].default_value=args.relief_distance;l.new(ht.outputs['Color'],bu.inputs['Height'])
att=n.new('ShaderNodeAttribute');att.attribute_name='Inferred pigment coverage'
fac=n.new('ShaderNodeMath');fac.operation='MULTIPLY';fac.inputs[1].default_value=args.relief_blend;l.new(att.outputs['Fac'],fac.inputs[0])
mix=n.new('ShaderNodeMixRGB');l.new(fac.outputs[0],mix.inputs[0]);l.new(oldnormal,mix.inputs[1]);l.new(bu.outputs['Normal'],mix.inputs[2]);l.new(mix.outputs[0],b.inputs['Normal']);l.new(mix.outputs[0],b.inputs['Coat Normal'])
cfg['restrained_reference_relief']={'strength':.3,'distance':args.relief_distance,'height_detail_gain':.15,'visible_blend':args.relief_blend,'hidden_prior_relief':True}
save_render(args.relief_variant)
