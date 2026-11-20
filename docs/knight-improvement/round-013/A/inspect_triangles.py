from pathlib import Path
import sys,json,bpy,numpy as np
D=Path(__file__).resolve().parent
source=D/('native-repair.blend' if '--repair' in sys.argv else 'knight.blend')
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
o=bpy.context.scene.objects['Knight | continuous horse head and neck']
m=o.data;m.calc_loop_triangles()
v=np.empty((len(m.vertices),3),np.float32);m.vertices.foreach_get('co',v.ravel())
t=np.empty((len(m.loop_triangles),3),np.int32);m.loop_triangles.foreach_get('vertices',t.ravel())
a=np.linalg.norm(np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]),axis=1)
for i in np.flatnonzero(a<1e-10):
    fi=m.loop_triangles[int(i)].polygon_index;f=m.polygons[fi]
    print('SMALL',int(i),float(a[i]),t[i].tolist(),'face',fi,list(f.vertices),'coords',v[t[i]].tolist())
print('TINY_COUNT',int((a<1e-10).sum()),float(a.min()))
