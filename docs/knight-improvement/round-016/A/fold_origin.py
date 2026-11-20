from pathlib import Path
import bpy,numpy as np,sys,json
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D));import sculpt
from geometry_qa import qamesh
func=sculpt.seat
for label in ['shape','seated']:
 s=sculpt.load('parent');sculpt.seat=func if label=='seated' else lambda s:0
 sculpt.carve(s);q=qamesh(s.objects['Knight | swept rounded mane'],bpy.context.evaluated_depsgraph_get());print(label,q['self_intersections'],flush=True)
