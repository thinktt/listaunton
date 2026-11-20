"""Locate both sides of the hanging mane by visible surface ownership in the fixed camera."""
from pathlib import Path
import hashlib,json,sys
import bpy
root,model,out=map(Path,sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(root.resolve()/'scripts/knight'))
from probe_carving import point_probe
bpy.ops.wm.open_mainfile(filepath=str(model.resolve()),load_ui=False)
probe=point_probe(bpy.context.scene)
rows=[]
for y in range(412,800,3):
    xs=[]
    for x in range(155,410):
        hit=probe(x+.5,y+.5)
        if hit and hit[1]=='Knight | swept rounded mane':
            xs.append(x)
    if xs: rows.append([y,min(xs),max(xs)])
out.write_text(json.dumps({'model':hashlib.sha256(model.read_bytes()).hexdigest(),'rows':rows,
                           'method':'First visible surface in the registered camera, sampled once every three rows.'},indent=2)+'\n')
print(rows[::12])
