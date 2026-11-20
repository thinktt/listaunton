"""Measure each existing body reflector independently without saving source edits."""
import argparse,hashlib,json,sys,math
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True)
p.add_argument('--basis-energy',type=float,default=5000);p.add_argument('--samples',type=int,default=64)
p.add_argument('--lighting-config')
p.add_argument('--border',nargs=4,type=int,default=[180,270,800,1120],metavar=('X0','Y0','X1','Y1'))
p.add_argument('--fixed-samples',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
names=['head reflection','collars reflection','socket reflection','base reflection'];lamps=[bpy.data.objects[name] for name in names]
assert all(lamp.visible_glossy and not lamp.visible_diffuse for lamp in lamps)
configuration=json.loads((ROOT/a.lighting_config).read_text()) if a.lighting_config else None
if configuration:
    for spec in configuration['lights']:
        assert spec['name'] in names
        ob=bpy.data.objects[spec['name']]
        for key in ['energy','color','size','size_y','shape']:
            if key in spec:setattr(ob.data,key,spec[key])
        if 'spread_degrees' in spec:ob.data.spread=math.radians(spec['spread_degrees'])
original=[]
for ob in lamps:
    original.append({'name':ob.name,'energy':ob.data.energy,'color':list(ob.data.color),'shape':ob.data.shape,
        'size':ob.data.size,'size_y':ob.data.size_y,'spread_radians':ob.data.spread,
        'position':list(ob.location),'rotation_euler':list(ob.rotation_euler),
        'receiver':ob.light_linking.receiver_collection.name if ob.light_linking.receiver_collection else None})
    ob.data.energy=0;ob.data.color=(1,1,1)
s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=False
w,h=s.render.resolution_x,s.render.resolution_y;box=a.border
s.render.border_min_x=box[0]/w;s.render.border_max_x=box[2]/w;s.render.border_min_y=1-box[3]/h;s.render.border_max_y=1-box[1]/h
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='32'
s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.render.use_persistent_data=True
if a.fixed_samples:s.cycles.use_adaptive_sampling=False
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type=='OPTIX'
if any(dev.use for dev in prefs.devices):s.cycles.device='GPU'
def render(name):
    file=out/(name+'.exr');s.render.filepath=str(file);bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(str(file),check_existing=False);assert list(im.size)==[w,h]
    values=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[::-1].copy();np.save(out/(name+'.npy'),values);bpy.data.images.remove(im)
    print('BISHOP_BODY_RESPONSE',name,flush=True)
render('base')
for i,ob in enumerate(lamps):
    ob.data.energy=a.basis_energy;render('reflector-'+str(i+1));ob.data.energy=0
for ob,old in zip(lamps,original):ob.data.energy=old['energy'];ob.data.color=old['color']
render('actual-current')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source':a.source,'source_sha256':digest,'original_lights':original,'lighting_config':configuration,'basis_energy':a.basis_energy,
    'basis_color':[1,1,1],'camera_unchanged':True,'source_unchanged':True,'render_border_pixels':box,'samples':a.samples,'adaptive_sampling':s.cycles.use_adaptive_sampling,
    'purpose':'Measure actual BSDF response and light spill. Diagnostic source remains unchanged.'},indent=2)+'\n')
print('BISHOP_BODY_RESPONSES_COMPLETE',flush=True)
