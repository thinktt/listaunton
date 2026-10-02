import bpy,json,numpy as np
from pathlib import Path
root=Path(r'C:\Users\toby\Documents\Codex\2026-10-01\go-x20')
for name,path in [('white',root/'outputs/lichess-staunton-3d/White-Queen.webp'),('model',root/'outputs/queen-model/queen-reference-view.png')]:
 im=bpy.data.images.load(str(path)); w,h=im.size; a=np.array(im.pixels[:]).reshape(h,w,4)[::-1]
 print(name,w,h)
 for thresh in [.1,.5,.95]:
  y,x=np.where(a[:,:,3]>thresh);print(thresh,(int(x.min()),int(y.min()),int(x.max()),int(y.max())))
 print('row widths',[(y,int(np.count_nonzero(a[y,:,3]>.95))) for y in range(0,h,10)])
