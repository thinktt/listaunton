"""Compare real BSDF socket crops with broader existing emitters; no scene saves."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',default='history/bishop-mission-010/bishop-rebuilt.blend')
p.add_argument('--out',default='build/bishop-mission/088-socket-emitter-probe')
p.add_argument('--samples',type=int,default=256)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT/a.source;out=ROOT/a.out
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
out.mkdir(parents=True,exist_ok=True);digest=hashlib.sha256(source.read_bytes()).hexdigest()
variants=[('radius-012',.012,1,1),('radius-024',.024,1,1),
          ('radius-012-cone14',.012,1.4,1.96),('radius-024-cone14',.024,1.4,1.96)]
records=[]
for label,radius,degrees,power in variants:
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    lamps=[o for o in s.objects if o.type=='LIGHT' and o.name.startswith('socket arc ')]
    assert len(lamps)==17
    changes=[]
    for lamp in lamps:
        lamp.data.shadow_soft_size=radius
        lamp.data.spot_size=math.radians(degrees)
        lamp.data.energy*=power
        changes.append({'name':lamp.name,'shadow_soft_size':lamp.data.shadow_soft_size,
                        'spot_size':lamp.data.spot_size,'energy':lamp.data.energy})
    s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=False
    s.render.border_min_x=330/1254;s.render.border_max_x=660/1254
    s.render.border_min_y=1-885/1254;s.render.border_max_y=1-710/1254
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
    s.cycles.samples=a.samples;s.cycles.use_adaptive_sampling=False
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
    s.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    config={'source':a.source,'variant':'089-'+label,'samples':256,'adaptive_sampling':False,
            'hypothesis':'Broader existing sources produce a wider cream socket band without changing the material.',
            'lights':changes}
    (out/(label+'.json')).write_text(json.dumps(config,indent=2)+'\n')
    records.append({'label':label,'radius':radius,'cone_degrees':degrees,'power_factor':power,
                    'render_sha256':hashlib.sha256((out/(label+'.png')).read_bytes()).hexdigest()})
    print('SOCKET_EMITTER_PROBE',label,flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source':a.source,'source_sha256':digest,'source_unchanged':True,
 'samples':a.samples,'crop':[330,710,660,885],'fixed_camera':True,'diagnostics_only':True,'variants':records},indent=2)+'\n')
