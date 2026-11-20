"""Read-only eye/skin triangle crossings and solid-ray intervals from evaluated meshes."""
from pathlib import Path
import sys,json,hashlib,math
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=Path(__file__).resolve().parent;pitch=.003;eps=1e-5
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mesh(obj,graph,R,offset):
    ev=obj.evaluated_get(graph);m=ev.to_mesh();m.calc_loop_triangles()
    local=np.empty((len(m.vertices),3),np.float32);m.vertices.foreach_get('co',local.ravel())
    T=np.array(ev.matrix_world);world=local@T[:3,:3].T+T[:3,3];p=(world-offset)@R
    tri=np.empty((len(m.loop_triangles),3),np.int32);m.loop_triangles.foreach_get('vertices',tri.ravel())
    tree=BVHTree.FromPolygons(p.tolist(),tri.tolist(),all_triangles=True)
    ev.to_mesh_clear()
    return p,tri,tree,world
def intervals(tree,start,direction):
    origin=Vector(start);d=Vector(direction);pts=[]
    while True:
        pt=tree.ray_cast(origin,d)[0]
        if pt is None:break
        t=float((pt-Vector(start)).dot(d))
        if not pts or t-pts[-1]>2e-6:pts.append(t)
        origin=pt+1.5e-6*d
        if len(pts)>32:raise ValueError('Unexpected layered surface')
    return pts
def crossing(p,q):
    """Strict segment/triangle intersections, rejecting coplanar and point-only contacts."""
    ans=[]
    for a,b in [(p,q),(q,p)]:
        w0,w1,w2=b
        e1=w1-w0;e2=w2-w0;normal=np.cross(e1,e2)
        for v,w in zip(a,np.roll(a,-1,axis=0)):
            dv,dw=(v-w0)@normal,(w-w0)@normal
            if dv*dw>=0:continue
            pt=v+dv/(dv-dw)*(w-v)
            aa,bb=np.linalg.lstsq(np.column_stack((e1,e2)),pt-w0,rcond=None)[0]
            if min(aa,bb,1-aa-bb)>1e-9:ans.append(pt)
    if len(ans)<2:return 0
    return float(max(np.linalg.norm(a-b) for i,a in enumerate(ans) for b in ans[i+1:]))
def aperture(skin,eye,side):
    P,T,et,world=eye;Q,F,st,_=skin
    pairs=st.overlap(et)
    lengths=np.array([crossing(Q[F[a]],P[T[b]]) for a,b in pairs])
    axis=np.array([1.,-.76])/np.hypot(1,.76);up=np.array([-axis[1],axis[0]]);center=np.array([.412,4.158])
    co=P[:,[0,2]]-center;uv=np.column_stack((co@axis,co@up))
    lo=np.floor(uv.min(0)/pitch).astype(int)-1;hi=np.ceil(uv.max(0)/pitch).astype(int)+1
    data=[];odd_eye=odd_skin=multieye=0;direction=(0,-side,0)
    for i in range(lo[0],hi[0]+1):
        for j in range(lo[1],hi[1]+1):
            u,v=(i+.37)*pitch,(j+.53)*pitch;x,z=center+u*axis+v*up;start=(x,side*3,z)
            hits=intervals(et,start,direction)
            if not hits:continue
            if len(hits)%2:odd_eye+=1;continue
            multieye+=len(hits)>2
            sk=intervals(st,start,direction)
            if len(sk)%2:odd_skin+=1;continue
            eye_i=list(zip(hits[::2],hits[1::2]));head_i=list(zip(sk[::2],sk[1::2]))
            thick=sum(b-a for a,b in eye_i)
            emb=sum(max(0,min(b,d)-max(a,c)) for a,b in eye_i for c,d in head_i)
            if not sk:raise RuntimeError('No skull along an eye ray')
            out=sum(max(0,min(b,sk[0])-a) for a,b in eye_i)
            gap=max(0,sk[0]-hits[-1])
            data.append([u,v,hits[0],hits[-1],sk[0],thick,emb,out,gap])
    a=np.array(data);w=a[:,5];inside=a[:,6];outside=a[:,7];gap=a[:,8];both=(inside>eps)&(outside>eps)
    inside_vol=float(inside.sum()*pitch*pitch);total=float(w.sum()*pitch*pitch)
    # Sign of vertex location is determined by two outward ray-parity checks.
    distances=[];unresolved=0
    directions=[np.array([.187,side,.271]),np.array([-.293,side,.127])]
    for point in P:
        ds=float(st.find_nearest(Vector(point))[3])
        if ds<eps:distances.append(0);continue
        signs=[len(intervals(st,point,d/np.linalg.norm(d)))%2 for d in directions]
        if signs[0]!=signs[1]:unresolved+=1;signs.append(len(intervals(st,point,(0,side,0)))%2)
        inside_vertex=sum(signs)>len(signs)/2
        distances.append(-ds if inside_vertex else ds)
    dist=np.asarray(distances)
    def sample(row):return {k:round(float(t),6) for k,t in zip(['u','v','eye_enter','eye_exit','skull_enter','eye_thickness','embedded','outward_exposure','gap_before_skull'],row)}
    example=a[np.argmin((a[:,0]-.0)**2+(a[:,1]-.04)**2)]
    strong=a[np.argmax(np.minimum(inside,outside))]
    return {'eye_vertices':len(P),'eye_triangles':len(T),'bvh_candidate_triangle_pairs':len(pairs),
        'transverse_segment_pairs_length_gt_1e-6':int((lengths>1e-6).sum()),'total_crossing_length':float(lengths[lengths>1e-6].sum()),
        'inside_vertices':int((dist<0).sum()),'outside_vertices':int((dist>0).sum()),'boundary_vertices_at_1e-5':int((dist==0).sum()),
        'vertex_parity_disagreements_resolved':unresolved,'deepest_vertex_inside':float(-dist.min()),'farthest_vertex_outside':float(dist.max()),
        'ray_pitch':pitch,'valid_eye_rays':len(a),'odd_eye_rays_excluded':odd_eye,'odd_skull_rays_excluded':odd_skin,'rays_with_multiple_eye_intervals':int(multieye),
        'rays_intersecting_eye_and_skull_material':int((inside>eps).sum()),'rays_with_outward_eye_exposure':int((outside>eps).sum()),'rays_simultaneously_buried_and_exposed':int(both.sum()),
        'rays_with_eye_entirely_ahead_of_skull':int((gap>eps).sum()),'maximum_gap_if_any':float(gap.max()),'maximum_embedded_thickness':float(inside.max()),'maximum_exposed_thickness':float(outside.max()),
        'estimated_eye_volume':total,'estimated_eye_inside_skull_volume':inside_vol,'inside_fraction':inside_vol/total,'sample_at_chart_center':sample(example),'sample_with_balanced_overlap_and_exposure':sample(strong)}
def main():
    model=D/'knight.blend';h=digest(model)
    bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);s=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get()
    p=json.loads(s['knight_mission_pose']);t=math.radians(p['twist_degrees']);R=np.array([[math.cos(t),-math.sin(t),0],[math.sin(t),math.cos(t),0],[0,0,1]])
    off=np.array([p['dx'],p['dy'],0])
    hobj=s.objects['Knight | continuous horse head and neck'];skin=mesh(hobj,dep,R,off)
    old_tree=BVHTree.FromObject(hobj,dep);result={}
    for side,name in [(-1,'near'),(1,'far')]:
        obj=s.objects['Knight | '+name+' eye'];eye=mesh(obj,dep,R,off)
        info=aperture(skin,eye,side);o=obj.matrix_world.translation;center=(eye[3].min(0)+eye[3].max(0))*.5
        hit=old_tree.ray_cast((obj.location.x,side*2,obj.location.z),(0,-side,0))[0];old_dist=abs(obj.location.y-hit.y)
        info['legacy_origin_world']=list(o);info['eye_world_bbox_midpoint']=center.tolist();info['origin_to_bbox_midpoint']=float(np.linalg.norm(np.array(o)-center))
        info['legacy_origin_distance']=old_dist;info['legacy_half_dimension_y']=obj.dimensions.y/2;info['legacy_test_passes']=old_dist<obj.dimensions.y/2
        result[name]=info;print(name,info,flush=True)
    assert digest(model)==h
    (D/'release-eye-seating.json').write_text(json.dumps({'source_sha256':h,'measured_skull_triangles':len(skin[1]),'method':'Evaluated meshes transformed into one rigid head frame. BVH pair tests require positive-length transverse triangle intersections. Outward side rays traverse the entire eye and skull and pair every hit to form solid intervals. Grid volumes are estimates. Signed vertex distances use nearest triangle distance and ray parity. The outside-only columns, if present, describe local air in the carved cavity; a positive embedded volume and true surface crossings establish attachment elsewhere.','sides':result},indent=2)+'\n')
if __name__=='__main__':main()
