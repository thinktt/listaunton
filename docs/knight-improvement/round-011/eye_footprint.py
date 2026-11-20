"""Project the boundary of the visible inner eye from the saved 54 degree camera."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
args=argparse.ArgumentParser()
args.add_argument('root',type=Path);args.add_argument('model',type=Path);args.add_argument('output',type=Path)
a=args.parse_args(sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(a.root.resolve()/'scripts/knight'))
from probe_carving import point_probe
bpy.ops.wm.open_mainfile(filepath=str(a.model.resolve()),load_ui=False)
probe=point_probe(bpy.context.scene)
columns=[]
for x in range(418,572):
    ys=[]
    for y in range(437,508):
        hit=probe(x+.5,y+.5)
        if hit and hit[1].endswith('near eye'):
            ys.append(y)
    if ys:
        if ys[-1]-ys[0]+1!=len(ys):
            raise ValueError(f'Disconnected visible eye in column {x}')
        columns.append([x,ys[0],ys[-1]])
if len(columns)<25:raise ValueError('Registered near eye not found')
info={'source_sha256':hashlib.sha256(a.model.read_bytes()).hexdigest(),'method':'First mesh hit at the center of each fixed-camera pixel. Reports only exposed eye insert, above the continuous carved cheek, within x418..571 and y437..507.','columns':columns,'visible_pixels':sum(hi-lo+1 for x,lo,hi in columns)}
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps(info,indent=2)+'\n')
print(len(columns),columns[0],columns[-1],info['visible_pixels'])
