from pathlib import Path
import bpy,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
source=ROOT/'build/rook-mission/034-measured-rim/rook.blend'
for number,power in [(35,1500),(36,4500)]:
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
 for o in s.objects:
  if o.type=='LIGHT' and o.name.startswith('Measured rim '):o.data.energy=power
 out=ROOT/f'build/rook-mission/{number:03d}-rim-strength';out.mkdir(parents=True,exist_ok=True)
 s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
 bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False);gpu(bpy.context.scene);bpy.ops.render.render(write_still=True)
 (out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'watts_each':power,'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest()},indent=2)+'\n')
 print('RIM_STRENGTH_DONE',number,flush=True)
