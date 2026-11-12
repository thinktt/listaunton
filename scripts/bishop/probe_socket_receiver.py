"""Test exact socket light receivers in unsaved, actual BSDF crop renders."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from render_regions import partition_socket,socket_only
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',default='history/bishop-mission-010/bishop-rebuilt.blend')
p.add_argument('--out',default='build/bishop-mission/094-socket-receiver-probe')
p.add_argument('--samples',type=int,default=256)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;out=ROOT/a.out
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve());out.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(source.read_bytes()).hexdigest();records=[]
variants=[('partition-control',False,None,None),('confined-control',True,None,None),
          ('confined-wide14',True,.024,1.4),('confined-wide20',True,.024,2),('confined-soft20',True,.05,2)]
for name,confined,radius,cone in variants:
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    parts,partition=partition_socket(s)
    lamps=[o for o in s.objects if o.type=='LIGHT' and o.name.startswith('socket arc ')];assert len(lamps)==17
    if confined:socket_only(lamps,parts)
    for lamp in lamps:
        if radius is not None:lamp.data.shadow_soft_size=radius
        if cone is not None:lamp.data.spot_size=math.radians(cone)
    s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=False
    s.render.border_min_x=330/1254;s.render.border_max_x=660/1254
    s.render.border_min_y=1-885/1254;s.render.border_max_y=1-710/1254
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
    s.cycles.samples=a.samples;s.cycles.use_adaptive_sampling=False
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for device in prefs.devices:device.use=device.type=='OPTIX'
    s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
    s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    records.append({'name':name,'socket_lights_confined':confined,'radius':radius,'cone_degrees':cone,
      'power_factor':1,'partition':partition,'render_sha256':hashlib.sha256((out/(name+'.png')).read_bytes()).hexdigest()})
    print('SOCKET_RECEIVER_PROBE',name,flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source':a.source,'source_sha256':digest,'source_unchanged':True,
 'diagnostics_only':True,'samples':a.samples,'crop':[330,710,660,885],'z_band':[1.20,1.38],'variants':records,
 'note':'Unchanged evaluated surface, UVs, materials and custom smooth normals. Control remains closed/editable. Diagnostic scenes are not saved.'},indent=2)+'\n')
