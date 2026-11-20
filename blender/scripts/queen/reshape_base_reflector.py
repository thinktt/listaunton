"""Refine the real base reflector from measured highlight displacement and extent."""
from pathlib import Path
import sys,json,hashlib,argparse
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
p=argparse.ArgumentParser();p.add_argument('--variant',default='121-rectified-base-panel');p.add_argument('--source',default='models/queen/queen-rebuilt.blend');p.add_argument('--dx',type=float,default=-6);p.add_argument('--dy',type=float,default=-11);p.add_argument('--width',type=float,default=.88);p.add_argument('--height',type=float,default=1.25);p.add_argument('--gain',type=float,default=1.1);args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/args.source;digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest=='2cb513a71cf36e6bbaa3619b95cc53208e1245f9dbefebc745470e582fc11a9b'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;obj=editable_mesh(s);cam=s.camera;cfg=json.loads(s['mission_material_config']);spec=next(a for a in cfg['lights'] if a['name']=='Display fitted base-key');light=bpy.data.objects[spec['name']]
for m in obj.modifiers:
 if m.type=='SUBSURF':m.levels=m.render_levels
bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(graph);mesh=ev.to_mesh();mesh.calc_loop_triangles();v=np.array([tuple(v.co) for v in mesh.vertices]);n=np.array([tuple(v.normal) for v in mesh.vertices]);tri=np.array([tuple(t.vertices) for t in mesh.loop_triangles]);tree=BVHTree.FromPolygons(v.tolist(),tri.tolist(),all_triangles=True)
W=s.render.resolution_x;H=s.render.resolution_y;matrix=cam.calc_matrix_camera(graph,x=W,y=H)@cam.matrix_world.inverted();inv=matrix.inverted();view=cam.matrix_world.to_3x3()@Vector((0,0,1));view.normalize();target=Vector(spec['target']);screen=matrix@Vector((*target,1));px=(screen.x/screen.w+1)*W/2;py=(1-screen.y/screen.w)*H/2;x=px+args.dx;y=py+args.dy
near=inv@Vector((2*x/W-1,1-2*y/H,-1,1));near=near.xyz/near.w;loc,_,idx,_=tree.ray_cast(near,-view,100);assert loc is not None;indices=tri[idx];a,b,c=v[indices];uv=np.linalg.lstsq(np.column_stack((b-a,c-a)),np.array(loc)-a,rcond=None)[0];normal=Vector(n[indices[0]]*(1-sum(uv))+n[indices[1]]*uv[0]+n[indices[2]]*uv[1]);normal.normalize();direction=2*normal.dot(view)*normal-view;distance=(Vector(spec['position'])-target).length;position=loc+direction*distance
light.location=position;light.rotation_euler=(loc-position).to_track_quat('-Z','Y').to_euler();light.data.size*=args.width;light.data.size_y*=args.height;light.data.energy*=args.gain
spec.update(position=list(position),target=list(loc),target_pixel=[x,y],size=light.data.size,size_y=light.data.size_y,energy=light.data.energy);cfg['variant']=args.variant;cfg['base_reflector_refinement']={'source_sha256':digest,'original_target_pixel':[px,py],'pixel_offset':[args.dx,args.dy],'size_factors':[args.width,args.height],'gain':args.gain,'method':'Move the physical rectangular emitter along a reflected view ray, narrowing and lengthening it according to measured reference glint moments. No geometry or material change.'};s['mission_material_config']=json.dumps(cfg);s['mission_variant']=args.variant;ev.to_mesh_clear()
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(parents=True,exist_ok=True);s.cycles.samples=128;s.cycles.use_denoising=True;s.render.use_persistent_data=True;s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2));print('BASE_PANEL_DONE',flush=True)
