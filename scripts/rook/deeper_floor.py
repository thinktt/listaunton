from pathlib import Path
import bpy,sys,json,hashlib,math,importlib.util
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'));from mission_trial import gpu
sys.path.insert(0,str(ROOT/'scripts/rook'));from rebuild_receivers import rebuild
spec=importlib.util.spec_from_file_location('rook_regions',ROOT/'scripts/rook/render_regions.py');rr=importlib.util.module_from_spec(spec);spec.loader.exec_module(rr)
source=ROOT/'history/rook-mission-037/models/rook/rook-rebuilt.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)=='a667b97122b3c188d93040279660ef947d91ba12b442442a71b4ba97a133e484'
for num,depth in [(39,6),(40,10)]:
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s);body=rr.closed_body(s);dz=depth/(280*math.cos(math.radians(54)))
 for v in body.data.vertices:
  row=v.index//128
  if row>=53:v.co.z-=dz
 body.data.update();bpy.context.view_layer.update();rebuild(s);checks=rr.validate(s)
 out=ROOT/f'build/rook-mission/{num:03d}-deeper-floor';out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
 # Saved-scene validation/render runs in a fresh Blender process to avoid stale subdivision caches.
 (out/'parameters.json').write_text(json.dumps({'source_sha256':sha(source),'model_sha256':sha(out/'rook.blend'),'lowered_control_rows':[53,58],'depth_profile_pixels':depth,'delta_z':-dz,'receiver_validation':checks,'unchanged':'outer control rows 0-52, merlons, camera, material, UV controls, lights'},indent=2)+'\n');print('DEEPER_FLOOR_DONE',num,flush=True)
