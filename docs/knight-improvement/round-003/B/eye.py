"""Round 3B. Blend a shallow orbital bed and a broad, soft lower lid into the skull."""
import json, math, sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/"scripts/knight"))
from mission_scene import configure_render, json_file, render, save_model, sha, use_side_camera, visible_meshes, world_vertices
from mission_pose import posed
from refine_eye import apply_world,unpose
PARENT="709fb263f2cdf079c1a645002064ce83b72ff6b15faea2a9d8e8a19adfdd4dfb"
CROP=(440,435,584,530)
def ease(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)

def open_blend(name):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/name),load_ui=False)
    return bpy.context.scene

def setup(scene):
    pose=json.loads(scene["knight_mission_pose"])
    args=[pose[k] for k in ("dx","dy","twist_degrees")]
    along=np.array([1.,-.76]);along/=np.linalg.norm(along)
    across=np.array([-along[1],along[0]])
    surfaces=[]
    for suffix in ("continuous horse head and neck","coherent skull cheek and conical muzzle","near eye","far eye"):
        obj=bpy.data.objects["Knight | "+suffix]
        w=world_vertices(obj)
        r=unpose(w,pose)
        xz=r[:,[0,2]]-[.42,4.155]
        surfaces.append((obj,r,w,xz@along,xz@across,suffix.endswith("eye")))
    def sculpt(k):
        amp,offset,width,bed,tilt,*extra=k
        lift=extra[0] if extra else 0
        steep,roll,focus=extra[1:4] if len(extra)>=4 else (0,0,0)
        back,up=extra[4:6] if len(extra)>=6 else (0,0)
        moved={}
        for obj,rest,w,u,v,eye in surfaces:
            r=rest.copy()
            side=np.sign(r[:,1])
            wall=ease((abs(r[:,1])-.13)/.15)
            local=ease((.37-abs(u))/.16)*ease((.235-abs(v))/.105)*wall
            taper=ease((abs(u)-.085)/.11)
            # A mild skew and taper within the socket keep the ocular surface
            # close to its existing corners and under the brow.
            du=.026*u+back
            dv=-tilt*u-.14*taper*v+.005+up
            r[:,0]+=local*(du*along[0]+dv*across[0])
            r[:,2]+=local*(du*along[1]+dv*across[1])
            r[:,1]+=side*local*(.026*u-.003)
            oval=np.exp(-((u/.177)**2+(v/.079)**2))
            if eye:
                # Ease the crown toward its new bed and submerge the sharp
                # lateral edges before they can leave a dark outline.
                r[:,1]-=side*(.009+.010*taper)*local
                # Very shallow shaping of the upper crown determines where
                # the inherited studio softboxes catch the polished eye.
                # The tapered ends stay seated as this central plane turns.
                crown=np.exp(-((u+.025)/.18)**4)
                r[:,1]+=side*crown*(steep*(u+.035)+roll*v+focus*np.exp(-((u+.035)/.095)**2-(v/.053)**2))
            else:
                # Fill the deepest part of the socket. Restore the lower
                # eyelid as a wide rolling plane, fading into the cheek.
                r[:,1]+=side*bed*oval*wall
                length=ease((u+.29)/.15)*ease((.34-u)/.15)
                axis=-.126+1.50*(u-.055)**2
                broad=np.exp(-((v-axis-offset)/width)**2)
                r[:,1]+=side*amp*broad*length*wall
                # The cheek below the socket blends upward into the rim. A
                # broad falloff protects the underjaw and adjoining panels.
                r[:,2]+=lift*length*wall*np.exp(-((v-axis+.10)/.122)**2)
            result=w+posed(r,*args)-posed(rest,*args)
            distance=np.linalg.norm(result-w,axis=1)
            moved[obj.name]={"count_above_0.0001":int(np.sum(distance>.0001)),"max":float(max(distance))}
            apply_world(obj,result)
        bpy.context.view_layer.update()
        return moved
    return sculpt

def crop(scene):
    x0,y0,x1,y1=CROP
    scene.render.use_border=True;scene.render.use_crop_to_border=True
    scene.render.border_min_x=(x0+.05)/1254;scene.render.border_max_x=(x1+.05)/1254
    scene.render.border_min_y=(1254-y1+.05)/1254;scene.render.border_max_y=(1254-y0+.05)/1254

def test(extra=False):
    s=open_blend("parent.blend")
    sculpt=setup(s)
    configure_render(s,64);crop(s)
    options=[
        [.020,-.065,.082,.034,.051],[.039,-.065,.082,.040,.051],
        [.056,-.065,.082,.040,.051],[.039,-.037,.072,.048,.051],
        [.033,-.084,.085,.052,.051],[.045,-.060,.110,.038,.051],
        [-.026,.035,.080,.055,.051],[-.040,.019,.078,.055,.051]]
    if extra:
        options=[
            [-.019,.027,.095,.045,.040,.065],[-.029,.024,.084,.042,.043,.060],
            [-.019,.025,.089,.041,.043,.105],[-.031,.020,.084,.037,.043,.102],
            [-.045,.020,.084,.042,.041,.080],[-.048,.004,.078,.045,.038,.078],
            [-.042,-.011,.083,.040,.038,.074],[-.039,-.024,.079,.042,.038,.077],
            [-.052,.005,.096,.039,.030,.043],[-.051,-.011,.1,.040,.031,.07]]
    for i,k in enumerate(options,start=10 if extra else 0):
        sculpt(k)
        render(s,OUT/f"study-{i}.png")
    json_file(OUT/("extra.json" if extra else "trials.json"),options)

def lens_test():
    s=open_blend("parent.blend");sculpt=setup(s);configure_render(s,96);crop(s)
    values=[]
    for du in [-.13,-.04,.06,.16]:
        for dv in [-.30,-.12,.06,.24]:
            values.append([-.018,.026,.094,.043,.038,.057,du,dv,.004])
    for i,k in enumerate(values):
        sculpt(k);render(s,OUT/f"lens-{i:02d}.png")
    json_file(OUT/"lens-tests.json",values)

def eye_card(scene,aim,power,size):
    from probe_carving import point_probe
    from fit_eye_reflection import smooth_normal
    hit=point_probe(scene)(*aim)
    assert hit[1]=="Knight | near eye",hit[1]
    _,name,point,fallback=hit
    n=smooth_normal(bpy.data.objects[name],point,fallback)
    view=scene.camera.matrix_world.to_quaternion()@Vector((0,0,1))
    reflection=(2*n.dot(view)*n-view).normalized()
    light=bpy.data.objects["Eye reflection upper"]
    # The parent already has a stationary physical reflector for both
    # polished eyes. Its position is set once; it never follows the camera.
    light.location=point+1.15*reflection
    light.rotation_euler=(point-light.location).to_track_quat("-Z","Y").to_euler()
    light.data.energy=power;light.data.size=size
    bpy.context.view_layer.update()
    return {"position":list(light.location),"energy":power,"disk_diameter":size,
            "receivers":[o.name for o in light.light_linking.receiver_collection.objects]}

def finish_test():
    s=open_blend("parent.blend");sculpt=setup(s);configure_render(s,96);crop(s)
    k=[-.018,.026,.094,.043,.050,.057,-.10,-.15,.004]
    sculpt(k)
    options=[([497,473],7,.24),([498,474],13,.23),([500,474],13,.27),([498,472],18,.32),
             ([499,474],20,.24),([496,473],14,.18)]
    for i,(point,energy,size) in enumerate(options):
        eye_card(s,point,energy,size);render(s,OUT/f"finish-{i}.png")
    json_file(OUT/"finish-tests.json",{"physical_profile":k,"cards":options})

def final():
    s=open_blend("parent.blend")
    params=json.loads((OUT/"selected.json").read_text())
    moved=setup(s)(params["physical_profile"])
    detail={"parent_sha256":PARENT,"basis":["lower_plane_height","lower_plane_offset","lower_plane_width","socket_fill","tilt",
        "cheek_lift","lens_longitudinal_slope","lens_cross_slope","lens_crown","lens_back","lens_up"],
        "physical_profile":params["physical_profile"],"moved":moved}
    if "polish_card" in params:
        detail["polish_card"]=eye_card(s,*params["polish_card"])
    s["knight_improvement_003_B"]=json.dumps(detail)
    configure_render(s,144);save_model(s,OUT/"knight.blend")
    s=open_blend("knight.blend");configure_render(s,144)
    render(s,OUT/"wood.png");use_side_camera(s);render(s,OUT/"wood-side.png")
    detail.update({"model_sha256":sha(OUT/"knight.blend"),"fixed_sha256":sha(OUT/"wood.png"),
        "side_sha256":sha(OUT/"wood-side.png"),"reopened_samples":144})
    json_file(OUT/"parameters.json",detail)
    # Match the physically centered camera bank used on the accepted parent.
    sys.path.insert(0,str(OUT))
    from diagnostics import diagnostics
    s=open_blend("knight.blend");configure_render(s,32);diagnostics(s,"",True)

if __name__=="__main__":
    assert sha(OUT/"parent.blend")==PARENT
    if "--test" in sys.argv:test()
    if "--refine" in sys.argv:test(True)
    if "--lens" in sys.argv:lens_test()
    if "--finish-test" in sys.argv:finish_test()
    if "--final" in sys.argv:final()
