"""Extend and seat the lower mane, fitting registered outlines on its subdivided surface."""
from pathlib import Path
import json
import sys
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'scripts/knight'));sys.path.insert(0,str(OUT))
from mission_scene import configure_render,json_file,save_model,sha,world_vertices,visible_meshes
from mission_pose import bend_weight
from refine_eye import apply_world
from diagnostic_views import pictures

PARENT='6d06b1ca5d781bcca921e5745f10504ab1113aae983571704a979964a934c177'


def rings(last):
    return np.array([0.]*(13-len(last))+last)


def controls(points,twist):
    """Offsets in the inherited sagittal frame, paired across every closed ring."""
    old=points.reshape(13,64,3)
    phases=np.arange(64)*2*np.pi/64
    outer=(1-np.cos(phases))*.5
    weight=bend_weight(old.mean(1)[:,2])
    yaw=np.radians(twist)*weight
    rear=np.array([-np.cos(yaw),-np.sin(yaw),np.zeros(13)]).T[:,None,:]
    lateral=np.array([-np.sin(yaw),np.cos(yaw),np.zeros(13)]).T[:,None,:]
    radial=.23+.77*outer
    back=rings([.04,.37,.84,1,.30])[:,None]*radial
    back[-1]=.30 # Preserve the small end cap.
    late=rings([0,.08,.39,1,.03])[:,None]*radial
    late[-1]=.03
    starting=rings([.09,1,.56,.06,0,0])[:,None]*radial
    width=rings([0,.27,.78,1,.16])[:,None]*np.sin(phases)[None,:]
    drop=rings([.025,.22,.62,.92,1])
    middle=rings([.025,.60,1,.38,0])
    zaxis=np.array([0.,0.,-1.])
    stretch=lambda w:np.broadcast_to(w[:,None,None]*zaxis,(13,64,3)).copy()
    # Rearward extension, lower seating, symmetric widening, initial draw-in,
    # then extra length through the shoulder of the lower sweep.
    return np.array([back[:,:,None]*rear,stretch(drop),width[:,:,None]*lateral,
                    -starting[:,:,None]*rear,stretch(middle),late[:,:,None]*rear]).reshape(6,-1,3)


def evaluated(obj,graph,combined):
    ev=obj.evaluated_get(graph);mesh=ev.to_mesh();mesh.calc_loop_triangles()
    xyz=np.empty((len(mesh.vertices),3),np.float32);mesh.vertices.foreach_get('co',xyz.ravel())
    tris=np.empty((len(mesh.loop_triangles),3),np.int32);mesh.loop_triangles.foreach_get('vertices',tris.ravel())
    mat=np.asarray(obj.matrix_world)
    xyz=xyz@mat[:3,:3].T+mat[:3,3]
    uv=(xyz@combined[:2,:3].T+combined[:2,3])*[627,-627]+627
    ev.to_mesh_clear()
    return uv.astype(np.float32),tris


def adjacency(tris):
    edges=np.sort(np.concatenate((tris[:,[0,1]],tris[:,[1,2]],tris[:,[2,0]])),axis=1)
    faces=np.tile(np.arange(len(tris)),3)
    order=np.lexsort((edges[:,1],edges[:,0]))
    edge=edges[order];face=faces[order]
    pairs=np.flatnonzero(np.all(edge[:-1]==edge[1:],axis=1))
    return edge[pairs],face[pairs],face[pairs+1]


def left(points,tris,adj,ys):
    t=points[tris];p=t[:,1]-t[:,0];q=t[:,2]-t[:,0]
    front=p[:,0]*q[:,1]>=p[:,1]*q[:,0]
    edge,face1,face2=adj
    start,end=points[edge[front[face1]!=front[face2]]].transpose(1,0,2)
    sy=start[:,1,None];ey=end[:,1,None];sx=start[:,0,None]
    on=(np.minimum(sy,ey)<=ys)&(np.maximum(sy,ey)>ys)
    cross=sx+(ys-sy)*(end[:,0,None]-sx)/np.where(abs(ey-sy)<1e-6,1.,ey-sy)
    return np.where(on,cross,3000).min(0)


def depth_into(tree,obj,world):
    inv=obj.matrix_world.inverted();loc,normal,_,distance=tree.find_nearest(inv@Vector(world))
    return -float((inv@Vector(world)-loc).dot(normal))


def main():
    assert sha(OUT/'parent.blend')==PARENT
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'parent.blend'),load_ui=False)
    scene=bpy.context.scene;cam=scene.camera;graph=bpy.context.evaluated_depsgraph_get()
    combined=np.asarray(cam.calc_matrix_camera(graph,x=1254,y=1254))@np.linalg.inv(np.asarray(cam.matrix_world))
    mane=bpy.data.objects['Knight | swept rounded mane']
    neck=bpy.data.objects['Knight | continuous horse head and neck']
    ped=bpy.data.objects['Knight | turned pedestal']
    pose=json.loads(scene['knight_mission_pose'])
    old=world_vertices(mane);modes=controls(old,pose['twist_degrees'])
    data=json.loads((OUT/'observations.json').read_text())
    rows=np.array(data['rows']);ys=rows+.5
    refs=np.stack((data['black_2'],data['sprite'])).astype(float)
    obs=np.mean(refs,axis=0)
    base,tris=evaluated(mane,graph,combined);adj=adjacency(tris)
    projected=[]
    for mode in modes:
        apply_world(mane,old+.25*mode);bpy.context.view_layer.update()
        val,_=evaluated(mane,graph,combined);projected.append((val-base)/.25)
    apply_world(mane,old);bpy.context.view_layer.update()
    projected=np.stack(projected)
    static=np.full(len(ys),3000.)
    for obj in [neck,ped]:
        p,t=evaluated(obj,graph,combined)
        static=np.minimum(static,left(p,t,adjacency(t),ys))
    parent_mane=left(base,tris,adj,ys)
    error=np.array(data['parent'])-np.minimum(parent_mane,static)
    # The terminal ring must sit inside the real neck envelope. The inner
    # circumference must continue to overlap the neck up the lower mane.
    tree=BVHTree.FromObject(neck,graph)
    tip0=old.reshape(13,64,3)[12].mean(0)
    tipm=modes.reshape(len(modes),13,64,3)[:,12].mean(1)
    inside0=old.reshape(13,64,3)[9:,0]
    insidem=modes.reshape(len(modes),13,64,3)[:,9:,0]
    low=(rows>=580)&(rows<=686)
    # A fixed pedestal starts to extend past the photographed sweep near its
    # lower end. Compare the visible union and the uninterrupted mane itself.
    weight=np.where(rows<575,.6,1.)
    guide=obs-np.clip((rows-648)/18,0,1)*4.4
    fit_mane=(rows>=568)&(rows<=668)
    def estimate(v):
        points=base+np.einsum('i,ivc->vc',v,projected,optimize=False)
        outline=left(points,tris,adj,ys)
        predicted=np.minimum(outline,static)+error
        return predicted,outline
    def cost(v,detail=False):
        pred,profile=estimate(v)
        union=np.average(np.abs(pred-obs),weights=weight)
        target=np.average(np.abs(profile[fit_mane]+error[fit_mane]-guide[fit_mane]))
        crest_x=pred[low].max();sel=rows[low][pred[low]>crest_x-.9]
        crest=float(sel.mean())
        tip=tip0+v@tipm
        seat=depth_into(tree,neck,tip)
        inners=inside0+np.einsum('i,irc->rc',v,insidem)
        connected=[depth_into(tree,neck,pt) for pt in inners]
        limiting=min(connected)
        junction=abs(np.interp(666,rows,profile-static))
        total=union+.65*target+.14*abs(crest-667)+.65*junction+90*max(0,.018-seat)+65*max(0,-.012-limiting)
        # Favor modest depth and a regular taper, with most fit carried by
        # the rear sweep. The actual side and rear decide the visual result.
        total+=1.8*v[2]+.40*abs(v[4])+.30*v[0]
        if detail:
            return {'cost':total,'union_contour_mae':union,'mane_contour_mae':target,'turn_row':crest,
                 'tip_center':tip.tolist(),'tip_neck_inside_depth':seat,'inner_neck_inside_depths':connected,
                 'predicted_edges':pred.tolist(),'mane_edges':profile.tolist(),'static_edges':static.tolist()}
        return total
    bounds=np.array([[.02,.44],[.10,.37],[0,.18],[0,.10],[-.04,.18],[0,.20]])
    best=np.array([.11,.33,0,.075,-.015,.14]);best_score=cost(best)
    directions=np.concatenate([np.eye(6),[[-.70,0,0,0,0,1],[0,-.60,0,0,1,0],[0,0,-.70,0,0,1]]])
    for step in [.07,.033,.014,.006,.002]:
        for _ in range(18):
            oldscore=best_score
            for direction in directions:
                for sign in [-1,1]:
                    v=np.clip(best+step*sign*direction,bounds[:,0],bounds[:,1])
                    sc=cost(v)
                    if sc<best_score-1e-5:best,best_score=v,sc
            if best_score==oldscore:break
    result=old+np.einsum('i,ivc->vc',best,modes)
    cfg={'parent_sha256':PARENT,'pose':[pose['dx'],pose['dy'],pose['twist_degrees']],
         'parameter_order':['rear_sweep','drop','extra_bilateral_half_width','upper_draw_in','middle_drop','terminal_shoulder'],
         'parameters_world_units':best.tolist(),'before':cost(np.zeros(len(modes)),True),'after':cost(best,True),
         'rows':rows.tolist(),'maximum_vertex_displacement':float(np.linalg.norm(result-old,axis=1).max())}
    if '--fit-only' in sys.argv:
        print('MANE_FIT_STUDY',best,cfg['after']['union_contour_mae'],cfg['after']['turn_row'],
              cfg['after']['inner_neck_inside_depths'],flush=True)
        return
    apply_world(mane,result);bpy.context.view_layer.update()
    scene['knight_improvement_004_A']=json.dumps({'values':best.tolist(),'parent':PARENT})
    configure_render(scene,144);save_model(scene,OUT/'knight.blend')
    cfg['model_sha256']=sha(OUT/'knight.blend');json_file(OUT/'parameters.json',cfg)
    print('MANE_FIT',best,cfg['before']['union_contour_mae'],cfg['after']['union_contour_mae'],
          cfg['after']['turn_row'],cfg['after']['tip_neck_inside_depth'],flush=True)
    pictures()


if __name__=='__main__':main()
