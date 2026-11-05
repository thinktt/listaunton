"""Constrain measured collar emitters to exact ring surfaces; inspect artistic fills."""
from pathlib import Path
import bpy,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from render_regions import partition,link
source=ROOT/'build/queen-mission/149-textured-collar-aim/queen.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;obj=editable_mesh(s);cfg=json.loads(s['mission_material_config'])
for o in s.objects:
 if o.type=='LIGHT':o.light_linking.receiver_collection=None
for o in list(s.objects):
 if o.get('mission_render_region'):bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
 if c.name.startswith(('Queen render regions','Receivers ')):bpy.data.collections.remove(c)
parts,report=partition(s,obj,socket_band=True,collar_band=True,split_collars=True);byname={o['mission_render_region']:o for o in parts}
bands=['lower-collar','middle-collar','upper-collar'];fills=[]
for spec in cfg['lights']:
 light=bpy.data.objects[spec['name']]
 if spec.get('receiver_parts'):
  names=[]
  for name in spec['receiver_parts']:names.extend(bands if name=='collars' else [name])
  if spec['name'].startswith('Collar crescent '):
   i=int(spec['name'].split()[-1]);names=[bands[2 if i<6 else 1 if i<17 else 0]]
   if i in [6,7,8]:light.data.use_shadow=False;spec['use_shadow']=False;fills.append(light.name)
  spec['receiver_parts']=names;link(light,[byname[n] for n in names],'+'.join(names))
for part in parts:part.hide_set(True)
cfg['finial_receiver_isolation']['render_regions']=report;cfg['subdivided_collar_receivers']={'source_sha256':digest,'regions':{'lower-collar':[2.78,2.97],'middle-collar':[2.97,3.16],'upper-collar':[3.16,3.34]},'nonshadowing_fills':fills,
 'method':'Exact evaluated face subdivision, preserving geometry/UVs/custom normals. Each new crescent emitter illuminates its intended collar only. Three left-edge specular fills omit cast shadows after native diagnostics showed self-occlusion; this is an explicit artistic lighting approximation.'}
cfg['variant']='150-separated-collar-fills';s['mission_material_config']=json.dumps(cfg);s['mission_variant']=cfg['variant'];out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(exist_ok=True,parents=True);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'));(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest;print('COLLAR_BANDS_PREPARED',flush=True)
