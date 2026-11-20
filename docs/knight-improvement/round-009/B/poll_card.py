"""Meter the existing poll reflector against the near crest after physical resculpting."""
from pathlib import Path
import json,sys
import bpy,numpy as np
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path[:0]=[str(OUT),str(ROOT/'scripts/knight')]
from carve import sculpt,DESIGNS,load,border
from mission_scene import configure_render,render,world_vertices
from probe_carving import point_probe

def smooth_samples(scene,obj,probe):
    """Interpolate the real, subdivided surface normals at visible camera rays."""
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh()
    mesh.calc_loop_triangles()
    matrix=np.asarray(obj.matrix_world)
    xyz=np.array([list(v.co) for v in mesh.vertices])@matrix[:3,:3].T+matrix[:3,3]
    tris=np.array([list(t.vertices) for t in mesh.loop_triangles])
    ns=np.array([[list(mesh.corner_normals[j].vector) for j in t.loops] for t in mesh.loop_triangles])
    tree=BVHTree.FromPolygons(xyz.tolist(),tris.tolist(),all_triangles=True)
    evaluated.to_mesh_clear()
    def query(x,y):
        h=probe(float(x)+.5,float(y)+.5)
        if not h or h[1]!=obj.name:return None
        q=np.asarray(h[2])
        _,_,idx,_=tree.find_nearest(Vector(q))
        p0,p1,p2=xyz[tris[idx]]
        u,v=np.linalg.lstsq(np.column_stack((p1-p0,p2-p0)),q-p0,rcond=None)[0]
        n=np.array([1-u-v,u,v])@ns[idx]@np.linalg.inv(matrix[:3,:3])
        return q,n/np.linalg.norm(n)
    return query

def meter(scene):
    mane=bpy.data.objects['Knight | swept rounded mane']
    locator=smooth_samples(scene,mane,point_probe(scene))
    rail=world_vertices(mane).reshape(13,64,3)[:6,39]
    def screen(pt):
        v=world_to_camera_view(scene,scene.camera,Vector(pt))
        return [v.x*1254,(1-v.y)*1254]
    p=np.array([screen(pt) for pt in rail])
    view=np.asarray(scene.camera.matrix_world.to_quaternion()@Vector((0,0,1)))
    samples=[]
    for x in range(300,459,6):
        y=np.interp(x,p[::-1,0],p[::-1,1])
        for offset in np.arange(-5,5.5,.5):
            h=locator(x,y+offset)
            if h:
                q,n=h
                samples.append({'pixel':[x,round(float(y+offset),2)],'offset':float(offset),
                                'position':q.tolist(),'reflected':(2*n.dot(view)*n-view).tolist()})
    return {'rail':p.tolist(),'samples':samples}

def fitted(scene,measurement,offset,energy,width,side_offset=0.):
    # The receiver sees one finite, real studio card. Fit its plane and extent
    # to the reflected rays of the physical bevel in world space.
    samples=[r for r in measurement['samples'] if r['offset']==offset and 313<=r['pixel'][0]<=454]
    pts=np.array([r['position'] for r in samples])
    dirs=np.array([r['reflected'] for r in samples])
    normal=np.median(dirs,axis=0)
    normal/=np.linalg.norm(normal)
    target=pts.mean(0)+1.75*normal
    w=((target-pts)@normal)/(dirs@normal)
    intersections=pts+w[:,None]*dirs
    mid=np.median(intersections,axis=0)
    _,_,v=np.linalg.svd(intersections-mid)
    along=v[0]-normal*v[0].dot(normal)
    along/=np.linalg.norm(along)
    across=np.cross(normal,along)
    loc=(intersections-mid)@along
    low,high=np.percentile(loc,[2,98])
    mid+=(low+high)*.5*along
    old=bpy.data.objects['Walnut | poll rear oval']
    old.location=Vector(mid+side_offset*across)
    old.rotation_euler=Matrix(np.column_stack((along,across,normal))).to_euler()
    old.data.size=float(np.clip((high-low)*1.23,.8,6))
    old.data.size_y=width
    old.data.energy=energy
    bpy.context.view_layer.update()
    return {'name':old.name,'location':list(old.location),'rotation':list(old.rotation_euler),
           'energy':energy,'size':[old.data.size,width],'native_rail_offset_px':offset,
           'receiver':str(old.light_linking.receiver_collection)}

def test():
    i=int(sys.argv[sys.argv.index('--design')+1])
    s=load('parent.blend')
    sculpt(s,DESIGNS[i])
    configure_render(s,64)
    border(s,(245,281,524,434))
    data=meter(s)
    (OUT/f'rail-{i}.json').write_text(json.dumps(data,indent=2)+'\n')
    lamp=bpy.data.objects['Walnut | poll rear oval']
    lamp.data.energy=0
    render(s,OUT/f'lamp-{i}-off.png')
    for idx,(off,w,watts) in enumerate([(-1,.105,90),(0,.105,90),(1,.105,90),(-2,.095,105),(2,.09,105),(.5,.17,125)]):
        info=fitted(s,data,off,watts,w)
        print(idx,info,flush=True)
        render(s,OUT/f'lamp-{i}-{idx}.png')
if __name__=='__main__':test()
