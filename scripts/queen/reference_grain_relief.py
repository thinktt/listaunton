"""Test fine reference-derived relief on the accepted real BSDF material."""
from pathlib import Path
import hashlib,json,sys
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
source=ROOT/'build/queen-mission/036-reference-grain/queen.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;o=next(o for o in s.objects if o.type=='MESH' and not o.hide_render)
n=o.data.materials[0].node_tree.nodes;l=o.data.materials[0].node_tree.links;b=n.get('Principled BSDF')
# Restore the accepted color; this trial changes relief alone.
color_mix=b.inputs['Base Color'].links[0].from_node
assert color_mix.type=='MIX_RGB'
l.new(color_mix.inputs[1].links[0].from_socket,b.inputs['Base Color'])
oldnormal=b.inputs['Normal'].links[0].from_socket
reference=np.load(ROOT/'build/queen-mission/pigment-fit-033/reference-linear.npy')
pigment=np.load(ROOT/'build/queen-mission/pigment-fit-033/pigment.npy')
lum=np.maximum(reference@np.array([.2126,.7152,.0722],dtype=np.float32),0)
height=np.clip(.5+.25*np.log((lum+.004)/(blur(lum)+.004)),.05,.95)
rgba=np.dstack([height,height,height,np.clip(pigment[:,:,3],0,1)]).astype(np.float32)
im=bpy.data.images.new('Queen fine reference relief',width=height.shape[1],height=height.shape[0],alpha=True,float_buffer=True)
im.colorspace_settings.name='Non-Color';im.alpha_mode='STRAIGHT';im.pixels.foreach_set(rgba[::-1].copy().reshape(-1))
out=ROOT/'build/queen-mission/038-reference-relief';out.mkdir(parents=True,exist_ok=True)
im.filepath_raw=str(out/'fine-relief.exr');im.file_format='OPEN_EXR';im.save();im.pack()
tex=n.new('ShaderNodeTexImage');tex.image=im;tex.extension='EXTEND'
uv=n.new('ShaderNodeUVMap');uv.uv_map='Inferred pigment projection';l.new(uv.outputs[0],tex.inputs['Vector'])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.3;bump.inputs['Distance'].default_value=.01;l.new(tex.outputs['Color'],bump.inputs['Height'])
coverage=n.new('ShaderNodeAttribute');coverage.attribute_name='Inferred pigment coverage'
weight=n.new('ShaderNodeMath');weight.operation='MULTIPLY';weight.inputs[1].default_value=.95;l.new(coverage.outputs['Fac'],weight.inputs[0])
mix=n.new('ShaderNodeMixRGB');l.new(weight.outputs[0],mix.inputs[0]);l.new(oldnormal,mix.inputs[1]);l.new(bump.outputs['Normal'],mix.inputs[2]);l.new(mix.outputs[0],b.inputs['Normal']);l.new(mix.outputs[0],b.inputs['Coat Normal'])
cfg=json.loads(s['mission_material_config']);cfg.pop('inferred_pigment',None)
cfg['variant']='038-reference-relief';cfg['reference_relief']={'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'base_color_restored_to_026':True,'strength':.3,'distance':.01,'visible_blend':.95,'method':'Log-luminance high pass with approximately 3.46px blur; local relief only, not diffuse shading','caveat':'Fine source shading can affect inferred relief; hidden surfaces retain prior continuous relief.'};s['mission_material_config']=json.dumps(cfg,sort_keys=True)
s.cycles.samples=96;s.cycles.use_denoising=True;s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');print('REFERENCE_RELIEF_DONE',flush=True)
