import bpy, bmesh, json, numpy as np
from pathlib import Path
root=Path(r'C:\Users\toby\Documents\Codex\2026-10-01\go-x20')
bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/queen-model/staunton-queen.blend'))
report=[]
for ob in bpy.data.collections['QUEEN - editable geometry'].objects:
 bm=bmesh.new();bm.from_mesh(ob.data)
 report.append({'object':ob.name,'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)})
 bm.free()
print(json.dumps(report,indent=2))
(root/'work/queen-mesh-check.json').write_text(json.dumps(report,indent=2))
for name,path in [('white',root/'outputs/lichess-staunton-3d/White-Queen.webp'),('model',root/'outputs/queen-model/queen-reference-view.png')]:
 im=bpy.data.images.load(str(path),check_existing=True);w,h=im.size;a=np.array(im.pixels[:]).reshape(h,w,4)[::-1]
 y,x=np.where(a[:,:,3]>.95); print(name,w,h,'bounds',[float(v)*300/w for v in (x.min(),y.min(),x.max(),y.max())])
