"""Round 5B. Plane a beveled mane and cut a two-sided eye directly into the face."""
from pathlib import Path
import json,sys
import bpy,bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/"scripts/knight"))
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import configure_render,json_file,render,save_model,sha,use_side_camera,visible_meshes,world_vertices
from refine_eye import apply_world
PARENT="65dac17941c4a06535e59ed0c63e0fc028979e5d60e8954046f4e92c5355b268"
EYE=np.array([.405,4.18]);ALONG=np.array([1.,-1.08]);ALONG/=np.linalg.norm(ALONG)
UP=np.array([-ALONG[1],ALONG[0]])
DESIGN=(.07,.009,.053,.003,.30,.006)
def ease(t):
    t=np.clip(t,0,1);return t*t*(3-2*t)
def loaded(name):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/name),load_ui=False)
    return bpy.context.scene
def old_tree(obj,co):
    obj.data.calc_loop_triangles()
    tri=np.empty((len(obj.data.loop_triangles),3),np.int32)
    obj.data.loop_triangles.foreach_get("vertices",tri.ravel())
    return BVHTree.FromPolygons(co.tolist(),tri.tolist(),all_triangles=True)
def planar_mane(pose,strength):
    obj=bpy.data.objects["Knight | swept rounded mane"]
    world=world_vertices(obj);original=rest_coords(world,pose);rings=original.reshape(13,64,3)
    new=rings.copy()
    # One dorsal plane, a softly crowned broad flank and two closely spaced
    # support edges at the undercut. Coordinates are continuous at the spine.
    stations=np.array([0,4,7,9,10,11,12,14,17,21,23,24,25,26,28,32])
    radial=np.array([1,.93,.83,.71,.61,.55,.46,.25,-.08,-.48,-.64,-.73,-.81,-.89,-.965,-1])
    width=np.array([0,.24,.44,.56,.63,.81,.91,.93,.956,.97,.963,.95,.89,.78,.55,0])
    signed=np.arange(64);idx=np.minimum(signed,64-signed)
    q=np.interp(idx,stations,radial);lat=np.interp(idx,stations,width)*np.where(signed<=32,1,-1)
    section=np.array([.56,.98,1,1,1,1,1,1,1,.98,.90,.62,.0])
    for i,ring in enumerate(rings):
        zero=ring.mean(0)
        # Use the parent's actual axes, including existing typed stations
        # and its asymmetric placement about the physical turned foot.
        axial=(ring[0]-ring[32])/2
        lateral=(ring[16]-ring[48])/2
        target=zero+q[:,None]*axial+lat[:,None]*lateral
        new[i]+=section[i]*strength*(target-ring)
    apply_world(obj,world+posed(new.reshape(-1,3),*pose)-posed(original,*pose))
    attr=obj.data.attributes.get("crease_edge") or obj.data.attributes.new("crease_edge","FLOAT","EDGE")
    values=np.zeros(len(obj.data.edges),np.float32)
    for edge in obj.data.edges:
        a,b=edge.vertices
        ca,cb=a%64,b%64
        if ca==cb and ca in [11,12,24,25,39,40,52,53]:
            values[edge.index]=.48*min(section[a//64],section[b//64])*strength
    attr.data.foreach_set("value",values);obj.data.update()
    return {"radial_stations":radial.tolist(),"half_widths":width.tolist(),"support_edges":int((values>0).sum()),
            "maximum_change":float(np.max(np.linalg.norm(new-rings,axis=2)))}

def coordinates(rest):
    xz=rest[:,[0,2]]-EYE
    return xz@ALONG,xz@UP

def prepare_bed(obj,pose):
    rest=rest_coords(world_vertices(obj),pose);tree=old_tree(obj,rest)
    grid=np.linspace(-.42,.43,98)
    grids={}
    for sign in (-1,1):
        rows=[]
        for off in [-.207,-.16,.152,.199]:
            row=[]
            for u in grid:
                x,z=EYE+u*ALONG+off*UP
                hit=tree.ray_cast(Vector((x,2*sign,z)),Vector((0,-sign,0)),4)[0]
                row.append(sign*hit.y if hit else np.nan)
            row=np.array(row);valid=np.isfinite(row)
            assert valid.sum()>len(grid)*.8
            row=np.interp(grid,grid[valid],row[valid])
            rows.append(row)
        grids[sign]=rows
    def surface(u,v,sign):
        result=np.zeros_like(u)
        for s,rows in grids.items():
            hit=sign==s
            if not hit.any():continue
            lo,left,right,hi=[np.interp(u[hit],grid,row) for row in rows]
            t=np.clip((v[hit]+.16)/.312,0,1)
            a=np.clip((left-lo)/.047,-1.7,1.7)*.312
            b=np.clip((hi-right)/.047,-1.7,1.7)*.312
            result[hit]=(2*t**3-3*t**2+1)*left+(t**3-2*t*t+t)*a+(-2*t**3+3*t*t)*right+(t**3-t*t)*b
        return result
    return surface

def subdivide(obj,pose):
    rest=rest_coords(world_vertices(obj),pose);u,v=coordinates(rest)
    keep=(np.abs(u)<.39)&(np.abs(v)<.222)&(np.abs(rest[:,1])>.16)
    bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.ensure_lookup_table()
    edges=[e for e in bm.edges if all(keep[k.index] for k in e.verts)]
    bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True)
    bm.to_mesh(obj.data);bm.free();obj.data.update()
    return len(obj.data.vertices)-len(rest)

def orbital_tilt(u,v,design):
    pitch,relief=design[:2]
    return (relief-pitch*v)*np.exp(-(u/.248)**4-(v/.133)**4)

def shape_face(obj,pose,bed,open_cut,design):
    world=world_vertices(obj);orig=rest_coords(world,pose);r=orig.copy()
    u,v=coordinates(r);s=np.sign(r[:,1]);d=np.abs(r[:,1])
    # The two ends have different lengths and turns. Only the upper edge has
    # a deep cut. The short lower glancing plane feathers out into the cheek.
    t=np.clip((u+.246)/.526,0,1);w=4*t*(1-t)
    arc=.060*w*(1.12-.42*t)-.019*t
    low=-.061*w*(.90+.16*t)-.013*t
    bowl=ease((v-low+.019)/.049)*ease((arc-v+.011)/.047)
    cut=(-.031*w*bowl-open_cut*w*(1-.21*t)*np.exp(-((v-arc+.006)/.027)**2)+
         .012*w*np.exp(-((v-arc-.041)/.046)**2))
    lip=.021*ease((u+.182)/.11)*ease((.205-u)/.12)*np.exp(-((v-low+.025)/.037)**2)
    surround=ease((u+.350)/.100)*ease((.372-u)/.090)*ease((v+.160)/.054)*ease((.152-v)/.044)
    surround*=.28+.72*ease((v+.145)/.087)
    surround*=ease((d-.14)/.12)
    fair=bed(u,v,s)
    r[:,1]=s*(d+surround*(fair+cut+lip+orbital_tilt(u,v,design)-d))
    apply_world(obj,world+(posed(r,*pose)-posed(orig,*pose)))
    return {"vertices_changed":int(np.sum(np.abs(r[:,1]-orig[:,1])>.00001)),
            "max_displacement":float(np.max(np.abs(r[:,1]-orig[:,1])))}

def inset_eye(obj,pose,bed,side,design):
    original=rest_coords(world_vertices(obj),pose)
    old_along=np.array([1.,-.76]);old_along/=np.linalg.norm(old_along)
    old_up=np.array([-old_along[1],old_along[0]])
    off=original[:,[0,2]]-np.array([.42,4.155])
    t=np.clip((off@old_along)/.198,-1,1)
    b=np.clip((off@old_up)/(.063*(1-.28*t*t)),-1,1)
    tree=old_tree(obj,original)
    fraction=[]
    for point in original:
        x,y,z=point
        a=tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4)[0]
        h=tree.ray_cast(Vector((x,2,z)),Vector((0,-1,0)),4)[0]
        if a is None or h is None or h.y-a.y<.00001:fraction.append(.5)
        else:fraction.append(np.clip((y-a.y)/(h.y-a.y),0,1))
    cap=(2*np.array(fraction)-1)*side*np.sqrt(np.maximum(0,1-t*t-b*b))
    # Compress the old orb into a tapered shallow facet. Its perimeter
    # passes beneath the re-cut lid. The outer cap is gently convex.
    u=-.024+.203*t
    v=.005+.043*b*(1-.47*t*t)-.014*t
    if len(design)>3:v-=design[5]
    tip=ease((.99-np.abs(t))/.41)
    profile=design[3]*tip-design[4]*v*tip if len(design)>3 else 0.
    d=bed(u,v,np.full_like(t,side))-.044+design[2]*cap+.002*t+orbital_tilt(u,v,design)+profile
    r=np.column_stack([EYE[0]+u*ALONG[0]+v*UP[0],side*d,EYE[1]+u*ALONG[1]+v*UP[1]])
    middle_u=np.array([-.024]);middle_v=np.array([.005])
    mid=EYE+middle_u[0]*ALONG+middle_v[0]*UP
    mid_depth=bed(middle_u,middle_v,np.array([side]))[0]-.044+orbital_tilt(middle_u,middle_v,design)[0]
    origin=posed(np.array([[mid[0],side*mid_depth,mid[1]]]),*pose)[0]
    apply_world(obj,posed(r,*pose),origin)
    return {"half_length":.203,"half_height":.043,"cap_depth":design[2]}

def geometry(s,strength=1.,open_cut=.060,design=DESIGN):
    p=json.loads(s["knight_mission_pose"]);pose=[p[k] for k in ("dx","dy","twist_degrees")]
    mane=planar_mane(pose,strength)
    skin=bpy.data.objects["Knight | continuous horse head and neck"]
    helper=bpy.data.objects["Knight | coherent skull cheek and conical muzzle"]
    bed=prepare_bed(skin,pose);subdivisions=subdivide(skin,pose)
    data={"mane":mane,"new_orbital_vertices":subdivisions,"eyes":{},"socket":{},"upper_cut_depth":open_cut,"orbital_tilt_and_crown":design}
    for obj in (skin,helper):data["socket"][obj.name]=shape_face(obj,pose,bed,open_cut,design)
    for side,name in [(-1,"near"),(1,"far")]:
        obj=bpy.data.objects["Knight | "+name+" eye"];data["eyes"][name]=inset_eye(obj,pose,bed,side,design)
    bpy.context.view_layer.update()
    return data

def flat(scene):
    for obj in visible_meshes(scene):
        for slot in obj.material_slots:slot.material=bpy.data.materials["Neutral satin clay"]
    for obj in scene.objects:
        if obj.type=="LIGHT":obj.hide_render=True
    mat=bpy.data.materials["Neutral satin clay"].node_tree.nodes["Principled BSDF"]
    mat.inputs["Base Color"].default_value=(.33,.35,.38,1);mat.inputs["Roughness"].default_value=.48
    for i,p in enumerate([(4,5,8),(4,-5,8),(-4,5,8),(-4,-5,8)]):
        l=bpy.data.lights.new("Clay bank "+str(i),"AREA");l.energy=440;l.shape="DISK";l.size=4.5
        ob=bpy.data.objects.new(l.name,l);scene.collection.objects.link(ob);ob.location=p
        ob.rotation_euler=(Vector((0,0,2.8))-ob.location).to_track_quat("-Z","Y").to_euler()

def comparisons(name,prefix):
    s=loaded(name);configure_render(s,40);s.render.resolution_percentage=64
    flat(s);render(s,OUT/(prefix+"clay-fixed.png"));use_side_camera(s);render(s,OUT/(prefix+"clay-side.png"))

def preview():
    s=loaded("parent.blend");geometry(s);configure_render(s,48);s.render.resolution_percentage=70
    render(s,OUT/"sculpt-fixed.png");use_side_camera(s);render(s,OUT/"sculpt-side.png")
    flat(s);render(s,OUT/"sculpt-clay.png")

def crop(s,box):
    x0,y0,x1,y1=box;s.render.use_border=True;s.render.use_crop_to_border=True
    s.render.border_min_x=(x0+.05)/1254;s.render.border_max_x=(x1+.05)/1254
    s.render.border_min_y=(1254-y1+.05)/1254;s.render.border_max_y=(1254-y0+.05)/1254

def aperture_test():
    designs=[(.26,.012,.048),(.48,.021,.049),(.69,.029,.051),(.91,.030,.052),
             (.42,.032,.057),(.62,.022,.059)]
    for i,params in enumerate(designs):
        s=loaded("parent.blend");geometry(s,design=params);configure_render(s,64)
        crop(s,(446,440,578,515));render(s,OUT/f"aperture-{i}-fixed.png")
        use_side_camera(s);crop(s,(580,275,737,376));render(s,OUT/f"aperture-{i}-side.png")
    json_file(OUT/"apertures.json",designs)

def reflector(scene,target,power,size):
    from probe_carving import point_probe
    from fit_eye_reflection import smooth_normal
    probe=point_probe(scene)
    candidates=[]
    x,y=target
    for dy in [0,-1,1,-2,2,-3,3,-4,4]:
        for dx in [0,-1,1,-2,2,-3,3]:
            hit=probe(x+dx,y+dy)
            if hit and hit[1].endswith("near eye"):
                candidates.append((dx*dx+dy*dy,x+dx,y+dy,hit))
    if not candidates:return {}
    _,cx,cy,hit=min(candidates,key=lambda a:a[0])
    _,name,point,fallback=hit
    n=smooth_normal(bpy.data.objects[name],point,fallback)
    eye=scene.camera.matrix_world.to_quaternion()@Vector((0,0,1))
    direction=(2*n.dot(eye)*n-eye).normalized()
    lamp=bpy.data.objects["Eye reflection upper"]
    lamp.location=point+.92*direction
    lamp.rotation_euler=(point-lamp.location).to_track_quat("-Z","Y").to_euler()
    lamp.data.energy=power;lamp.data.size=size
    bpy.context.view_layer.update()
    return {"lamp":lamp.name,"location":list(lamp.location),"energy":power,"diameter":size,
            "receivers":[o.name for o in lamp.light_linking.receiver_collection.objects],"anchor":[cx,cy]}

def facet_test():
    options=[(.07,.009,.053,.003,.30,.006),(.08,.012,.060,.005,.58,.009),
             (.09,.012,.058,.009,.82,.011),(.09,.008,.068,.005,.90,.009)]
    for i,params in enumerate(options):
        s=loaded("parent.blend");geometry(s,design=params);configure_render(s,80)
        reflector(s,(498,474),2.6,.138)
        crop(s,(446,440,578,515));render(s,OUT/f"facet-{i}-fixed.png")
        use_side_camera(s);crop(s,(580,275,737,376));render(s,OUT/f"facet-{i}-side.png")
        if i in (1,2):
            flat(s);render(s,OUT/f"facet-{i}-clay.png")
    json_file(OUT/"facets.json",options)

def final():
    s=loaded("parent.blend");data=geometry(s)
    data["existing_upper_eye_card"]=reflector(s,(498,474),.63,.139)
    data["parent_sha256"]=PARENT
    s["knight_improvement_005_B"]=json.dumps(data)
    configure_render(s,144);save_model(s,OUT/"knight.blend")
    s=loaded("knight.blend");configure_render(s,144)
    render(s,OUT/"wood.png");use_side_camera(s);render(s,OUT/"wood-side.png")
    data.update({"model_sha256":sha(OUT/"knight.blend"),"fixed_sha256":sha(OUT/"wood.png"),"side_sha256":sha(OUT/"wood-side.png"),"samples":144})
    json_file(OUT/"parameters.json",data)
    comparisons("knight.blend","")
    sys.path.insert(0,str(OUT));from diagnostics import diagnostics
    s=loaded("knight.blend");configure_render(s,32);diagnostics(s,"",True)
if __name__=="__main__":
    assert sha(OUT/"parent.blend")==PARENT
    if "--preview" in sys.argv:preview()
    if "--parent-flat" in sys.argv:comparisons("parent.blend","parent-")
    if "--apertures" in sys.argv:aperture_test()
    if "--facets" in sys.argv:facet_test()
    if "--final" in sys.argv:final()
