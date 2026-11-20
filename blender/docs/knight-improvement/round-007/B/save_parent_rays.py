"""Record geometric normals and mirror directions while the accepted parent is staged."""
from pathlib import Path
import ast
import json
import sys
import numpy as np
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parents[2]/'scripts/knight'))
from probe_reflections import surface_probe
tree=ast.parse((OUT/'eyelid.py').read_text())
trials=next(ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and
            any(isinstance(t,ast.Name) and t.id=='TRIALS' for t in node.targets))
probe,source=surface_probe(OUT.parents[2]/'assets/knight')
hits={}
for span,dy,distance,energy in trials:
    if not span:continue
    for x in np.linspace(*span,10):
        y=np.interp(x,[476,488,504,518,530],[488,495,499,500,499])+dy
        key=f'{round(x)},{round(y)}'
        if key not in hits:hits[key]=probe(round(x),round(y))
(OUT/'parent-eyelid-rays.json').write_text(json.dumps({'source_sha256':source,'hits':hits},indent=2)+'\n')
