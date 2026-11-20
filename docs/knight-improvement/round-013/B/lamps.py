"""Reposition the existing softbox around the physically carved support."""
from pathlib import Path
import json,math
import numpy as np,bpy
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from probe_carving import point_probe
D=Path(__file__).resolve().parent
def rays(s,upper=False):
    p=point_probe(s);ob=s.objects['Knight | '+('near eye' if upper else 'continuous horse head and neck')].evaluated_get(bpy.context.evaluated_depsgraph_get())
    m=np.asarray(ob.matrix_world);me=ob.to_mesh();me.calc_loop_triangles()
    co=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',co.ravel());co=co@m[:3,:3].T+m[:3,3]
    tris=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('vertices',tris.ravel())
    loops=np.empty_like(tris);me.loop_triangles.foreach_get('loops',loops.ravel())
    nm=np.empty((len(me.corner_normals),3),np.float32);me.corner_normals.foreach_get('vector',nm.ravel())
    tree=BVHTree.FromPolygons(co.tolist(),tris.tolist(),all_triangles=True)
    view=np.asarray(s.camera.matrix_world.to_quaternion()@Vector((0,0,1)))
    targets=np.array(json.loads((D/'lower-trace.json').read_text())['anchors'])
    if upper:targets=np.array([(488,470),(499,472),(506,474),(516,477),(526,482),(534,486)])
    result=[]
    for x in (range(489,535,2) if upper else range(478,531,3)):
        y=np.interp(x,targets[:,0],targets[:,1]);hit=p(x+.5,y+.5)
        if not hit or hit[1]!=ob.name:continue
        pos=np.asarray(hit[2]);_,_,i,_=tree.find_nearest(Vector(pos));v=co[tris[i]]
        a,b=np.linalg.lstsq(np.column_stack((v[1]-v[0],v[2]-v[0])),pos-v[0],rcond=None)[0]
        normal=np.array([1-a-b,a,b])@nm[loops[i]]@np.linalg.inv(m[:3,:3]);normal/=np.linalg.norm(normal)
        result.append((x,pos,2*normal.dot(view)*normal-view))
    ob.to_mesh_clear()
    return result
def fit(s,i,upper=False):
    bpy.context.view_layer.update();params={
        4:(.325,.83,.096,.065,21.,496),5:(.335,1.03,.117,.090,25.,495),6:(.395,1.12,.115,.100,27.,494),
        7:(.39,1.24,.144,.037,30.,502),8:(.39,1.30,.162,.048,32.,506),9:(.45,1.19,.151,.054,29.,505),
        10:(.50,1.25,.12,.155,70.,508),11:(.48,1.16,.11,.115,55.,507),12:(.49,1.15,.103,.125,59.,509),13:(.49,1.15,.103,.121,58.,509)}
    upper_params={7:(.38,1.07,.14,.047,34.,509),8:(.40,1.22,.17,.054,35.,515),9:(.40,1.25,.185,.070,35.,512),
        10:(.39,1.04,.165,.225,70.,509),11:(.40,.96,.145,.170,53.,511),12:(.43,1.05,.16,.22,55.,522),13:(.42,1.01,.155,.207,54.,518.5)}
    dist,spread_scale,minor,energy,spread,target=(upper_params if upper else params)[i]
    probe=rays(s,upper);x=np.array([q[0] for q in probe]);points=np.array([q[1] for q in probe]);dr=np.array([q[2] for q in probe])
    weights=np.exp(-((x-target)/15.)**2);weights/=weights.sum()
    n=weights@dr;n/=np.linalg.norm(n);pos=weights@points+dist*n
    k=((pos-points)@n)/(dr@n);plane=points+k[:,None]*dr
    center=weights@plane
    _,_,B=np.linalg.svd((plane-center)*np.sqrt(weights[:,None]));long=B[0]-B[0].dot(n)*n;long/=np.linalg.norm(long);short=np.cross(n,long)
    along=(plane-center)@long;major=np.clip((np.percentile(along,90)-np.percentile(along,10))*spread_scale+.07,.21,.62)
    ob=s.objects['Eye reflection '+('upper' if upper else 'lower')];ob.location=Vector(center);ob.rotation_euler=Matrix(np.column_stack((long,short,n))).to_euler()
    ob.data.shape='ELLIPSE';ob.data.size=float(major);ob.data.size_y=minor;ob.data.spread=math.radians(spread);ob.data.energy=energy
    print('Lower softbox',i,'dimensions',ob.data.size,minor,'watts',energy,'samples',len(x),flush=True)
    if i>=7 and not upper:fit(s,i,True)
