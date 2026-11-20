"""Validate the intentional floor-depth edit against checkpoint 037."""
from pathlib import Path
import bpy,bmesh,numpy as np,sys,json,hashlib,importlib.util,math
ROOT=Path(__file__).resolve().parents[2];variant=sys.argv[sys.argv.index('--')+1];out=ROOT/'build/rook-mission'/variant
spec=importlib.util.spec_from_file_location('rook_regions',ROOT/'scripts/rook/render_regions.py');rr=importlib.util.module_from_spec(spec);spec.loader.exec_module(rr)
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);s=bpy.context.scene;parts={};dg=bpy.context.evaluated_depsgraph_get()
 for ob in s.objects:
  if ob.type!='MESH' or ob.get('rook_render_receiver'):continue
  ev=ob.evaluated_get(dg);m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m);assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0
  parts[ob.name]={'co':np.array([v.co[:] for v in ob.data.vertices]),'uv':{u.name:np.array([v.uv[:] for v in u.data]) for u in ob.data.uv_layers},'volume':bm.calc_volume(signed=True)};bm.free();ev.to_mesh_clear()
 c=s.camera;camera=(list(map(list,c.matrix_world)),c.data.ortho_scale,c.data.shift_x,c.data.shift_y,s.render.resolution_x,s.render.resolution_y)
 return parts,camera
base=ROOT/'history/rook-mission-037/models/rook/rook-rebuilt.blend';before,cam=snapshot(base);after,newcam=snapshot(out/'rook.blend');assert cam==newcam;params=json.loads((out/'parameters.json').read_text());depth=float(sys.argv[sys.argv.index('--depth')+1]) if '--depth' in sys.argv else params.get('depth_profile_pixels',0);delta=params.get('delta_z',-depth/(280*math.cos(math.radians(54))));errors={}
for name,a in before.items():
 b=after[name];expected=a['co'].copy()
 if 'continuous turned' in name:expected[53*128:,2]+=delta
 err=float(np.abs(expected-b['co']).max());assert err<2e-7;errors[name]=err
 for key,uv in a['uv'].items():assert np.array_equal(uv,b['uv'][key]),(name,key)
report={'camera_exact':True,'only_control_rows_53_to_58_lowered':True,'control_position_max_errors':errors,'control_uvs_exact':True,'closed_positive_components':len(after),'volumes':{n:a['volume'] for n,a in after.items()},'receivers':rr.validate(bpy.context.scene),'source_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'trial_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest()};(out/'geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('FLOOR_GEOMETRY_VALIDATED',json.dumps(report))
