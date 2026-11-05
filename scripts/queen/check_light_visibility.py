"""Measure which light controls actually affect Cycles reflections."""
from pathlib import Path
import json
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'build/queen-mission/039-rolled-collar-refit/queen.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
lights=[o for o in s.objects if o.type=='LIGHT'];light=next(o for o in lights if o.name=='Right key')
for other in lights:
 if other!=light:bpy.data.objects.remove(other,do_unlink=True)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
obj=next(o for o in s.objects if o.type=='MESH' and not o.hide_render);bs=obj.data.materials[0].node_tree.nodes.get('Principled BSDF');links=obj.data.materials[0].node_tree.links
for link in list(bs.inputs['Base Color'].links):links.remove(link)
bs.inputs['Base Color'].default_value=(0,0,0,1)
print('SPECULAR_FACTOR_DESCRIPTION',light.data.bl_rna.properties['specular_factor'].description,flush=True)
s.render.resolution_x=s.render.resolution_y=418;s.render.resolution_percentage=100;s.render.use_persistent_data=True;s.cycles.samples=32;s.cycles.use_denoising=False
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA'
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
out=ROOT/'build/queen-mission/light-visibility';out.mkdir(parents=True,exist_ok=True);report={}
for name,factor,visible,diffuse in [('baseline',1,True,True),('data-factor-zero',0,True,True),('object-glossy-off',1,False,True),('object-diffuse-off',1,True,False)]:
 light.data.specular_factor=factor;light.visible_glossy=visible;light.visible_diffuse=diffuse;path=out/(name+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 im=bpy.data.images.load(str(path),check_existing=False);a=np.empty(418*418*4,dtype=np.float32);im.pixels.foreach_get(a);a=a.reshape(418,418,4);bpy.data.images.remove(im)
 report[name]={'mean_rgb':float(a[:,:,:3].mean()),'sum_rgb':float(a[:,:,:3].sum()),'maximum':float(a[:,:,:3].max())};print(name,report[name],flush=True)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
