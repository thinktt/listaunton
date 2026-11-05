"""Measure glint ridge positions without altering reference pixels or registration."""
from pathlib import Path
from PIL import Image
import numpy as np,json
r=Path(__file__).resolve().parents[2]
ref=np.asarray(Image.open(r/'assets/queen/reference.png').convert('RGB'),dtype=float)/255
positions=np.load(r/'build/queen-mission/collar-surface-148/position.npy')
c=json.loads((r/'build/queen-mission/150-separated-collar-fills/parameters.json').read_text())
points=[]
for s in c['lights']:
 if s['name'].startswith('Collar crescent ') and 6<=int(s['name'].split()[-1])<=16:
  x,y=s['target_pixel'];values=[]
  for yy in range(y-16,y+17):
   z=positions[yy-350,x-290,2]
   if 2.97<z<3.16:
    # Small horizontal median suppresses individual wood pores.
    values.append((float(np.median(ref[yy,x-1:x+2].min(1))),yy,float(z)))
  brightness,peak,z=max(values)
  points.append({'name':s['name'],'old':[x,y],'ridge_pixel':[x,peak],'reference_min_rgb':brightness,'surface_z':z})
print(json.dumps(points,indent=2))
(r/'build/queen-mission/collar-surface-148/reference-ridge.json').write_text(json.dumps(points,indent=2)+'\n')
