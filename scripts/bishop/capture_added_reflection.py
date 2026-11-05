"""Measure an added real reflector against the unchanged accepted bishop rig."""
import argparse,hashlib,json,sys,math
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('config');p.add_argument('--out',required=True);p.add_argument('--samples',type=int,default=64)
p.add_argument('--fixed-samples',action='store_true');p.add_argument('--crop-tip',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads((ROOT/a.config).read_text());source=ROOT/cfg['source']
digest=hashlib.sha256(source.read_bytes()).hexdigest();out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
assert len(cfg['lights'])==1
spec=cfg['lights'][0];assert spec['name'] not in bpy.data.objects
data=bpy.data.lights.new(spec['name'],spec.get('type','AREA'));ob=bpy.data.objects.new(spec['name'],data);s.collection.objects.link(ob)
ob.location=spec['position'];ob.rotation_euler=(Vector(spec['target'])-ob.location).to_track_quat('-Z','Y').to_euler()
for key in ['shape','size','size_y','spot_size','spot_blend','shadow_soft_size']:
    if key in spec:setattr(data,key,spec[key])
if 'spread_degrees' in spec:data.spread=math.radians(spec['spread_degrees'])
data.color=(1,1,1)
ob.visible_diffuse=False;ob.visible_glossy=True
ob.light_linking.receiver_collection=bpy.data.collections['Bishop light receiver body']
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_percentage=100
if a.crop_tip:
    w,h=s.render.resolution_x,s.render.resolution_y;s.render.use_border=True
    s.render.border_min_x=445/w;s.render.border_max_x=565/w;s.render.border_min_y=1-480/h;s.render.border_max_y=1-385/h
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='32'
s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.render.use_persistent_data=True
if a.fixed_samples:s.cycles.use_adaptive_sampling=False
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type=='OPTIX'
if any(dev.use for dev in prefs.devices):s.cycles.device='GPU'
def render(name):
    file=out/(name+'.exr');s.render.filepath=str(file);bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(str(file),check_existing=False);w,h=im.size
    ar=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[::-1].copy();np.save(out/(name+'.npy'),ar);bpy.data.images.remove(im)
    print('ADDED_REFLECTION_RESPONSE',name,flush=True)
data.energy=0;render('base')
data.energy=spec['energy'];render('added')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
record={'source':cfg['source'],'source_sha256':digest,'config':cfg,'basis_energy':spec['energy'],'basis_color':[1,1,1],
        'samples':a.samples,'camera_unchanged':True,'source_unchanged':True,'original_rig_retained':True,
        'adaptive_sampling':s.cycles.use_adaptive_sampling,'render_border_pixels':[445,385,565,480] if a.crop_tip else None,
        'note':'Real BSDF diagnostic passes only; no scene saved. Accept only after a full candidate render.'}
record['effective_light']={key:getattr(data,key) for key in ['type','energy','size','size_y','shape','spread','spot_size','spot_blend','shadow_soft_size'] if hasattr(data,key)}
(out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print('ADDED_REFLECTION_CAPTURE_COMPLETE',flush=True)
