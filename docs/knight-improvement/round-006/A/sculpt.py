"""Shape the eye corners and the upper mane while preserving the registered model."""
from pathlib import Path
import json
import sys
import bpy
import numpy as np
from mathutils import Vector

sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path[:0]=[str(ROOT/'scripts/knight'),str(OUT)]
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import configure_render,json_file,render,save_model,sha,use_side_camera,world_vertices
from refine_eye import apply_world
from diagnostic_views import pictures,clay_studio
from glint import focus_oval

PARENT='8a53403942a3e5bea1df92e3f28c9bfd5d80c61a1026a03549f1c21fd4c96cb6'
CENTER=np.array([.412,4.158])
AXIS=np.array([1.,-.76])/np.hypot(1.,.76)
NORMAL=np.array([-AXIS[1],AXIS[0]])
L=.267


def ease(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)


def bell(v,width):
    return np.exp(-(v/width)**2)


def edit_eye(obj,pose):
    world=world_vertices(obj);rest=rest_coords(world,pose)
    xy=rest[:,[0,2]]-CENTER
    u=xy@AXIS;v=xy@NORMAL;n=u/L
    taper=np.maximum(0,1-n*n)
    axis=-.105*u+.008*taper
    upper=axis+.067*taper*(1-.16*n)
    lower=axis-.052*taper*(1+.08*n)
    r=np.hypot(u/.31,v/.15)
    blend=ease((1.58-r)/.44)
    w=ease((1.07-abs(n))/.25)
    old_open=w*ease((upper-v+.005)/.030)*ease((v-lower+.019)/.056)
    old_arch=w*(.030*bell(v-upper-.009,.042)+.019*bell(v-upper-.052,.083))
    old_lower=w*(.018*bell(v-lower+.015,.043)+.008*bell(v-lower+.054,.072))
    old_crease=w*.013*bell(v-upper+.022,.014)
    old_floor=-old_open*(.060+.012*ease((v-lower)/.095))
    old_corner=-.014*bell(abs(u)-.249,.043)*bell(v+.105*u,.033)

    # A C1 continuation matters here: a hard stop in the elliptical radius
    # leaves a vertical ridge outside the eye even after filling the divot.
    radius=1-n*n
    soft=.29
    taper=np.where(radius>=soft,radius,np.where(radius<=-soft,0.,(radius+soft)**2/(4*soft)))
    axis=-.105*u+.008*taper
    upper=axis+.067*taper*(1-.16*n)
    lower=axis-.052*taper*(1+.08*n)
    # End the recess before the overlapping lips have lost all their height.
    # Both canthi return monotonically to the cheek without a second dimple.
    opening=ease((1.02-abs(n))/.44)
    lip=ease((1.27-abs(n))/.63)
    recess=opening*ease((upper-v+.005)/.032)*ease((v-lower+.022)/.058)
    floor=-recess*(.061+.010*ease((v-lower)/.095))
    upper_lid=lip*(.027*bell(v-upper-.011,.045)+.014*bell(v-upper-.050,.092))
    crease=opening*.010*bell(v-upper+.021,.017)
    # The lower edge wraps out below the eye and towards the malar plane.
    # Continue its forward end along the cheek tangent as the opening closes.
    extended=lower-.020*ease((n-.60)/.62)
    shelf=ease((1.36-abs(n-.06))/.68)
    lower_lid=shelf*(.020*bell(v-extended+.021,.041)+.014*bell(v-extended+.072,.091))
    delta=(upper_lid+lower_lid-crease+floor)-(old_arch+old_lower-old_crease+old_floor+old_corner)
    mask=(abs(rest[:,1])>.12)&(r<1.58)
    step=np.where(mask,delta*blend,0)
    new=rest.copy();new[:,1]+=np.sign(rest[:,1])*step
    apply_world(obj,world+posed(new,*pose)-posed(rest,*pose))
    finish=obj.data.attributes.get('Knight varnish coverage')
    if finish is not None:
        coverage=np.empty(len(finish.data),np.float32);finish.data.foreach_get('value',coverage)
        corner_softness=np.where(mask,ease((n-.62)/.26)*ease((1.38-n)/.24)*bell(v-axis,.087),0)
        finish.data.foreach_set('value',(coverage*(1-.76*corner_softness)).astype(np.float32))
        obj.data.update()
    return {'changed_vertices':int(np.count_nonzero(abs(step)>.0001)),
            'max_surface_displacement':float(abs(step).max()),
            'max_anterior_canthus_fill':float(step[(n>.78)&(n<1.15)].max())}


def edit_crown(obj,pose):
    world=world_vertices(obj);rest=rest_coords(world,pose).reshape(13,64,3)
    edited=rest.copy()
    # Rail fractions set a continuous arc around the poll. Taper the lower
    # arris into the forehead over the first four rings to lose the abrupt
    # triangular termination. Keep the complete broad section below ring 7.
    fractions=[1.17,1.08,.62,.40,.35,.50,.78,1.,1.,1.,1.,1.,1.]
    merger=[1.,.95,.67,.27,.03,0.,0.,0.,0.,0.,0.,0.,0.]
    knots=[0,8,17,25,32]
    for i,ring in enumerate(rest[:7]):
        anchors=ring[knots].copy()
        # A quadratic turn from the dorsal midline retains a slightly convex
        # cap above the narrow bevel. Its following face remains broad.
        rail=ring[32]+(ring[25]-ring[32])*fractions[i]
        rail[[0,2]]=ring[32,[0,2]]+(ring[25,[0,2]]-ring[32,[0,2]])*fractions[i]**1.64
        anchors[3]=rail
        anchors[1,1]+=merger[i]*(ring[17,1]*.12)
        t0=(anchors[2,2]-anchors[1,2])/(anchors[3,2]-anchors[1,2])
        joined=(1-t0)*anchors[1,1]+t0*anchors[3,1]
        anchors[2,1]+=merger[i]*(joined-anchors[2,1])*.27
        # Seat the inner side of the forehead joint closer to the ear.
        anchors[1,0]+=.041*merger[i];anchors[2,0]+=.017*merger[i]
        anchors[1,1]+=.027*merger[i];anchors[2,1]+=.017*merger[i]
        # Reconnect the two side ridges with lengthwise corresponding quad rows.
        for j,(a,b) in enumerate(zip(knots[:-1],knots[1:])):
            t=np.linspace(0,1,b-a+1)
            t=.23*t+.77*ease(t)
            if a in (17,25):
                # Slightly widen the real radius of the upper bevel. Sharpen
                # it progressively along the neck, using the same old vertices.
                extra=.65*(1-i/9)
                t=(1-extra)*t+extra*np.linspace(0,1,b-a+1)
            edited[i,a:b+1]=(1-t[:,None])*anchors[j]+t[:,None]*anchors[j+1]
        # Preserve the original solid shoulder on both sides under the far
        # ear. Reparameterise the long face and ease through the old shoulder
        # between the new bevel and lateral plane. Its curvature is continuous.
        restore=ease((1.01-fractions[i])/.32)
        if restore:
            prior=edited[i,17:26].copy()
            shoulder=ring[25].copy()
            shoulder[1]+=.021
            entering=.78*shoulder+.22*prior[0]
            leaving=.72*shoulder+.28*rail
            curve=[prior[0],.58*prior[0]+.42*entering,entering]
            for t in (.25,.60,1.0):
                curve.append((1-t)**2*entering+2*(1-t)*t*shoulder+t*t*leaving)
            curve.extend((.58*leaving+.42*rail,.21*leaving+.79*rail,rail))
            edited[i,17:26]=prior+restore*(np.asarray(curve)-prior)
        # Gently chamfer the core of the longitudinal rail in the crown only.
        span=.19*(1-i/9)
        edited[i,25]=(1-2*span)*edited[i,25]+span*(edited[i,24]+edited[i,26])
        for k in range(1,32):
            edited[i,64-k]=edited[i,k];edited[i,64-k,1]*=-1
    dif=posed(edited.reshape(-1,3),*pose)-posed(rest.reshape(-1,3),*pose)
    apply_world(obj,world+dif)
    # The gently burnished bevel follows the topological edge on both faces.
    # Its flanking flat planes retain a satin surface finish.
    finish=obj.data.attributes['Knight varnish coverage']
    cov=np.array([q.value for q in finish.data],np.float32).reshape(13,64)
    k=np.minimum(np.arange(64),64-np.arange(64))
    strength=np.array([.55,.9,1,1,1,.72,.26,0,0,0,0,0,0])[:,None]*ease((k-14)/5)[None,:]
    target=.021+.58*np.exp(-((k-25)/1.20)**2)
    finish.data.foreach_set('value',(cov+(target-cov)*strength).astype(np.float32).ravel())
    obj.data.update()
    return {'dorsal_rail_fractions':fractions,'forehead_merge_weights':merger,
            'max_displacement':float(np.linalg.norm(dif,axis=1).max()),
            'lower_six_rings_max_displacement':float(np.linalg.norm(dif.reshape(13,64,3)[7:],axis=2).max())}


def select_crop(scene,box):
    x0,y0,x1,y1=box
    scene.render.use_border=True;scene.render.use_crop_to_border=True
    scene.render.border_min_x=(x0+.01)/1254;scene.render.border_max_x=(x1+.01)/1254
    scene.render.border_min_y=(1254-y1+.01)/1254;scene.render.border_max_y=(1254-y0+.01)/1254


def preview():
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'knight.blend'),load_ui=False);scene=bpy.context.scene
    configure_render(scene,64)
    select_crop(scene,(195,273,574,514));render(scene,OUT/'preview-wood.png')
    clay_studio(scene,10.3);render(scene,OUT/'preview-clay.png')
    scene.render.use_border=False;scene.render.use_crop_to_border=False
    use_side_camera(scene);select_crop(scene,(450,125,707,375));render(scene,OUT/'preview-side-clay.png')


def build():
    assert sha(OUT/'parent.blend')==PARENT
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'parent.blend'),load_ui=False)
    scene=bpy.context.scene
    p=json.loads(scene['knight_mission_pose']);pose=[p[k] for k in ['dx','dy','twist_degrees']]
    cfg={'pose':pose,'parent_sha256':PARENT}
    for name,key in [('Knight | continuous horse head and neck','skull'),
                     ('Knight | coherent skull cheek and conical muzzle','construction')]:
        cfg[key]=edit_eye(bpy.data.objects[name],pose)
    mane=bpy.data.objects['Knight | swept rounded mane']
    cfg['crown']=edit_crown(mane,pose)
    bpy.context.view_layer.update()
    cfg['studio']=focus_oval(scene,mane)
    scene['knight_improvement_006_A']=json.dumps(cfg)
    configure_render(scene,144);save_model(scene,OUT/'knight.blend')
    cfg['model_sha256']=sha(OUT/'knight.blend');json_file(OUT/'parameters.json',cfg)


if __name__=='__main__':
    if '--render-only' not in sys.argv:build()
    if '--preview' in sys.argv:preview()
    elif '--build-only' not in sys.argv:pictures()
