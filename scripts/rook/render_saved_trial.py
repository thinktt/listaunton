"""Validate receiver copies and render an isolated saved trial in a fresh process."""
from pathlib import Path
import bpy,sys,json,importlib.util
ROOT=Path(__file__).resolve().parents[2];variant=sys.argv[sys.argv.index('--')+1];out=ROOT/'build/rook-mission'/variant
sys.path.insert(0,str(ROOT/'scripts/king'));from mission_trial import gpu
spec=importlib.util.spec_from_file_location('rook_regions',ROOT/'scripts/rook/render_regions.py');rr=importlib.util.module_from_spec(spec);spec.loader.exec_module(rr)
bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False);s=bpy.context.scene;gpu(s);report=rr.validate(s)
bpy.ops.render.render(write_still=True)
(out/'saved-receiver-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('SAVED_TRIAL_RENDERED',variant)
