from pathlib import Path
import argparse,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from focused_reflections import target
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
bpy.ops.wm.open_mainfile(filepath=str(ROOT/a.source),load_ui=False);s=bpy.context.scene;rows=[]
points=[(435,y) for y in range(1038,1059,2)]+[(x,y) for x,y in [(315,1008),(340,1020),(365,1030),(390,1037),(415,1042),(460,1048),(485,1049),(510,1048),(535,1046),(560,1041)]]
for x,y in points:
    ob,point,direction,normal=target(s,x,y);rows.append(dict(pixel=[x,y],receiver=ob.get('king_render_region'),point=list(point),normal=list(normal),reflection=list(direction)))
out=ROOT/a.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8');print(json.dumps(rows,indent=2))
