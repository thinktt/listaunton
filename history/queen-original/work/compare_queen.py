import bpy, numpy as np
from pathlib import Path
r=Path(r'C:\Users\toby\Documents\Codex\2026-10-01\go-x20')
arrays=[]
for p in [r/'outputs/lichess-staunton-3d/White-Queen.webp',r/'outputs/queen-model/queen-reference-view.png']:
 im=bpy.data.images.load(str(p));w,h=im.size
 a=np.array(im.pixels[:]).reshape(h,w,4)[::-1]
 # Numerical comparisons only, no image modification or output.
 a=a[(np.arange(300)*h/300).astype(int)[:,None],(np.arange(300)*w/300).astype(int)[None,:],3]>.95
 arrays.append(a)
for y in range(10,261,5):
 vals=[]
 for a in arrays:
  x=np.where(a[y])[0]; vals.append((int(x.min()),int(x.max()),len(x)) if len(x) else (0,0,0))
 print(y,vals)
a,b=arrays;print('silhouette IoU',np.count_nonzero(a&b)/np.count_nonzero(a|b))
