"""Finial seating trial: edit closed control and regenerate linked receivers."""
from pathlib import Path
import sys,json,hashlib,argparse
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh,set_material
from render_regions import partition,link
p=argparse.ArgumentParser();p.add_argument('--variant',default='096-seated-finial');p.add_argument('--height',type=float,default=.85);p.add_argument('--radius',type=float,default=.96);args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
assert Path(args.variant).name==args.variant and args.variant not in ('.','..')
assert 0.5 <= args.height <= 1 and 0.5 <= args.radius <= 1
source=ROOT/'history/queen-mission-008/queen-rebuilt.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='c32bccbf33e5e137d982bdeafd881a783b006f62e644dbd5db2df57d02801004'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene;obj=editable_mesh(scene)
for light in [o for o in scene.objects if o.type=='LIGHT']:light.light_linking.receiver_collection=None
for o in list(scene.objects):
 if o.get('mission_render_region'):bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
 if c.name.startswith(('Queen render regions','Receivers ')):bpy.data.collections.remove(c)
a=np.array([tuple(v.co) for v in obj.data.vertices],dtype=np.float32).reshape(-1,192,3)
baseline_body_sha=hashlib.sha256(a[:107].tobytes()).hexdigest()
original_top=float(a[:,:,2].max())
anchor=float(a[106,:,2].mean())
for i in range(107,len(a)):
 weight=min(1.,(i-106)/2)
 a[i,:,:2]*=1+(args.radius-1)*weight
 a[i,:,2]=anchor+(a[i,:,2]-anchor)*args.height
obj.data.vertices.foreach_set('co',a.reshape(-1));obj.data.update();bpy.context.view_layer.update()
parts,report=partition(scene,obj,finial_only=True)
body=next(o for o in parts if o['mission_render_region']=='turned-body')
settings=json.loads(scene['mission_material_config'])
for spec in settings['lights']:
 if spec.get('diffuse_factor',1)==0 and not ('finial-' in spec['name'] and spec['name'].endswith('-spot')):link(bpy.data.objects[spec['name']],[body],'turned-body')
for part in parts:part.hide_set(True)
settings['variant']=args.variant
settings['finial_receiver_isolation']['render_regions']=report
settings['finial_seating']={'height_factor':args.height,'radial_factor':args.radius,'anchor':anchor,'top_lowering':original_top-float(a[:,:,2].max()),'unchanged_body_sha256':baseline_body_sha}
scene['mission_material_config']=json.dumps(settings);scene['mission_variant']=args.variant
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(parents=True,exist_ok=True)
scene.render.filepath=str(out/'wood.png');scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.render.use_persistent_data=True
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
mat=bpy.data.materials.new('Finial inspection clay');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.24,.26,.29,1);bs.inputs['Roughness'].default_value=.32
set_material(scene,mat);scene.render.filepath=str(out/'neutral.png');bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'height_factor':args.height,'radial_factor':args.radius,'anchor':anchor,'changed_rings':list(range(107,len(a))),'receivers':report},indent=2))
print('FINIAL_TRIAL_DONE',flush=True)
