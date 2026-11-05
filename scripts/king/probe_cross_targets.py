"""Probe true surface normals at cross reflection targets; run in Blender."""
from pathlib import Path
import argparse,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from focused_reflections import target
parser=argparse.ArgumentParser();parser.add_argument('source',nargs='?',default='models/king/king-rebuilt.blend')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(ROOT/args.source),load_ui=False)
rows=[]
for x,y in [(505,44),(505,48),(505,52),(505,56),(480,53),(530,53),(440,85),(570,85)]:
    ob,p,d,n=target(bpy.context.scene,x,y);rows.append(dict(pixel=[x,y],point=list(p),normal=list(n),object=ob.name))
print(json.dumps(rows,indent=2))
