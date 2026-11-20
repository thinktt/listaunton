from pathlib import Path
import bpy,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'));from mission_trial import gpu
source=ROOT/'build/rook-mission/024-shoulder-light/rook.blend';out=ROOT/'build/rook-mission/025-separated-edge-rig';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
receiver=bpy.data.collections.new('Old reflectors turret only');receiver.objects.link(next(o for o in s.objects if o.get('rook_render_receiver')=='rim'))
for name in ['Rook upper edge','Rook rim edge']:s.objects[name].light_linking.receiver_collection=receiver
s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'));bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False);s=bpy.context.scene;gpu(s);bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest(),'changed':'Old upper/rim reflectors restricted to turret rim receiver; rest unchanged from 024.'},indent=2)+'\n');print('SEPARATED_EDGE_RIG_DONE')
