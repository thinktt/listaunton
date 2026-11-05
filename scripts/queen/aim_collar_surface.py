"""Aim middle-collar emitters using measured textured normals and inspect shadows."""
from pathlib import Path
import bpy,numpy as np,json,sys,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'build/queen-mission/148-fuller-middle-lip/queen.blend';capture=ROOT/'build/queen-mission/collar-surface-148'
digest=hashlib.sha256(source.read_bytes()).hexdigest();assert json.loads((capture/'manifest.json').read_text())['source_sha256']==digest
positions=np.load(capture/'position.npy');normals=np.load(capture/'normal.npy')
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;cfg=json.loads(s['mission_material_config']);view=s.camera.matrix_world.to_3x3()@Vector((0,0,1));view.normalize();report=[]
prior={p['name']:p['energy'] for p in cfg['lights'] if p['name'].startswith(('Collar crescent ','Collar retained '))}
for spec in cfg['lights']:
 name=spec['name'];light=bpy.data.objects[name]
 if name.startswith('Collar crescent '):
  light.data.energy=400;spec['energy']=400
  if 6<=int(name.split()[-1])<=16:
   tx,ty=spec['target_pixel'];x,y=tx-290,ty-350;options=[]
   for yy in range(y-3,y+4):
    for xx in range(x-3,x+4):
     if positions[yy,xx,3]>.999 and 2.98<positions[yy,xx,2]<3.15:options.append(((xx-x)**2+(yy-y)**2,xx,yy))
   assert options,name
   _,xx,yy=min(options);loc=Vector(positions[yy,xx,:3]);local=[]
   for qy in range(yy-1,yy+2):
    for qx in range(xx-1,xx+2):
     if positions[qy,qx,3]>.999 and 2.98<positions[qy,qx,2]<3.15 and np.linalg.norm(positions[qy,qx,:3]-np.array(loc))<.03:local.append(normals[qy,qx,:3])
   normal=Vector(np.mean(local,axis=0));normal.normalize();assert normal.dot(view)>.03
   direction=2*normal.dot(view)*normal-view;pos=loc+direction*6;light.location=pos;light.rotation_euler=(loc-pos).to_track_quat('-Z','Y').to_euler()
   spec.update(position=list(pos),target=list(loc),surface_pixel=[xx+290,yy+350],surface_normal=list(normal))
   report.append({'name':name,'requested_pixel':[tx,ty],'surface_pixel':[xx+290,yy+350],'normal_samples':len(local),'target_z':loc.z,'normal':list(normal)})
 elif name.startswith('Collar retained '):light.data.energy=bpy.data.objects[spec['clone_of']].data.energy;spec['energy']=light.data.energy
cfg['variant']='149-textured-collar-aim';cfg['collar_surface_aim']={'source_sha256':digest,'prior_energies':prior,'targets':report,'method':'Native emitted world positions and actual bump normals, averaged over same-surface 3x3 neighbors. At occluding edges use the nearest middle-collar pixel within three pixels; reference registration is unchanged.'}
s['mission_material_config']=json.dumps(cfg);s['mission_variant']=cfg['variant'];out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(exist_ok=True,parents=True);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'));(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
diag=ROOT/'build/queen-mission/collar-shadow-149';diag.mkdir(exist_ok=True,parents=True)
for o in s.objects:
 if o.type=='LIGHT':o.data.energy=0
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
light=bpy.data.objects['Collar crescent 06'];light.data.energy=400
props={'light_use_shadow':hasattr(light.data,'use_shadow'),'cycles_cast_shadow':hasattr(light.data.cycles,'cast_shadow')};print('SHADOW_PROPERTIES',props,flush=True)
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=(290+.01)/1254;s.render.border_max_x=(680+.01)/1254;s.render.border_min_y=(1254-565+.01)/1254;s.render.border_max_y=(1254-350+.01)/1254
s.cycles.samples=256;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
for shadows in [True,False]:
 if props['light_use_shadow']:light.data.use_shadow=shadows
 if props['cycles_cast_shadow']:light.data.cycles.cast_shadow=shadows
 s.render.filepath=str(diag/('with-shadows.png' if shadows else 'without-shadows.png'));bpy.ops.render.render(write_still=True)
(diag/'manifest.json').write_text(json.dumps({'source_sha256':digest,'properties':props,'light':light.name,'targets':report},indent=2)+'\n')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print('COLLAR_SURFACE_AIM_DONE',flush=True)
