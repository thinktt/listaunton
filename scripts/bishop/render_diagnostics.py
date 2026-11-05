"""Render level head/whole profiles and a rear slit view without saving camera changes."""
from pathlib import Path
import argparse,json,math,sys
import bpy
from mathutils import Vector
p=argparse.ArgumentParser()
p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
p.add_argument('--model',default='models/bishop/bishop-rebuilt.blend')
p.add_argument('--out',default='assets/bishop')
p.add_argument('--head-only',action='store_true')
p.add_argument('--view',choices=['head-side','side-profile','rear-oblique'],help='Render one diagnostic view for an isolated trial.')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=args.root;out=root/args.out;out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/args.model))
scene=bpy.context.scene;camera=scene.camera
cfg=json.loads((root/'scripts/bishop/profile.json').read_text(encoding='utf-8'))
A=json.loads((root/'assets/bishop/original-alignment.json').read_text(encoding='utf-8'))
factor=1254/300/A['scale']/cfg['scale'];co=math.cos(math.radians(cfg['elevation']))
head_z=(cfg['y0']-72)*factor/co
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type=='CUDA'
 if any(dev.type=='CUDA' for dev in prefs.devices):scene.cycles.device='GPU'
except Exception:pass
views=[('head-side',(0,0,head_z),0,0,1.72,900)]
if not args.head_only:
 views += [('side-profile',(0,0,2.32),0,0,4.98,1000),('rear-oblique',(0,0,2.1),28,120,6,768)]
if args.view:views=[v for v in views if v[0]==args.view]
report={}
for name,target,e,az,scale,size in views:
 target=Vector(target);e=math.radians(e);az=math.radians(az)
 camera.location=target+Vector((10*math.sin(az)*math.cos(e),-10*math.cos(az)*math.cos(e),10*math.sin(e)))
 camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
 camera.scale=(1,1,1);camera.data.shift_x=0;camera.data.shift_y=0;camera.data.ortho_scale=scale
 scene.render.resolution_x=size;scene.render.resolution_y=size;scene.cycles.samples=24
 scene.render.filepath=str(out/(name+'.png'));bpy.context.view_layer.update()
 graph=bpy.context.evaluated_depsgraph_get();projection=camera.calc_matrix_camera(graph,x=size,y=size)
 report[name]={'elevationDegrees':math.degrees(e),'azimuthDegrees':math.degrees(az),'worldToCamera':[float(x) for row in camera.matrix_world.inverted() for x in row],'projectionMatrix':[float(x) for row in projection for x in row],'orthoScale':scale,'width':size,'height':size}
 bpy.ops.render.render(write_still=True)
(out/'diagnostic-cameras.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('DIAGNOSTIC_VIEWS_COMPLETE; saved blend camera left unchanged')
