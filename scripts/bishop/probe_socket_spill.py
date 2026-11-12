"""Test measured head/collar reflection spill on the socket, without scene saves."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from render_regions import partition_socket,socket_only
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--samples',type=int,default=256)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT/'history/bishop-mission-010/bishop-rebuilt.blend';out=ROOT/'build/bishop-mission/095-socket-spill-probe';out.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(source.read_bytes()).hexdigest();records=[]
variants=[('socket-control',[]),('without-collar-spill',['collars reflection']),
          ('without-head-collar-spill',['head reflection','collars reflection'])]
for name,excluded in variants:
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    parts,partition=partition_socket(s,.99,1.38)
    arcs=[o for o in s.objects if o.type=='LIGHT' and o.name.startswith('socket arc ')];assert len(arcs)==17
    socket_only(arcs,parts)
    for lamp in arcs:lamp.data.shadow_soft_size=.024;lamp.data.spot_size=math.radians(2)
    rest=next(o for o in parts if o['bishop_render_region']=='body-rest')
    collection=bpy.data.collections.new('Bishop all body except socket');collection.objects.link(rest)
    for light in excluded:bpy.data.objects[light].light_linking.receiver_collection=collection
    s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=False
    s.render.border_min_x=330/1254;s.render.border_max_x=660/1254
    s.render.border_min_y=1-885/1254;s.render.border_max_y=1-710/1254
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
    s.cycles.samples=a.samples;s.cycles.use_adaptive_sampling=False
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
    s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    records.append({'name':name,'excluded_lights':excluded,'partition':partition,'render_sha256':hashlib.sha256((out/(name+'.png')).read_bytes()).hexdigest()})
    print('SOCKET_SPILL_PROBE',name,flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source':str(source.relative_to(ROOT)),'source_sha256':digest,
 'source_unchanged':True,'samples':a.samples,'z_band':[.99,1.38],'arc_radius':.024,'arc_cone_degrees':2,
 'arc_power_factor':1,'diagnostics_only':True,'variants':records},indent=2)+'\n')
