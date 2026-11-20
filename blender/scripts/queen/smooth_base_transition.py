"""Smooth the small ledge where the flared base rolls into the socket wall."""
from pathlib import Path
import sys,json,hashlib,argparse
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh,set_material
from render_regions import partition,link
p=argparse.ArgumentParser();p.add_argument('--source',default='models/queen/queen-rebuilt.blend');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);source=ROOT/args.source;digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest=='2cb513a71cf36e6bbaa3619b95cc53208e1245f9dbefebc745470e582fc11a9b';bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;obj=editable_mesh(s);cfg=json.loads(s['mission_material_config'])
for light in [o for o in s.objects if o.type=='LIGHT']:light.light_linking.receiver_collection=None
for o in list(s.objects):
 if o.get('mission_render_region'):bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
 if c.name.startswith(('Queen render regions','Receivers ')):bpy.data.collections.remove(c)
a=np.array([tuple(v.co) for v in obj.data.vertices],dtype=np.float32).reshape(-1,192,3);before=a.copy();r=np.linalg.norm(a[:,:,:2],axis=2).mean(1);z=a[:,:,2].mean(1);m0=float((r[25]-r[24])/(z[25]-z[24]));span=float(z[29]-z[25]);target=float(r[31]);changed=[]
for i in range(26,30):
 t=float((z[i]-z[25])/span);value=(2*t**3-3*t*t+1)*float(r[25])+(t**3-2*t*t+t)*span*m0+(-2*t**3+3*t*t)*target;a[i,:,:2]*=value/r[i];changed.append({'ring':i,'old_radius':float(r[i]),'new_radius':value,'z':float(z[i])})
keep=np.ones(len(a),dtype=bool);keep[26:30]=False;assert np.array_equal(a[keep],before[keep]);obj.data.vertices.foreach_set('co',a.reshape(-1));obj.data.update();bpy.context.view_layer.update();parts,report=partition(s,obj,finial_only=True);body=next(o for o in parts if o['mission_render_region']=='turned-body')
for spec in cfg['lights']:
 if spec.get('diffuse_factor',1)==0 and not ('finial-' in spec['name'] and spec['name'].endswith('-spot')):link(bpy.data.objects[spec['name']],[body],'turned-body')
for part in parts:part.hide_set(True)
variant='125-smooth-base-transition';cfg['variant']=variant;cfg['finial_receiver_isolation']['render_regions']=report;cfg['base_transition_refinement']={'source_sha256':digest,'rings':changed,'unchanged_controls_sha256':hashlib.sha256(before[keep].tobytes()).hexdigest(),'method':'Cubic Hermite radius through rings 25-29, matching the incoming flare slope and ending tangent to the socket cylinder. Only radii of rings 26-29 change; all heights, other controls, camera, UVs, material and lights are retained.'};s['mission_material_config']=json.dumps(cfg);s['mission_variant']=variant;out=ROOT/'build/queen-mission'/variant;out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png');s.cycles.samples=64;s.cycles.use_denoising=True;s.render.use_persistent_data=True;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True);mat=bpy.data.materials.new('Base transition inspection clay');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.24,.26,.29,1);bs.inputs['Roughness'].default_value=.32;set_material(s,mat);s.render.filepath=str(out/'neutral.png');bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2));print('BASE_TRANSITION_DONE',json.dumps(changed),flush=True)
