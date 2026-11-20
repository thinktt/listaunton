"""Adjust two existing fixed studio cards to the new carved surfaces."""
import bpy
import numpy as np
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
from probe_carving import point_probe
from mission_scene import world_vertices


def smooth_samples(scene,obj,probe):
    dg=bpy.context.evaluated_depsgraph_get()
    ev=obj.evaluated_get(dg);mesh=ev.to_mesh();mesh.calc_loop_triangles()
    mat=np.asarray(obj.matrix_world)
    vs=np.array([list(v.co) for v in mesh.vertices])@mat[:3,:3].T+mat[:3,3]
    tris=np.array([list(t.vertices) for t in mesh.loop_triangles])
    ns=np.array([[list(mesh.corner_normals[j].vector) for j in t.loops] for t in mesh.loop_triangles])
    tree=BVHTree.FromPolygons(vs.tolist(),tris.tolist(),all_triangles=True)
    ev.to_mesh_clear()
    def hit(x,y):
        h=probe(float(x)+.5,float(y)+.5)
        if not h or h[1]!=obj.name:return None
        q=np.asarray(h[2]);_,_,i,_=tree.find_nearest(Vector(q))
        a,b,c=vs[tris[i]]
        u,v=np.linalg.lstsq(np.column_stack((b-a,c-a)),q-a,rcond=None)[0]
        normal=np.array([1-u-v,u,v])@ns[i]@np.linalg.inv(mat[:3,:3])
        normal/=np.linalg.norm(normal)
        return q,normal
    return hit


def focus_oval(scene,mane):
    probe=point_probe(scene);hit=smooth_samples(scene,mane,probe)
    camera=np.asarray(scene.camera.matrix_world.to_quaternion()@Vector((0,0,1)))
    old=bpy.data.objects['Walnut | poll rear oval']
    def reflect(n):return 2*n.dot(camera)*n-camera

    # Search the actual bevel at its projection. Locate the middle of the
    # normal transition so a long softbox illuminates the turned edge itself.
    near_rail=world_vertices(mane).reshape(13,64,3)[:6,39,:]
    p=np.array([[v.x*1254,(1-v.y)*1254] for pt in near_rail
                for v in [world_to_camera_view(scene,scene.camera,Vector(pt))]])
    results=[]
    for x in range(298,472,7):
        y=round(float(np.interp(x,p[::-1,0],p[::-1,1])))
        points=[(y+i,hit(x,y+i)) for i in range(-13,14)]
        points=[(k,h) for k,h in points if h is not None]
        if len(points)<13:continue
        ns=np.array([h[1] for _,h in points]);ys=np.array([k for k,_ in points])
        curv=np.linalg.norm(np.gradient(ns,axis=0),axis=1)
        use=abs(ys-y)<=7
        if not any(use):continue
        idx=np.argmax(np.where(use,curv,-1))
        yc,q,n=points[idx][0],*points[idx][1]
        results.append((x,yc,q,reflect(n)))
    if len(results)<12:raise ValueError('Too few samples on the bevel')
    # The fixed card is a real elliptical area source in a world-space plane.
    points=np.array([h[2] for h in results]);dirs=np.array([h[3] for h in results])
    plane_n=np.median(dirs,axis=0);plane_n/=np.linalg.norm(plane_n)
    plane_point=points.mean(0)+1.5*plane_n
    w=((plane_point-points)@plane_n)/(dirs@plane_n)
    on_plane=points+w[:,None]*dirs
    center=np.median(on_plane,axis=0)
    _,_,axes=np.linalg.svd(on_plane-center)
    along=axes[0]-plane_n*axes[0].dot(plane_n);along/=np.linalg.norm(along)
    across=np.cross(plane_n,along)
    lengths=(on_plane-center)@along
    low,high=np.percentile(lengths,[3,97]);center+=(low+high)*.5*along
    old.location=Vector(center+.16*across);old.rotation_euler=Matrix(np.column_stack((along,across,plane_n))).to_euler()
    old.data.size=float((high-low)*1.32)
    old.data.size_y=.08;old.data.energy=148.
    lid=bpy.data.objects['Eye reflection lower']
    skin=bpy.data.objects['Knight | continuous horse head and neck']
    skin_hit=smooth_samples(scene,skin,probe)
    q,n=skin_hit(498,491)
    ray=reflect(n)
    lid.location=Vector(q+.83*ray);lid.rotation_euler=(-Vector(ray)).to_track_quat('-Z','Y').to_euler()
    lid.data.energy=.009;lid.data.size=.14;lid.data.size_y=.064
    bpy.context.view_layer.update()
    return {'poll':{'name':old.name,'location':list(old.location),'rotation':list(old.rotation_euler),
                    'axes':[old.data.size,old.data.size_y],'watts':old.data.energy,
                    'rail_samples':[[r[0],r[1]] for r in results]},
            'lower_eyelid':{'name':lid.name,'location':list(lid.location),'watts':lid.data.energy,
                            'receiver_pixel':[498,491],'axes':[lid.data.size,lid.data.size_y]}}
