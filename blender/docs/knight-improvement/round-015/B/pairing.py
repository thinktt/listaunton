"""Inspect matching native points on the left and right eye shells."""
from pathlib import Path
import sys,numpy as np
from mathutils.kdtree import KDTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import load,rest_coords,world_vertices,pose
s=load('parent.blend')
x,y=[rest_coords(world_vertices(s.objects['Knight | '+n+' eye']),pose(s)) for n in ('near','far')]
x[:,1]*=-1
t=KDTree(len(x))
for i,q in enumerate(x):t.insert(q,i)
t.balance();hits=[t.find(q) for q in y]
ids=np.array([r[1] for r in hits])
print('indexed',np.percentile(np.linalg.norm(x-y,axis=1),[0,10,50,90,100]))
print('nearest',np.percentile([r[2] for r in hits],[0,10,50,90,100]),'uniques',len(np.unique(ids)),len(y))
f=s.objects['Knight | far eye'].data;f.calc_loop_triangles();tris=np.array([i.vertices[:] for i in f.loop_triangles]);nf=s.objects['Knight | near eye'].data;nf.calc_loop_triangles()
faces={tuple(sorted(i.vertices[:])) for i in nf.loop_triangles}
print('topol matches under natural direct and nearest mapping',sum(tuple(sorted(i)) in faces for i in tris),sum(tuple(sorted(i)) in faces for i in ids[tris]),len(tris))
print('near and far examples',np.round(x[[100,500,1000,4000]],4),np.round(y[[100,500,1000,4000]],4))
for m in [nf,f]:
    print('uv:',[(l.name,np.round(np.asarray(l.data[300].uv),4)) for l in m.uv_layers],len(m.polygons),len(m.vertices))
    print('first co',np.round(m.vertices[8].co,3))
def charts(m):
    li=np.empty(len(m.loops),np.int32);m.loops.foreach_get('vertex_index',li)
    uv=np.empty((len(li),2),np.float32);m.uv_layers['UVMap'].data.foreach_get('uv',uv.ravel())
    count=np.bincount(li);theta=np.angle(np.bincount(li,weights=np.cos(2*np.pi*uv[:,0]))+1j*np.bincount(li,weights=np.sin(2*np.pi*uv[:,0])))/(2*np.pi)
    return np.c_[theta%1,np.bincount(li,weights=uv[:,1])/count]
a=charts(nf);b=charts(f)
for sgu in [1,-1]:
    for sgv in [1,-1]:
        du=(a[ids,0]-sgu*b[:,0])%1;dv=np.abs(a[ids,1]-(b[:,1] if sgv==1 else 1-b[:,1]))
        bins,_=np.histogram(du,bins=np.arange(130)/128-1/256)
        print(sgu,sgv,'mode of U offset',np.argmax(bins)/128,'hits',bins.max(),'median V error',np.median(dv))
print('rows',np.unique(np.rint(a[:,1]*1024),return_counts=True))
