"""Diagnostic color and projection-coverage passes; never deliver as beauty."""
from pathlib import Path
import hashlib,json,sys
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
source=ROOT/'history/queen-mission-008/queen-rebuilt.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='c32bccbf33e5e137d982bdeafd881a783b006f62e644dbd5db2df57d02801004'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;o=editable_mesh(s);n=o.data.materials[0].node_tree.nodes;l=o.data.materials[0].node_tree.links
bs=n.get('Principled BSDF');color=bs.inputs['Base Color'].links[0].from_socket
output=next(node for node in n if node.type=='OUTPUT_MATERIAL');emission=n.new('ShaderNodeEmission');l.new(emission.outputs[0],output.inputs['Surface'])
out=ROOT/'build/queen-mission/pigment-diagnostic-008';out.mkdir(parents=True,exist_ok=True)
s.cycles.samples=16;s.cycles.use_denoising=False;s.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):s.cycles.device='GPU'
attribute=n.new('ShaderNodeAttribute');attribute.attribute_name='Inferred pigment coverage'
for name,socket in [('pigment',color),('coverage',attribute.outputs['Fac'])]:
 l.new(socket,emission.inputs['Color']);s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.filepath=str(out/(name+'.exr'))
 bpy.ops.render.render(write_still=True)
im_records=[]
for node in n:
 if node.type=='TEX_IMAGE' and node.image:im_records.append({'node':node.name,'image':node.image.name,'size':list(node.image.size),'colorspace':node.image.colorspace_settings.name,'filepath':node.image.filepath})
(out/'manifest.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'diagnostic_only':True,'images':im_records},indent=2)+'\n')
for name in ['pigment','coverage']:
 im=bpy.data.images.load(str(out/(name+'.exr')),check_existing=False)
 a=np.empty(im.size[0]*im.size[1]*4,dtype=np.float32);im.pixels.foreach_get(a);a=a.reshape(im.size[1],im.size[0],4)[::-1].copy();np.save(out/(name+'.npy'),a)
print('CURRENT_PIGMENT_DIAGNOSTICS_DONE',flush=True)
