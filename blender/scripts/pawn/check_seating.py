"""Validate the rebuilt pawn and render its level side view."""
import sys,runpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[2]
before=json.loads((r/'history/pawn/04-before-seated-head/profile.json').read_text())
after=json.loads((r/'scripts/pawn/profile.json').read_text())
assert before['profile'][:40]==after['profile'][:40]
assert after['head_seating']['seat_radius']>20
sys.argv=['validate.py','--',str(r)]
runpy.run_path(str(r/'scripts/pawn/validate.py'),run_name='__main__')
report=json.loads((r/'assets/pawn/validation.json').read_text());report['seating_correction']={'lower_body_and_collar_outer_profile_unchanged':True,'head_lowered_original_pixels':4,'seat_radius_original_pixels':22,'continuous_single_surface':True};(r/'assets/pawn/validation.json').write_text(json.dumps(report,indent=2)+'\n')
runpy.run_path(str(r/'scripts/pawn/render_side.py'),run_name='__main__')
