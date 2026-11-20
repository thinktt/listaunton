"""Inspect the bilateral sections, seat and triangle crossings before freezing."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import load,proposal
from sections import sections
from native import verify_mane
for i in sys.argv[sys.argv.index('--')+1:]:
    s=load('parent.blend')
    if i.isdigit():proposal(s,int(i))
    q={'symmetry':sections(s),'mesh':verify_mane(s,False)}
    (D/f'geometry-{i}.json').write_text(json.dumps(q,indent=2)+'\n')
    print(i,{k:v for k,v in q['symmetry'].items() if k!='stations'},q['mesh'])
