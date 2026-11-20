"""Read-only black-BSDF light responses, separating reflection fitting from color."""
from pathlib import Path
import argparse,hashlib,json,math,shutil,sys
import bpy
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--spot-refinements',action='store_true');p.add_argument('--spot-degrees',type=float,default=4);p.add_argument('--directory');p.add_argument('--reuse-base-responses',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/'build/queen-mission/039-rolled-collar-refit/queen.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
o=next(o for o in s.objects if o.type=='MESH' and not o.hide_render);links=o.data.materials[0].node_tree.links;b=o.data.materials[0].node_tree.nodes.get('Principled BSDF')
for link in list(b.inputs['Base Color'].links):links.remove(link)
b.inputs['Base Color'].default_value=(0,0,0,1)
specs=[x for x in json.loads((ROOT/'build/queen-mission/light-fit/manifest.json').read_text())['specs'] if x['name']!='soft-fill']
specs.extend([
 {'name':'bowl-arc','position':[-.14,1.5,9.77],'target':[0,.3,4.03],'energy':400,'shape':'RECTANGLE','size':2.1,'size_y':.45},
 {'name':'finial-right','position':[3.92,-4.7,4.78],'target':[.06,-.14,4.36],'energy':120,'size':.3}
])
if args.spot_refinements:
 rays=json.loads((ROOT/'build/queen-mission/reflection-rays-026.json').read_text())
 for name in ['finial-left','finial-top','finial-right']:
  light=dict(next(s for s in specs if s['name']==name));light.update({'name':name+'-spot','type':'SPOT','spot_degrees':args.spot_degrees,'spot_blend':.25,'target':rays[name]['point'],'position':rays[name]['light_at_distance_6']});specs.append(light)
out=ROOT/(args.directory or ('build/queen-mission/specular-spots-039' if args.spot_refinements else 'build/queen-mission/specular-fit-039'));out.mkdir(parents=True,exist_ok=True)
reuse=ROOT/'build/queen-mission/specular-fit-039'
if args.reuse_base_responses:assert json.loads((reuse/'manifest.json').read_text())['source_sha256']==before
s.render.resolution_x=s.render.resolution_y=418;s.render.resolution_percentage=100
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA'
s.render.use_persistent_data=True;s.cycles.samples=64;s.cycles.use_denoising=False
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
for i,spec in enumerate(specs):
 if args.reuse_base_responses and not spec['name'].endswith('-spot'):
  for suffix in ('.npy','.exr'):shutil.copyfile(reuse/(spec['name']+suffix),out/(spec['name']+suffix))
  print('REUSED_IDENTICAL_SOURCE_RESPONSE',spec['name'],flush=True);continue
 for light in list(s.objects):
  if light.type=='LIGHT':bpy.data.objects.remove(light,do_unlink=True)
 s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=spec.get('world',0)
 if 'position' in spec:
  kind=spec.get('type','AREA');data=bpy.data.lights.new(spec['name'],kind);data.energy=spec['energy']
  if kind=='AREA':
   data.shape=spec.get('shape','DISK');data.size=spec['size']
   if data.shape=='RECTANGLE':data.size_y=spec['size_y']
  else:data.shadow_soft_size=spec['size']/2;data.spot_size=math.radians(spec['spot_degrees']);data.spot_blend=spec.get('spot_blend',.3)
  light=bpy.data.objects.new(spec['name'],data);s.collection.objects.link(light);light.location=spec['position'];light.rotation_euler=(Vector(spec.get('target',[0,0,2.3]))-light.location).to_track_quat('-Z','Y').to_euler()
 path=out/(spec['name']+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 im=bpy.data.images.load(str(path),check_existing=False);a=np.empty(418*418*4,dtype=np.float32);im.pixels.foreach_get(a);a=a.reshape(418,418,4)[::-1].copy();bpy.data.images.remove(im);np.save(out/(spec['name']+'.npy'),a)
 print('SPECULAR_BASIS_DONE',i+1,len(specs),spec['name'],flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
(out/'manifest.json').write_text(json.dumps({'source':source.relative_to(ROOT).as_posix(),'source_sha256':before,'width':418,'height':418,'samples':64,'denoising':False,'black_base_color_diagnostic_only':True,'specs':specs},indent=2)+'\n')
print('SPECULAR_BASES_COMPLETE',flush=True)
