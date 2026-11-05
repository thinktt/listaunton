from pathlib import Path
import json,sys
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/king/king-rebuilt.blend'),load_ui=False)
s=bpy.context.scene;cross=next(o for o in s.objects if o.type=='MESH' and 'cross' in o.name)
v=np.array([v.co[:] for v in cross.data.vertices]);f=[list(p.vertices) for p in cross.data.polygons]
out=ROOT/'build/king-mission/cross-inspection';out.mkdir(parents=True,exist_ok=True)
(out/'controls.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f,'matrix':list(x for row in cross.matrix_world for x in row),'smooth_faces':[p.use_smooth for p in cross.data.polygons],'uv_layers':[x.name for x in cross.data.uv_layers]},indent=2))
print(json.dumps({'name':cross.name,'vertices':len(v),'faces':len(f),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'modifiers':[(m.name,m.type) for m in cross.modifiers],'smooth_face_count':sum(p.use_smooth for p in cross.data.polygons),'unique_x':np.unique(np.round(v[:,0],5)).tolist(),'unique_y':np.unique(np.round(v[:,1],5)).tolist(),'unique_z':np.unique(np.round(v[:,2],5)).tolist()},indent=2))
