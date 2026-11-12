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
    try:
        runpy.run_path(str(path),run_name='__main__')
    except SystemExit as outcome:
        # The geometry-phase mission dispatcher is also a standalone CLI.
        # A successful CLI exit is equivalent to its normal return here.
        if script!='validate_mission.py' or outcome.code not in (0,None):raise
    print('BISHOP_CHECKPOINT_CHECK_PASSED',script,flush=True)
