"""Refine only the middle collar's lower bevel, preserving its peak radius/height."""
from pathlib import Path
import bpy,numpy as np,sys,json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh,set_material
from render_regions import partition,link
p=argparse.ArgumentParser();p.add_argument('--source',default='models/queen/queen-rebuilt.blend');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/args.source;digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest=='8b1c052b8c6960c6faf6760635090a7c081b04e5ad779641a4b9e49433f628c0'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;obj=editable_mesh(s);cfg=json.loads(s['mission_material_config'])
co=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',co);a=co.reshape(-1,192,3);before=a.copy()
snap=ROOT/'build/queen-mission/collar-profile-015/baseline-controls.npz';snap.parent.mkdir(exist_ok=True,parents=True);np.savez_compressed(snap,controls=before,source_sha256=digest)
changes=[]
for i,radius in {64:.565,65:.580,66:.584}.items():
 oldr=np.linalg.norm(a[i,:,:2],axis=1);a[i,:,:2]*=(radius/oldr)[:,None]
 changes.append({'ring':i,'old_radius':float(oldr.mean()),'new_radius':radius,'z':float(a[i,:,2].mean())})
keep=np.ones(len(a),dtype=bool);keep[[64,65,66]]=False
assert np.array_equal(a[keep],before[keep]) and np.array_equal(a[:,:,2],before[:,:,2])
for o in s.objects:
 if o.type=='LIGHT':o.light_linking.receiver_collection=None
for o in list(s.objects):
 if o.get('mission_render_region'):bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
 if c.name.startswith(('Queen render regions','Receivers ')):bpy.data.collections.remove(c)
obj.data.vertices.foreach_set('co',a.reshape(-1));obj.data.update();bpy.context.view_layer.update()
parts,report=partition(s,obj,socket_band=True,collar_band=True);byname={o['mission_render_region']:o for o in parts}
for spec in cfg['lights']:
 if spec.get('receiver_parts'):
  names=spec['receiver_parts'];link(bpy.data.objects[spec['name']],[byname[n] for n in names],'+'.join(names))
for part in parts:part.hide_set(True)
cfg['finial_receiver_isolation']['render_regions']=report
new_hash=hashlib.sha256(a.tobytes()).hexdigest()
for key in ['stem_socket_receiver_isolation','collar_receiver_isolation']:cfg[key]['closed_controls_sha256']=new_hash
cfg['middle_collar_edge_refinement']={'source_sha256':digest,'rings':changes,'unchanged_controls_sha256':hashlib.sha256(a[keep].tobytes()).hexdigest(),'all_heights_sha256':hashlib.sha256(a[:,:,2].tobytes()).hexdigest(),
 'method':'Fill the lower bevel radially at three controls; retain all heights, maximum middle-collar radius, peak ring, all other controls, camera, UVs, pigment and lights. Regenerate every exact light receiver.'}
variant='148-fuller-middle-lip';cfg['variant']=variant;s['mission_material_config']=json.dumps(cfg);s['mission_variant']=variant
out=ROOT/'build/queen-mission'/variant;out.mkdir(exist_ok=True,parents=True);s.render.filepath=str(out/'wood.png');s.cycles.samples=64;s.cycles.use_denoising=True;s.render.use_persistent_data=True;bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
clay=bpy.data.materials.new('Middle collar edge inspection clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.24,.26,.29,1);bs.inputs['Roughness'].default_value=.32;set_material(s,clay)
s.render.filepath=str(out/'neutral.png');bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print('MIDDLE_EDGE_TRIAL_DONE',json.dumps(changes),flush=True)
