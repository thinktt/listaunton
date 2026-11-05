"""Run the accepted bishop's existing export, geometry, material and join checks."""
import runpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for script,arguments in [
    ('export_mission.py',[]),
    ('validate.py',[str(ROOT)]),
    ('validate_mission.py',[]),
    ('check_join_regression.py',[str(ROOT)]),
]:
    path=Path(__file__).with_name(script)
    print('BISHOP_CHECKPOINT_CHECK_BEGIN',script,flush=True)
    sys.argv=[str(path),'--',*arguments]
    runpy.run_path(str(path),run_name='__main__')
    print('BISHOP_CHECKPOINT_CHECK_PASSED',script,flush=True)
