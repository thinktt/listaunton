"""Cut a planar mane and carve bilateral upper and lower lids into the skull."""
from pathlib import Path
import json
import sys
import bmesh
import bpy
import numpy as np
from mathutils import Vector

sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'scripts/knight'));sys.path.insert(0,str(OUT))
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import configure_render,json_file,render,save_model,sha,world_vertices
from refine_eye import apply_world
from probe_carving import point_probe
from diagnostic_views import pictures

PARENT='65dac17941c4a06535e59ed0c63e0fc028979e5d60e8954046f4e92c5355b268'
CENTER=np.array([.412,4.158])
LONG=np.array([1.,-.76]);LONG/=np.linalg.norm(LONG)
ACROSS=np.array([-LONG[1],LONG[0]])
GUIDES=np.array([[1,0],[.70,.765],[-.16,1.015],[-.802,.603],[-1.002,0]])
KNOTS=[0,8,17,25,32]
L=.267


def smooth(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)


def pose_for(scene):
    info=json.loads(scene['knight_mission_pose'])
    return [info[k] for k in ('dx','dy','twist_degrees')]


def section_polygon():
    yz=np.empty((33,2))
    for i,(a,b) in enumerate(zip(KNOTS[:-1],KNOTS[1:])):
        t=np.linspace(0,1,b-a+1)
        # The samples closest to an arris are real support lines. Two levels of
        # subdivision round only the narrow cutting edge between broad faces.
        t=.23*t+.77*smooth(t)
        yz[a:b+1]=(1-t[:,None])*GUIDES[i]+t[:,None]*GUIDES[i+1]
    half=yz[-2:0:-1].copy();half[:,1]*=-1
    return np.concatenate((yz,half))


def carve_mane(obj,pose):
    world=world_vertices(obj)
    old=rest_coords(world,pose).reshape(13,64,3)
    theta=np.arange(64)*2*np.pi/64
    desired=section_polygon()
    out=old.copy()
    for i,ring in enumerate(old):
        # Retain the established course of each ring, including the depth
        # correction and the lower neck insertion. Replace only its perimeter.
        a=(ring[0]-ring[32])*.5
        b=(ring[16]-ring[48])*.5
        tip_width=1 if i<=10 else [.945,.79][i-11]
        out[i]+=(desired[:,0]-np.cos(theta))[:,None]*a
        out[i]+=(desired[:,1]*tip_width-np.sin(theta))[:,None]*b
    moved=world+posed(out.reshape(-1,3),*pose)-posed(old.reshape(-1,3),*pose)
    apply_world(obj,moved)
    attr=obj.data.attributes['Knight varnish coverage']
    varnish=np.empty(len(attr.data),np.float32);attr.data.foreach_get('value',varnish)
    crown=np.repeat([1,1,1,1,.85,.56,.20,0,0,0,0,0,0],64)
    attr.data.foreach_set('value',(varnish*(1-.53*crown)).astype(np.float32));obj.data.update()
    return {'guides_inner_to_back_half':GUIDES.tolist(),'guide_vertex_indices':KNOTS,
            'support_interpolation_linear_fraction':.23,'last_two_ring_width_multipliers':[.945,.79],
            'crown_varnish_multiplier':.47,
            'max_displacement':float(np.linalg.norm(moved-world,axis=1).max())}


def coordinates(rest):
    d=rest[:,[0,2]]-CENTER
    return d@LONG,d@ACROSS


def coefficients(u,v):
    return np.column_stack([np.ones_like(u),u,v,u*u,u*v,v*v,u*u*u,u*u*v,u*v*v,v*v*v])


def fit_cheek(rest,side):
    u,v=coordinates(rest)
    r=np.sqrt((u/.30)**2+(v/.145)**2)
    use=(r>1.06)&(r<1.70)&(side*rest[:,1]>.17)
    design=coefficients(u[use],v[use]);y=side*rest[use,1]
    weight=np.exp(-((r[use]-1.27)/.38)**2)
    for _ in range(3):
        coef=np.linalg.lstsq(design*weight[:,None],y*weight,rcond=None)[0]
        residual=np.abs(design@coef-y)
        weight*=np.minimum(1,.026/np.maximum(residual,1e-5))
    return coef


def refine_orbital_surface(obj,pose):
    before=len(obj.data.vertices)
    rest=rest_coords(world_vertices(obj),pose)
    u,v=coordinates(rest)
    region=((u/.405)**2+(v/.242)**2<1.03)&(np.abs(rest[:,1])>.15)
    bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.ensure_lookup_table();bm.verts.index_update()
    edges=[edge for edge in bm.edges if all(region[q.index] for q in edge.verts)]
    bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True,smooth=0.)
    bm.normal_update();bm.to_mesh(obj.data);bm.free();obj.data.update()
    return [before,len(obj.data.vertices)]


def lid_profiles(u,v):
    n=u/L
    window=smooth((1.07-abs(n))/.25)
    taper=np.maximum(0,1-n*n)
    # A shallower front corner and a lower front tip rake the eye forward.
    axis=-.105*u+.008*taper
    upper=axis+.067*taper*(1-.16*n)
    lower=axis-.052*taper*(1+.08*n)
    return n,window,taper,upper,lower


def shape_skull(obj,pose,cheeks):
    world=world_vertices(obj);rest=rest_coords(world,pose);out=rest.copy()
    u,v=coordinates(rest);n,w,_,upper,lower=lid_profiles(u,v)
    r=np.sqrt((u/.31)**2+(v/.15)**2)
    blend=smooth((1.58-r)/.44)
    opening=w*smooth((upper-v+.005)/.030)*smooth((v-lower+.019)/.056)
    # This continuous envelope supplies both lips. In cross-section the top
    # edge turns abruptly over the floor; the lower ledge runs into the cheek.
    arch=w*(.030*np.exp(-((v-upper-.009)/.042)**2)+.019*np.exp(-((v-upper-.052)/.083)**2))
    lower_plane=w*(.018*np.exp(-((v-lower+.015)/.043)**2)+.008*np.exp(-((v-lower+.054)/.072)**2))
    crease=w*.013*np.exp(-((v-upper+.022)/.014)**2)
    floor=-opening*(.060+.012*smooth((v-lower)/.095))
    canthus=-.014*np.exp(-((np.abs(u)-.249)/.043)**2-((v+.105*u)/.033)**2)
    for side,coef in cheeks.items():
        local=(side*rest[:,1]>.12)&(r<1.58)
        chart=coefficients(u[local],v[local])@coef
        old=side*rest[local,1]
        desired=chart+arch[local]+lower_plane[local]+crease[local]*-1+floor[local]+canthus[local]
        out[local,1]+=side*blend[local]*(desired-old)
    moved=world+posed(out,*pose)-posed(rest,*pose)
    apply_world(obj,moved)
    varnish=obj.data.attributes.get('Knight varnish coverage')
    if varnish is not None:
        prior=np.empty(len(varnish.data),np.float32);varnish.data.foreach_get('value',prior)
        band=w*np.exp(-((v-lower+.018)/.026)**2)*blend
        varnish.data.foreach_set('value',(prior+(1-prior)*.55*band).astype(np.float32))
        obj.data.update()
    return {'changed_vertices':int((np.linalg.norm(moved-world,axis=1)>.0005).sum()),
            'max_displacement':float(np.linalg.norm(moved-world,axis=1).max())}


def seat_floor(obj,pose,side,cheek):
    world=world_vertices(obj);rest=rest_coords(world,pose)
    u,v=coordinates(rest)
    u0=(u.min()+u.max())/2;v0=(v.min()+v.max())/2
    uc=(u-u0)/(.5*np.ptp(u));vc=(v-v0)/(.5*np.ptp(v))
    # The existing closed, UV-mapped piece becomes a shallow floor behind the
    # continuous skull opening. The perimeter sits beneath both carved lips.
    dest_u=.261*uc
    dest_v=-.105*dest_u+.001+.079*vc*(1-.18*uc*uc)
    dest_xz=CENTER+dest_u[:,None]*LONG+dest_v[:,None]*ACROSS
    oldmid=coefficients(u,v)
    thickness=side*rest[:,1]-oldmid@np.linalg.lstsq(oldmid,side*rest[:,1],rcond=None)[0]
    base=coefficients(dest_u,dest_v)@cheek
    height=.038*np.maximum(0,1-((dest_u+.019)/.255)**2)*np.maximum(0,1-(vc/.99)**2)
    y=base-.030+height+.23*thickness
    dst=np.column_stack((dest_xz[:,0],side*y,dest_xz[:,1]))
    apply_world(obj,world+posed(dst,*pose)-posed(rest,*pose))
    attr=obj.data.attributes['Knight varnish coverage']
    a=np.empty(len(attr.data),np.float32);attr.data.foreach_get('value',a)
    coverage=np.minimum(.29,.115+.32*a).astype(np.float32)
    attr.data.foreach_set('value',coverage)
    obj.data.update()
    return {'old_half_length':float(.5*np.ptp(u)),'old_max_hemisphere_thickness':float(np.ptp(thickness)),
            'new_max_hemisphere_thickness':float(.23*np.ptp(thickness)),
            'bed_setback':.030,'center_crown':.038,'max_varnish_fraction':float(coverage.max())}


def soft_reflection(scene,probe,lightname,obj,nominal,dimensions,energy,skin_receiver=False):
    nearby=[]
    for x in range(nominal[0]-9,nominal[0]+10,2):
        for y in range(nominal[1]-6,nominal[1]+7,2):
            hit=probe(x+.5,y+.5)
            if hit and hit[1]==obj.name:
                nearby.append(((x-nominal[0])**2+(y-nominal[1])**2,x,y,hit))
    if not nearby:raise ValueError((lightname,nominal))
    _,x,y,hit=min(nearby,key=lambda d:d[0])
    _,_,point,face_normal=hit
    inv=obj.matrix_world.inverted()
    success,local,_,polyindex=obj.closest_point_on_mesh(inv@point)
    normal=face_normal
    if success:
        verts=[obj.data.vertices[i] for i in obj.data.polygons[polyindex].vertices]
        weights=np.array([1/(.00004+(v.co-local).length**2) for v in verts]);weights/=weights.sum()
        n=sum((v.normal*float(w) for v,w in zip(verts,weights)),Vector())
        normal=(inv.transposed().to_3x3()@n).normalized()
    view=scene.camera.matrix_world.to_quaternion()@Vector((0,0,1))
    direction=(2*view.dot(normal)*normal-view).normalized()
    lamp=bpy.data.objects[lightname]
    lamp.location=point+.80*direction
    lamp.rotation_euler=(point-lamp.location).to_track_quat('-Z','Y').to_euler()
    lamp.data.shape='ELLIPSE';lamp.data.size,lamp.data.size_y=dimensions
    lamp.data.energy=energy;lamp.data.spread=np.radians(24)
    lamp.visible_diffuse=False;lamp.visible_glossy=True
    if skin_receiver:
        col=bpy.data.collections.new('Knight | lower eyelid finish')
        col.objects.link(obj);lamp.light_linking.receiver_collection=col
    return {'name':lightname,'point_on_part':[x,y],'world_position':list(lamp.location),
            'receiver':lamp.light_linking.receiver_collection.name,'axes':dimensions,'watts':energy}


def build():
    assert sha(OUT/'parent.blend')==PARENT
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'parent.blend'),load_ui=False)
    scene=bpy.context.scene;pose=pose_for(scene)
    skull=bpy.data.objects['Knight | continuous horse head and neck']
    construction=bpy.data.objects['Knight | coherent skull cheek and conical muzzle']
    cheeks={side:fit_cheek(rest_coords(world_vertices(skull),pose),side) for side in (-1,1)}
    cfg={'parent_sha256':PARENT,'pose':pose,
         'mane':carve_mane(bpy.data.objects['Knight | swept rounded mane'],pose),
         'skull_editable_vertices_before_after':refine_orbital_surface(skull,pose),
         'eye_center_rest_xz':CENTER.tolist(),'half_length':L,'cheek_polynomial':{k:v.tolist() for k,v in cheeks.items()},
         'continuous_surface':shape_skull(skull,pose,cheeks),
         'source_loft':shape_skull(construction,pose,cheeks)}
    for side,name in [(-1,'near'),(1,'far')]:
        cfg[name+'_floor']=seat_floor(bpy.data.objects['Knight | '+name+' eye'],pose,side,cheeks[side])
    oval=bpy.data.objects['Walnut | poll rear oval']
    cfg['poll_oval_watts_before_after']=[float(oval.data.energy),27.]
    oval.data.energy=27.
    bpy.context.view_layer.update()
    probe=point_probe(scene)
    cfg['eye_reflections']=[
        soft_reflection(scene,probe,'Eye reflection upper',bpy.data.objects['Knight | near eye'],
                        (498,479),(.068,.045),.046),
        soft_reflection(scene,probe,'Eye reflection lower',skull,(502,492),(.20,.065),.007,True)]
    scene['knight_improvement_005_A']=json.dumps(cfg)
    configure_render(scene,144);save_model(scene,OUT/'knight.blend')
    cfg['model_sha256']=sha(OUT/'knight.blend');json_file(OUT/'parameters.json',cfg)
    print('RIBBON_SOCKET',cfg['skull_editable_vertices_before_after'],cfg['near_floor'],flush=True)
    if '--preview' in sys.argv:
        configure_render(scene,96);scene.render.use_border=True;scene.render.use_crop_to_border=True
        scene.render.border_min_x=205/1254;scene.render.border_max_x=576/1254
        scene.render.border_min_y=(1254-514)/1254;scene.render.border_max_y=(1254-270)/1254
        render(scene,OUT/'refinement.png')


if __name__=='__main__':
    build()
    if '--build-only' not in sys.argv and '--preview' not in sys.argv:pictures()
