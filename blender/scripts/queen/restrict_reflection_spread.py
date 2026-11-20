"""Confine lower reflection lights to their intended regions and retain power fit."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from configure_rig import configure
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--source',default='build/queen-mission/071-limited-base-reflector/queen.blend');p.add_argument('--variant',default='072-confined-reflections');p.add_argument('--remaining',action='store_true')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/args.source
digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
cfg=json.loads(s['mission_material_config']);basis=ROOT/'build/queen-mission/specular-expanded-039'
manifest=json.loads((basis/'manifest.json').read_text());oldspecs={v['name']:v for v in manifest['specs']}
targets={'upper-right':(543,439),'socket-right':(553,764),'foot-right':(618,1012),'collars-right':(580,477),'lower-right':(566,528)}
if args.remaining:
 targets={};disabled=[]
 for light in cfg['lights']:
  if light.get('diffuse_factor',1)!=0 or light.get('type','AREA')!='AREA':continue
  name=light['name'].removeprefix('Display fitted ')
  if name.startswith('original-'):
   light['energy']=0;disabled.append(light['name']);continue
  if 'spread_degrees' in light:continue
  point=world_to_camera_view(s,s.camera,Vector(light['target']))
  targets[name]=(round(point.x*1254),round((1-point.y)*1254))
 cfg['disabled_global_reflections']=disabled
o=next(o for o in s.objects if o.type=='MESH' and not o.hide_render);nodes=o.data.materials[0].node_tree.nodes;links=o.data.materials[0].node_tree.links;b=nodes.get('Principled BSDF')
color=b.inputs['Base Color'].links[0].from_socket
for link in list(b.inputs['Base Color'].links):links.remove(link)
b.inputs['Base Color'].default_value=(0,0,0,1)
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(parents=True,exist_ok=True)
s.render.resolution_x=s.render.resolution_y=418;s.render.use_persistent_data=True;s.cycles.samples=64;s.cycles.use_denoising=False
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA'
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
records=[]
for name,(px,py) in targets.items():
 spec=next(v for v in cfg['lights'] if v['name']=='Display fitted '+name);old_energy=spec['energy'];oldspec=oldspecs[name]
 old=np.load(basis/(name+'.npy'))[:,:,:3]*(old_energy/oldspec['energy'])
 spec['spread_degrees']=12;test=dict(spec);test['energy']=oldspec['energy'];test['color']=[1,1,1]
 configure(s,{'lights':[test],'world':0,'cycles_ray_visibility':True});s.render.filepath=str(out/('diagnostic-'+name+'.exr'));bpy.ops.render.render(write_still=True)
 im=bpy.data.images.load(s.render.filepath,check_existing=False);a=np.empty(418*418*4,dtype=np.float32);im.pixels.foreach_get(a);a=a.reshape(418,418,4)[::-1].copy();bpy.data.images.remove(im);np.save(out/('diagnostic-'+name+'.npy'),a)
 cx,cy=round(px/3),round(py/3);roi=(slice(cy-8,cy+9),slice(cx-8,cx+9));x=a[roi][:,:,:3];y=old[roi]
 factor=float(np.sum(x*y)/max(np.sum(x*x),1e-12));assert 0<factor<10,(name,factor)
 spec['energy']=oldspec['energy']*factor
 before=float(old[49:89,141:181].sum());after=float((a[49:89,141:181,:3]*factor).sum())
 record={'name':name,'spread_degrees':12,'previous_energy':old_energy,'new_energy':spec['energy'],'fit_pixel_at_1254':[px,py],'fit_half_width_at_418':8,'old_response_sha256':hashlib.sha256((basis/(name+'.npy')).read_bytes()).hexdigest(),'response_path':(out/('diagnostic-'+name+'.npy')).relative_to(ROOT).as_posix(),'basis_energy':oldspec['energy'],'finial_linear_sum_before':before,'finial_linear_sum_after':after}
 records.append(record);print('REFLECTION_CONFINED',record,flush=True)
links.new(color,b.inputs['Base Color']);configure(s,cfg)
prior=cfg.get('confined_reflections',{}).get('lights',[]) if args.remaining else []
cfg['variant']=args.variant;cfg['source']=source.relative_to(ROOT).as_posix();cfg['confined_reflections']={'source_sha256':digest,'lights':prior+records,'method':'Narrow real area-light spread; fit power only in each intended highlight neighborhood using unchanged geometry/black-BSDF response. No image is projected as light.'}
s['mission_material_config']=json.dumps(cfg,sort_keys=True);s.render.resolution_x=s.render.resolution_y=1254;s.cycles.use_denoising=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'));bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print('CONFINED_REFLECTIONS_DONE',flush=True)
