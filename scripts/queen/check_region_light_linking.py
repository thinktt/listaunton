"""Measure whether one linked reflector illuminates only its intended region."""
from pathlib import Path
import json, sys
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from render_regions import link, REGION_NAMES
source=ROOT/'build/queen-mission/082-render-regions-equivalence/queen.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene
parts={o['mission_render_region']:o for o in scene.objects if o.get('mission_render_region')}
bsdf=parts['finial'].data.materials[0].node_tree.nodes.get('Principled BSDF')
print('BSDF_INPUTS',[(i.name,list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value,i.is_linked) for i in bsdf.inputs if hasattr(i,'default_value')],flush=True)
links=parts['finial'].data.materials[0].node_tree.links
for wire in list(bsdf.inputs['Base Color'].links):links.remove(wire)
bsdf.inputs['Base Color'].default_value=(0,0,0,1)
for light in list(scene.objects):
    if light.type=='LIGHT':bpy.data.objects.remove(light,do_unlink=True)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
data=bpy.data.lights.new('Link probe','SUN');data.energy=4;data.angle=.10
light=bpy.data.objects.new('Link probe',data);scene.collection.objects.link(light)
light.location=(2,-4,6);light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
light.visible_diffuse=False;light.visible_glossy=True
scene.render.resolution_x=scene.render.resolution_y=418
scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_depth='32'
scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):scene.cycles.device='GPU'
out=ROOT/'build/queen-mission/linked-light-diagnostics';out.mkdir(parents=True,exist_ok=True)
ids=np.load(ROOT/'build/queen-mission/082-render-regions-equivalence/region-ids.npy')
labels=np.rint(ids[:,:,0]*16).astype(int)-1
report={}
for name in ['global','finial-only']:
    if name=='finial-only':
        receiver=link(light,[parts['finial']],'diagnostic-finial')
        print('RECEIVER_STATES',[(o.name,r.light_linking.link_state) for o,r in zip(receiver.objects,receiver.collection_objects)],flush=True)
    scene.render.filepath=str(out/(name+'.exr'));bpy.ops.render.render(write_still=True)
    image=bpy.data.images.load(scene.render.filepath,check_existing=False)
    pixels=np.empty(418*418*4,dtype=np.float32);image.pixels.foreach_get(pixels)
    pixels=pixels.reshape(418,418,4)[::-1].copy();np.save(out/(name+'.npy'),pixels)
    report[name]={region:float(pixels[:,:,:3][(labels==i)&(ids[:,:,3]>.995)].sum()) for i,region in enumerate(REGION_NAMES)}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('LINK_DIAGNOSTIC',json.dumps(report),flush=True)
