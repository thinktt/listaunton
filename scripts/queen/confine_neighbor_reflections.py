"""Confine three proven spill reflectors while retaining their intended glint energy."""
from pathlib import Path
import sys,json,hashlib,math
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'build/queen-mission/122-color-refined-base/queen.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;cfg=json.loads(s['mission_material_config']);out=ROOT/'build/queen-mission/123-confined-neighbor-lights';out.mkdir(parents=True,exist_ok=True);lights=[o for o in s.objects if o.type=='LIGHT'];powers={o.name:o.data.energy for o in lights};world=s.world.node_tree.nodes['Background'];world_power=world.inputs['Strength'].default_value;world.inputs['Strength'].default_value=0
for o in lights:o.data.energy=0
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA';s.render.use_persistent_data=True;s.cycles.samples=256;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
W=s.render.resolution_x;H=s.render.resolution_y;measurements=[];adjusted={};arrays={}
def render(name):
 path=out/(name+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);im=bpy.data.images.load(str(path),check_existing=False);w,h=im.size;a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(h,w,4)[::-1,:,:3].copy()
for key,(x,y),(rx,ry),degrees in [('lower-right',(566,528),(40,30),6),('socket-right',(553,764),(30,22),4),('foot-right',(618,1012),(40,18),4)]:
 name='Display fitted '+key;light=bpy.data.objects[name];assert light.data.type=='AREA';light.data.energy=powers[name];s.render.border_min_x=(x-rx)/W;s.render.border_max_x=(x+rx)/W;s.render.border_min_y=1-(y+ry)/H;s.render.border_max_y=1-(y-ry)/H
 old=render(key+'-old');light.data.spread=math.radians(degrees);new=render(key+'-confined');old_energy=powers[name];gain=float(old.sum()/max(new.sum(),1e-10));adjusted[name]=old_energy*gain;light.data.energy=0;arrays[key+'_old']=old;arrays[key+'_confined']=new*gain;record={'name':name,'crop_center':[x,y],'crop_radius':[rx,ry],'spread_degrees':degrees,'old_power':old_energy,'new_power':adjusted[name],'intended_glint_linear_sum_ratio':float((new*gain).sum()/old.sum())};measurements.append(record)
 spec=next(a for a in cfg['lights'] if a['name']==name);spec['spread_degrees']=degrees;spec['energy']=adjusted[name];print('CONFINED_REFLECTOR',json.dumps(record),flush=True)
for o in lights:o.data.energy=adjusted.get(o.name,powers[o.name])
world.inputs['Strength'].default_value=world_power;cfg['variant']=out.name;cfg['confined_neighbor_reflections']={'source_sha256':digest,'samples':256,'measurements':measurements,'method':'Limit area-light spread around each existing target. Fit power to preserve isolated physical BSDF energy in the intended glint ROI, excluding unrelated base spill.'};s['mission_material_config']=json.dumps(cfg);s['mission_variant']=out.name;np.savez_compressed(out/'intended-responses.npz',**arrays)
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.render.filepath=str(out/'wood.png');s.cycles.samples=128;s.cycles.use_adaptive_sampling=True;s.cycles.use_denoising=True;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'));bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2));print('CONFINED_NEIGHBORS_DONE',flush=True)
