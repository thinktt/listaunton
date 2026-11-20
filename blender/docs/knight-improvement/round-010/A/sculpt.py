"""Sharpen the paired mane shoulders and seat the swept ear roots into the skull."""
from pathlib import Path
import json,sys
import numpy as np
import bpy
D=Path(__file__).resolve().parent;sys.dont_write_bytecode=True
sys.path[:0]=[str(D),str(D.parents[2]/'scripts/knight')]
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import world_vertices,configure_render,save_model,json_file,sha,render,use_side_camera
from sections import skull_profile
from diagnostic_views import pictures,clay_studio
PARENT='8e015620e552bda2c1e67866da8a7a3ba0e671c16deb22d93c07fb6c7859121d'
def ease(t):
    t=np.clip(t,0,1);return t*t*(3-2*t)
def apply(obj,original,edited,pose):
    shift=posed(edited.reshape(-1,3),*pose)-posed(original.reshape(-1,3),*pose)
    shift[~np.any(edited.reshape(-1,3)!=original.reshape(-1,3),axis=1)]=0
    mat=np.asarray(obj.matrix_world)
    vec=np.empty((len(obj.data.vertices),3),np.float32);obj.data.vertices.foreach_get('co',vec.ravel())
    vec+=np.asarray(shift@np.linalg.inv(mat[:3,:3]).T,np.float32)
    obj.data.vertices.foreach_set('co',vec.ravel());obj.data.update()
    n=np.linalg.norm(edited-original,axis=2)
    return {'max_displacement':float(n.max()),'moved_vertices_1e-6':int((n>1e-6).sum()),'max_by_station':n.max(1).tolist()}
def bevel(ring):
    # Intersect the tangents of the existing broad faces. Trim back their
    # intersection to retain a small convex, physical bevel under subdivision.
    p,q=ring[18],ring[24];l=ring[19]-p;r=q-ring[23]
    l/=np.linalg.norm(l);r/=np.linalg.norm(r)
    s,t=np.linalg.lstsq(np.column_stack((l,r)),q-p,rcond=None)[0]
    corner=((p+s*l)+(q-t*r))*.5
    angle=float(np.arccos(np.clip(l@r,-1,1)))
    trim=min(.018,.32*s,.32*t)
    left=corner-trim*l;right=corner+trim*r
    contour=[left]
    for a in [.20,.50,.80]:contour.append((1-a)**2*left+2*(1-a)*a*corner+a*a*right)
    contour.append(right)
    return np.array(contour),{'old_face_tangent_turn_degrees':float(np.degrees(angle)),'tangent_trim':float(trim)}
def soften_heel(ring):
    # The lower arris reaches the frontal attachment at lane 17. Ease its
    # lateral tangent into the broad forehead before it meets the upper ear.
    # One Hermite turn preserves both neighboring faces and removes the
    # straight facet boundary that previously traversed the heel.
    old=ring[7:20];ds=np.r_[0,np.cumsum(np.linalg.norm(np.diff(old,axis=0),axis=1))]
    u=(ds/ds[-1])[:,None]
    v0=ring[9]-ring[7];v0/=np.linalg.norm(v0)
    v1=ring[19]-ring[18];v1/=np.linalg.norm(v1)
    return ((2*u**3-3*u**2+1)*old[0]+(u**3-2*u**2+u)*ds[-1]*v0
           +(-2*u**3+3*u**2)*old[-1]+(u**3-u**2)*ds[-1]*v1)
def cut_mane(obj,pose,depth):
    a=rest_coords(world_vertices(obj),pose).astype(float).reshape(13,64,3);b=a.copy();detail={}
    weights=[0,0,.81,.90,.90,.81,.47,0,0,0,0,0,0]
    for i in range(2,7):
        cut,detail[i]=bevel(a[i]);b[i,19:24]+=weights[i]*(cut-a[i,19:24])
        # Preserve bilateral geometry, including the original tiny numerical
        # asymmetry from posing, by applying only the mirrored increment.
        inds=np.arange(19,24);b[i,64-inds]+=(b[i,inds]-a[i,inds])*[1,-1,1]
    # Ease the last visible part of each face into the forehead. The center
    # of the cap and the pitched sides away from the join retain their contour.
    k=np.minimum(np.arange(64),64-np.arange(64))
    for i,weight in enumerate([.85,1.,.30]):
        ring=b[i];surface=depth(ring);excess=abs(ring[:,1])-surface
        fade=ease((k-7)/4)*ease((23-k)/4)
        touch=.019*weight*fade*np.exp(-((np.nan_to_num(excess,nan=2)-.025)/.085)**2)
        # The lower return follows underneath the cheek-facing ear shoulder.
        # Its outside catches up with the broad skin before dying into it.
        low=np.exp(-((k-12)/4.0)**2)*weight
        ring[:,1]+=np.sign(ring[:,1])*(.024*low-touch)
        ring[:,2]-=.014*low
    for i,weight in enumerate([1,1,.92,.31]):
        ring=b[i];inds=np.arange(7,20)
        move=weight*(soften_heel(ring)-ring[inds]);ring[inds]+=move
        ring[64-inds]+=move*[1,-1,1]
    attrs=obj.data.attributes['Knight varnish coverage'];cov=np.array([x.value for x in attrs.data]).reshape(13,64)
    # Gentle burnishing follows the narrow shoulder on both flanks and fades
    # before the face disappears into the forehead.
    keep=.29+.71*np.exp(-((k-25.1)/.91)**2)
    roll=np.array([.32,.87,1,1,.94,.66,.32,0,0,0,0,0,0])[:,None]*ease((k-18)/3)[None,:]
    cov*=1-roll*(1-keep)
    target=(.05*np.exp(-((k-21)/1.50)**2))[None,:]*np.array(weights)[:,None]
    attrs.data.foreach_set('value',(cov+(1-cov)*target).astype(np.float32).ravel())
    info=apply(obj,a,b,pose);info.update({'shoulder_weights':weights,'bevel_sections':detail,
         'centerline_max_change':float(np.linalg.norm(a[:,:,0:3]-b[:,:,0:3],axis=2)[:,32].max())})
    return info
def each_ear(obj,pose,side,depth):
    a=rest_coords(world_vertices(obj),pose).astype(float).reshape(7,64,3);b=a.copy()
    k=np.arange(64);phi=((k+32)%64)-32
    # Only the inner surface of the high ear rail is tipped toward the crown.
    # Its exterior silhouette and both entire free-end stations are protected.
    inner=np.exp(-((phi+3.)/6.)**2)
    crown=ease((np.cos(2*np.pi*phi/64)+.1)/1.05)
    for i,(tip,seat) in enumerate(zip([0,0,.74,.82,.38,.08,0],[0,0,0,.42,1.,.81,.25])):
        ring=a[i];surface=depth(ring);excess=abs(ring[:,1])-surface
        window=np.exp(-((np.nan_to_num(excess,nan=2)-.031)/.096)**2)
        # Tuck each root through the native forehead skin at a shallower angle.
        b[i,:,1]-=side*seat*(.009+.025*window)
        b[i,:,2]-=seat*(.006+.006*window)
        b[i,:,1]+=side*.012*tip*inner;b[i,:,2]-=.006*tip*inner
        # The embedded ear cap returns towards the forehead; the lower face
        # still planes into the seat. Both free-end stations remain in place.
        arch=[0,0,0,.31,1.,.56,0][i]*crown
        b[i,:,2]+=.064*arch;b[i,:,1]+=side*.021*arch
    attr=obj.data.attributes['Knight varnish coverage'];cov=np.array([x.value for x in attr.data]).reshape(7,64)
    polish=np.exp(-((phi+1)/8.)**4)*np.array([0,.38,1.,1.,.72,.32,0])[:,None]
    new=cov*(1-.975*polish)
    attr.data.foreach_set('value',new.astype(np.float32).ravel())
    info=apply(obj,a,b,pose);info['mean_polish_near_stripe']=[float(t[2,61:64].mean()) for t in (cov,new)]
    return info
def finish_joint(obj,pose,outer):
    # A narrow convex fillet dresses the intersection towards the forehead.
    # It is built in both physical flanks, independent of any camera or light.
    a=rest_coords(world_vertices(obj),pose).astype(float)
    x,y,z=a.T
    w=(ease((x+.35)/.18)*ease((.37-x)/.13)*ease((z-4.70)/.105)*
       ease((5.085-z)/.055)*ease((abs(y)-.09)/.10))
    active=w>0
    sleeve=outer(a[active]);s=abs(y[active])-np.nan_to_num(sleeve,nan=2)
    radius=.085
    rise=np.maximum(radius-s,0)**2/(4*radius)-.0018
    rise=np.maximum(0,rise)*ease((s+.13)/.086)*w[active]
    offset=np.zeros(len(a));offset[active]=np.minimum(.055,rise)
    b=a.copy();b[:,1]+=np.sign(y)*offset
    # Dress the narrow end-grain return with satin finish. Ease out before
    # the short upright face of the forehead so the upright can still glint.
    attr=obj.data.attributes.get('Knight varnish coverage')
    if attr is not None:
        old=np.array([v.value for v in attr.data]);new=old.copy()
        belt=w[active]*np.exp(-((s-.004)/.053)**2)*ease((.233-x[active])/.100)
        new[active]*=1-.83*belt
        attr.data.foreach_set('value',new.astype(np.float32))
    info=apply(obj,a[None],b[None],pose)
    info['fillet_width']=radius;info['visible_fillet_max_lift']=float(rise[s>=0].max(initial=0))
    return info
def preview(scene):
    configure_render(scene,64)
    for tag,camera,clay,box in [('fixed','fixed',False,(236,282,530,409)),('clay','fixed',True,(236,282,530,409)),
                                ('side-clay','side',True,(300,96,798,391))]:
        if camera=='side':use_side_camera(scene)
        if tag=='clay':clay_studio(scene,10.3)
        x,y,u,v=box;scene.render.use_border=scene.render.use_crop_to_border=True
        scene.render.border_min_x=(x+.001)/1254;scene.render.border_max_x=(u+.001)/1254
        scene.render.border_min_y=(1254-v+.001)/1254;scene.render.border_max_y=(1254-y+.001)/1254
        render(scene,D/('preview-'+tag+'.png'))
def build():
    assert sha(D/'parent.blend')==PARENT
    bpy.ops.wm.open_mainfile(filepath=str(D/'parent.blend'),load_ui=False);s=bpy.context.scene
    p=json.loads(s['knight_mission_pose']);pose=[p[k] for k in ('dx','dy','twist_degrees')]
    depth=skull_profile(s,pose);cfg={'parent_sha256':PARENT,'pose':pose,'geometry':{}}
    cfg['geometry']['mane']=cut_mane(s.objects['Knight | swept rounded mane'],pose,depth)
    for side,sign in [('near',-1),('far',1)]:
        cfg['geometry'][side+' ear']=each_ear(s.objects['Knight | '+side+' swept ear'],pose,sign,depth)
    bpy.context.view_layer.update()
    mantle=skull_profile(s,pose,'swept rounded mane')
    for suffix in ('continuous horse head and neck','coherent skull cheek and conical muzzle'):
        cfg['geometry'][suffix]=finish_joint(s.objects['Knight | '+suffix],pose,mantle)
    s['knight_improvement_010_A']=json.dumps(cfg);configure_render(s,144);save_model(s,D/'knight.blend')
    cfg['model_sha256']=sha(D/'knight.blend');json_file(D/'parameters.json',cfg)
    print('ROUND_10A',cfg['model_sha256'],flush=True)
if __name__=='__main__':
    if '--render-only' not in sys.argv:build()
    if '--preview' in sys.argv:
        bpy.ops.wm.open_mainfile(filepath=str(D/'knight.blend'),load_ui=False);preview(bpy.context.scene)
    elif '--build-only' not in sys.argv:pictures()
