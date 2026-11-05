"""Identify other reflectors contributing to the queen base's unwanted broad glint."""
from pathlib import Path
import bpy,numpy as np,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'build/queen-mission/122-color-refined-base/queen.blend';before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;lights=[o for o in s.objects if o.type=='LIGHT'];powers={o.name:o.data.energy for o in lights};out=ROOT/'build/queen-mission/base-spill-012';out.mkdir(parents=True,exist_ok=True)
x1,y1,x2,y2=480,780,720,1040;W=s.render.resolution_x;H=s.render.resolution_y;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=x1/W;s.render.border_max_x=x2/W;s.render.border_min_y=1-y2/H;s.render.border_max_y=1-y1/H;s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA';s.render.use_persistent_data=True;s.cycles.samples=256;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False
for o in lights:o.data.energy=0
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
names=['original-top','original-right','foot-right','socket-right','lower-right','socket-left-precise','lower-collar','original-foot'];responses={};scores=[]
for key in names:
 name='Display fitted '+key;light=bpy.data.objects.get(name)
 if light is None:continue
 light.data.energy=powers[name];path=out/(key+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);im=bpy.data.images.load(str(path),check_existing=False);w,h=im.size;a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);a=a.reshape(h,w,4)[::-1,:,:3].copy();responses[key]=a;lum=a@np.array([.2126,.7152,.0722]);yy,xx=np.indices(lum.shape);scores.append({'name':name,'linear_luminance_sum':float(lum.sum()),'centroid':[float((lum*xx).sum()/max(lum.sum(),1e-9)+x1),float((lum*yy).sum()/max(lum.sum(),1e-9)+y1)]});s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(out/(key+'.png')),scene=s);s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';light.data.energy=0;print('SPILL_RESPONSE',key,flush=True)
np.savez_compressed(out/'responses.npz',**responses);assert hashlib.sha256(source.read_bytes()).hexdigest()==before;(out/'manifest.json').write_text(json.dumps({'source_sha256':before,'crop':[x1,y1,x2,y2],'samples':256,'source_unchanged':True,'lights':sorted(scores,key=lambda x:-x['linear_luminance_sum'])},indent=2));print('SPILL_INSPECTION_DONE',flush=True)
