"""Read-only diagnostic renders to estimate diffuse pigment response.

Black/white BSDF inputs bracket the material's response under the chosen rig.
An emission pass records current pigment only. None is a public beauty render.
"""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
import numpy as np
import PyOpenColorIO as ocio
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);p.add_argument('--samples',type=int,default=64);args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT/args.source;before=hashlib.sha256(source.read_bytes()).hexdigest();out=ROOT/args.out;out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);scene=bpy.context.scene;obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
cfg=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
view=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display=scene.display_settings.display_device,view=scene.view_settings.view_transform);view.setDirection(ocio.TRANSFORM_DIR_INVERSE)
target=np.load(out/'reference-srgb.npy');cfg.getProcessor(view).getDefaultCPUProcessor().applyRGB(target);np.save(out/'reference-linear.npy',target)
mat=obj.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF');output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
pigment=bs.inputs['Base Color'].links[0].from_socket
for link in list(bs.inputs['Base Color'].links):links.remove(link)
scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_depth='32';scene.render.image_settings.color_mode='RGBA'
scene.render.resolution_percentage=100;scene.render.use_persistent_data=True;scene.cycles.samples=args.samples;scene.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
def render(name):
 path=out/(name+'.exr');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 im=bpy.data.images.load(str(path),check_existing=False);w,h=im.size;values=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(values);values=values.reshape(h,w,4)[::-1].copy();bpy.data.images.remove(im);np.save(out/(name+'.npy'),values);print('RESPONSE_PASS_DONE',name,flush=True)
bs.inputs['Base Color'].default_value=(0,0,0,1);render('black-bsdf')
bs.inputs['Base Color'].default_value=(1,1,1,1);render('white-bsdf')
emission=nodes.new('ShaderNodeEmission');links.new(pigment,emission.inputs['Color']);links.new(emission.outputs[0],output.inputs['Surface']);render('pigment')
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
(out/'manifest.json').write_text(json.dumps({'source':args.source,'source_sha256':before,'resolution':[scene.render.resolution_x,scene.render.resolution_y],'samples':args.samples,'source_unchanged':True,'caveat':'White and black shader response is an approximation when multiple diffuse bounces are present; derived pigment is inferred, not recovered ground truth.'},indent=2)+'\n')
