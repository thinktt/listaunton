"""Refocus the small existing physical card along the carved lower orbital lip."""
import bpy
import numpy as np
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from probe_carving import point_probe
def focus(scene):
    ob=bpy.data.objects['Knight | continuous horse head and neck'];g=bpy.context.evaluated_depsgraph_get()
    ev=ob.evaluated_get(g);mesh=ev.to_mesh();mesh.calc_loop_triangles();mat=np.array(ob.matrix_world)
    vs=np.array([list(v.co) for v in mesh.vertices])@mat[:3,:3].T+mat[:3,3]
    tris=np.array([list(t.vertices) for t in mesh.loop_triangles])
    normals=np.array([[list(mesh.corner_normals[j].vector) for j in t.loops] for t in mesh.loop_triangles])
    tree=BVHTree.FromPolygons(vs.tolist(),tris.tolist(),all_triangles=True);ev.to_mesh_clear()
    probe=point_probe(scene);cam=np.array(scene.camera.matrix_world.to_quaternion()@Vector((0,0,1)))
    nominal=[(490,496),(493,497),(497,497),(500,498),(503,498),(506,499)]
    points=[];directions=[]
    for x,y in nominal:
        h=probe(x+.5,y+.5);assert h and h[1]==ob.name
        p=np.array(h[2]);_,_,i,_=tree.find_nearest(Vector(p));a,b,c=vs[tris[i]]
        u,v=np.linalg.lstsq(np.column_stack((b-a,c-a)),p-a,rcond=None)[0]
        n=np.array([1-u-v,u,v])@normals[i]@np.linalg.inv(mat[:3,:3]);n/=np.linalg.norm(n)
        points.append(p);directions.append(2*n.dot(cam)*n-cam)
    points=np.array(points);ray=np.array(directions)
    n=ray[2];mid=points[2]+.82*n
    lengths=((mid-points)@n)/(ray@n)
    on=points+lengths[:,None]*ray
    _,_,basis=np.linalg.svd(on-on.mean(0))
    axis=basis[0]-basis[0].dot(n)*n;axis/=np.linalg.norm(axis);cross=np.cross(n,axis)
    lamp=bpy.data.objects['Eye reflection lower'];lamp.location=Vector(mid)
    lamp.rotation_euler=Matrix(np.column_stack((axis,cross,n))).to_euler()
    lamp.data.shape='ELLIPSE';lamp.data.size=.16;lamp.data.size_y=.32;lamp.data.energy=.044
    lamp.data.spread=np.radians(13)
    bpy.context.view_layer.update()
    return {'name':lamp.name,'axes':[lamp.data.size,lamp.data.size_y],'watts':lamp.data.energy,
            'location':list(lamp.location),'rotation':list(lamp.rotation_euler),'receiver_points':nominal}
