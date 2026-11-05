"""Place the three real finial reflectors at measured reference-glint targets."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy,numpy as np
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from render_regions import link
p=argparse.ArgumentParser()
p.add_argument('--source',default='build/queen-mission/163-finial-pigment-repair/queen.blend')
p.add_argument('--capture',default='finial-surface-163')
p.add_argument('--targets',default='finial-targets-016')
p.add_argument('--variant',default='164-refined-finial-targets')
p.add_argument('--cone',type=float,default=12)
p.add_argument('--retain-elsewhere',action='store_true')
p.add_argument('--emitter-radius-factor',type=float,default=2)
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/args.source
digest=hashlib.sha256(source.read_bytes()).hexdigest()
capture=ROOT/'build/queen-mission'/args.capture
manifest=json.loads((capture/'manifest.json').read_text())
assert manifest['source_sha256']==digest
x1,y1,x2,y2=manifest['crop']
positions=np.load(capture/'position.npy');normals=np.load(capture/'normal.npy')
targets=json.loads((ROOT/'build/queen-mission'/args.targets/'targets.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;cfg=json.loads(s['mission_material_config'])
view=(s.camera.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
report=[]
for target in targets['targets']:
    name=target['name'];light=bpy.data.objects[name]
    linked=light.light_linking.receiver_collection
    previous_links=None if linked is None else [o.get('mission_render_region') for o in linked.all_objects]
    if args.retain_elsewhere:
        prior=next(x for x in cfg['lights'] if x['name']==name)
        clone=light.copy();clone.data=light.data.copy()
        clone.name='Finial retained '+name.split('-')[-2];s.collection.objects.link(clone)
        others=[o for o in s.objects if o.get('mission_render_region') and o['mission_render_region']!='finial']
        link(clone,others,'finial-prior-on-body')
        clone_spec=dict(prior,name=clone.name,clone_of=name,shadow_soft_size=clone.data.shadow_soft_size,rotation_euler=list(clone.rotation_euler),receiver_parts=sorted(o['mission_render_region'] for o in others))
        cfg['lights'].append(clone_spec)
        cfg['finial_receiver_isolation']['excluded_reflectors'].append(clone.name)
    finial=next(o for o in s.objects if o.get('mission_render_region')=='finial')
    link(light,[finial],'finial-glints')
    parts={o.get('mission_render_region') for o in light.light_linking.receiver_collection.all_objects}
    assert parts=={'finial'},(name,parts)
    assert not light.visible_diffuse and light.visible_glossy
    tx,ty=target['pixel'];xx=int(round(tx))-x1;yy=int(round(ty))-y1
    assert positions[yy,xx,3]>.999
    loc=Vector(positions[yy,xx,:3])
    local=[]
    for py in range(yy-1,yy+2):
        for px in range(xx-1,xx+2):
            if positions[py,px,3]>.999 and np.linalg.norm(positions[py,px,:3]-np.asarray(loc))<.03:
                local.append(normals[py,px,:3])
    normal=Vector(np.mean(local,axis=0)).normalized()
    assert normal.dot(view)>.1
    direction=(2*normal.dot(view)*normal-view).normalized()
    spec=next(x for x in cfg['lights'] if x['name']==name)
    previous=dict(spec)
    previous['actual_shadow_soft_size']=light.data.shadow_soft_size
    olddistance=(Vector(spec['position'])-Vector(spec['target'])).length
    distance=6
    light.location=loc+distance*direction
    light.rotation_euler=(loc-light.location).to_track_quat('-Z','Y').to_euler()
    light.data.shadow_soft_size=light.data.shadow_soft_size*args.emitter_radius_factor*distance/olddistance
    light.data.energy=spec['energy']*(distance/olddistance)**2
    light.data.spot_size=math.radians(args.cone)
    spec.update(position=list(light.location),target=list(loc),size=2*light.data.shadow_soft_size,shadow_soft_size=light.data.shadow_soft_size,rotation_euler=list(light.rotation_euler),
                energy=light.data.energy,spot_degrees=args.cone,target_pixel=[tx,ty],
                surface_pixel=[xx+x1,yy+y1],surface_normal=list(normal),receiver_parts=['finial'])
    report.append({'name':name,'previous':previous,'current':dict(spec),'normal_samples':len(local),
                   'previous_receivers':previous_links,'receivers':sorted(parts),'visible_diffuse':light.visible_diffuse,'visible_glossy':light.visible_glossy})
cfg['variant']=args.variant
cfg['finial_reflector_aim']={'source_sha256':digest,'capture':args.capture,'targets':targets,'changes':report,'retained_prior_lights_elsewhere':args.retain_elsewhere,'emitter_radius_factor':args.emitter_radius_factor,
    'method':'Use actual bump normals averaged over same-surface 3x3 neighbors and the reflected orthographic view direction. Explicitly scale the physical emitter radius and preserve initial inverse-square irradiance before power fitting; widen cone to avoid clipping the specular lobe. Three finial-only glossy lights; optional exact prior-light copies preserve illumination elsewhere.'}
s['mission_material_config']=json.dumps(cfg);s['mission_variant']=args.variant
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(exist_ok=True,parents=True)
s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.samples=64;s.cycles.use_denoising=True
s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'queen.blend'),load_ui=False)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):bpy.context.scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print('FINIAL_REFLECTORS_AIMED',json.dumps(report),flush=True)
