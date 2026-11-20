"""Project the actual visible ear onto the registered reference for shape review."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy

p=argparse.ArgumentParser()
p.add_argument('root',type=Path);p.add_argument('model',type=Path);p.add_argument('output',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(a.root.resolve()/'scripts/knight'))
from probe_carving import point_probe
bpy.ops.wm.open_mainfile(filepath=str(a.model.resolve()),load_ui=False)
hit=point_probe(bpy.context.scene)
points=[]
for x in range(205,599,3):
    ys=[]
    for y in range(346,480,2):
        v=hit(x+.5,y+.5)
        if v and v[1].endswith('near swept ear'):ys.append(y)
    if ys:points.append([x,min(ys),max(ys)])
if len(points)<30:raise RuntimeError('The near ear was not located in the registered camera.')
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps({'model':hashlib.sha256(a.model.read_bytes()).hexdigest(),'method':'Frontmost evaluated surface at fixed camera pixel centers. Column spacing 3 px, row spacing 2 px.','visible_ear_columns':points},indent=2)+'\n')
print('Ear footprint',points[0],points[-1],len(points))
