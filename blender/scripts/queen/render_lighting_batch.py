"""Run sequential independent lighting configs in one Blender process."""
from pathlib import Path
import argparse,runpy,sys
p=argparse.ArgumentParser();p.add_argument('configs',nargs='+')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
script=Path(__file__).with_name('place_lights.py')
for config in args.configs:
 sys.argv=['blender','--',config]
 runpy.run_path(str(script),run_name='__main__')
