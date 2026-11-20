"""Split edge-subdivision transition quads through their non-collinear diagonal."""
from pathlib import Path
from functools import lru_cache
import json,sys
import bpy,bmesh,numpy as np
sys.dont_write_bytecode=True;D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from mission_scene import sha,save_model,json_file
def repair(obj):
    m=obj.data;current,_=areas(m)
    suspect={m.loop_triangles[int(i)].polygon_index for i in np.flatnonzero(current<2e-9)}
    bm=bmesh.new();bm.from_mesh(m)
    fixed=[]
    for f in list(bm.faces):
        if len(f.verts)>4 and f.index in suspect:
            verts=list(f.verts);p=np.array([v.co[:] for v in verts]);normal=np.array(f.normal)
            @lru_cache(None)
            def best(lo,hi):
                if hi<=lo+1:return (float('inf'),[])
                highest=(-1,[])
                for mid in range(lo+1,hi):
                    area=float(np.cross(p[mid]-p[lo],p[hi]-p[lo])@normal)
                    if area<=0:continue
                    left,dl=best(lo,mid);right,dr=best(mid,hi)
                    quality=min(left,right,area)
                    if quality>highest[0]:
                        diagonals=([(lo,mid)] if mid-lo>1 else [])+([(mid,hi)] if hi-mid>1 else [])
                        highest=(quality,diagonals+dl+dr)
                return highest
            quality,diagonals=best(0,len(verts)-1)
            if quality<1e-9:raise RuntimeError('No well-conditioned triangulation')
            for aa,bb in diagonals:
                va,vb=verts[aa],verts[bb]
                face=next(q for q in va.link_faces if vb in q.verts and len(q.verts)>3)
                fixed.append([va.index,vb.index]);bmesh.utils.face_split(face,va,vb)
            continue
        if len(f.verts)!=4:continue
        p=np.array([list(v.co) for v in f.verts],float)
        area=np.linalg.norm(np.cross(np.roll(p,-1,0)-p,np.roll(p,-2,0)-p),axis=1)
        min02=min(area[0],area[2]);min13=min(area[1],area[3])
        if min(min02,min13)>.0001*max(area):continue
        # A locally subdivided triangle with one split edge has four
        # boundary vertices. Both triangles must use the middle vertex.
        i=0 if min02>min13 else 1
        if max(min02,min13)<1e-9:raise RuntimeError('Both diagonals are ill-conditioned')
        verts=list(f.verts);fixed.append([verts[i].index,verts[i+2].index])
        bmesh.utils.face_split(f,verts[i],verts[i+2])
    bm.to_mesh(m);bm.free();m.update()
    return fixed
def areas(m):
    m.calc_loop_triangles();xyz=np.empty((len(m.vertices),3),np.float32);m.vertices.foreach_get('co',xyz.ravel())
    tris=np.empty((len(m.loop_triangles),3),np.int32);m.loop_triangles.foreach_get('vertices',tris.ravel())
    return np.linalg.norm(np.cross(xyz[tris[:,1]]-xyz[tris[:,0]],xyz[tris[:,2]]-xyz[tris[:,0]]),axis=1),xyz
def check(source,output):
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;o=s.objects['Knight | continuous horse head and neck']
    before,points=areas(o.data);split=repair(o);after,new=areas(o.data)
    assert np.array_equal(points,new) and np.all(after>=1e-9)
    record={'withdrawn_digest':sha(source),'new_diagonals':len(split),'preserved_vertex_coordinates':True,'before_small_double_areas':int((before<1e-10).sum()),'after_small_double_areas':int((after<1e-10).sum()),'minimum_double_area':float(after.min())}
    s['knight_013A_boundary_repair']=json.dumps(record);save_model(s,output)
    bpy.ops.wm.open_mainfile(filepath=str(output),load_ui=False);m=bpy.context.scene.objects['Knight | continuous horse head and neck'].data
    a,p=areas(m);assert np.array_equal(points,p) and np.all(a>=1e-9)
    record['reopened_digest']=sha(output);json_file(D/'repair.json',record)
    k=json.loads((D/'parameters.json').read_bytes());k['model_sha256']=sha(output);k['native_diagonal_repair']=record;json_file(D/'native-repair-parameters.json',k)
    print(record)
if __name__=='__main__':check(D/'knight.blend',D/'native-repair.blend')
