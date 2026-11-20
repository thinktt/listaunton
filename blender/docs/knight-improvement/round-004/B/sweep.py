"""Extend the lower mane into a jointly modelled, convex back of the neck."""
from pathlib import Path
import json,sys
import bpy
import numpy as np
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/"scripts/knight"))
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import configure_render, json_file,render, save_model, sha, use_side_camera, world_vertices
from refine_eye import apply_world

PARENT="6d06b1ca5d781bcca921e5745f10504ab1113aae983571704a979964a934c177"
SUFFIX=["swept rounded mane","continuous horse head and neck","curved neck and chest"]
def ease(x):
    x=np.clip(x,0,1)
    return x*x*(3-2*x)

def setup(scene):
    placement=json.loads(scene["knight_mission_pose"])
    pose=[placement[k] for k in ("dx","dy","twist_degrees")]
    objects=[]
    for name in SUFFIX:
        obj=bpy.data.objects["Knight | "+name];world=world_vertices(obj)
        objects.append((name,obj,world,rest_coords(world,pose)))
    def change(values):
        rear,spread,drop,support,root_flare,*tuning=values
        station,root=tuning[:2] if tuning else (0.,0.)
        feather=tuning[2] if len(tuning)>2 else 0.
        metrics={}
        for name,obj,world,original in objects:
            r=original.copy()
            if name=="swept rounded mane":
                rings=r.reshape(13,64,3)
                # Preserve the established arch; ease its lower four stations
                # backwards, down and wider in three dimensions. The last,
                # narrower station finishes inside the enlarged neck root.
                for i,ring in enumerate(rings):
                    if i<8:continue
                    j=i-8
                    mid=original.reshape(13,64,3)[i].mean(0)
                    radial=ring[:,1]-mid[1]
                    ring[:,0]+=[.017, (-.065+.070*station)*rear, (-.155+.062*station)*rear,
                                -.172*rear-.034*feather, -.090*rear][j]
                    ring[:,2]-=drop*[.003,.042-.034*station,.098-.047*station,.174+.044*feather,.223-.045*feather][j]
                    ring[:,1]+=spread*[.00,.13-.110*station,.34-.145*station,.43,-.05][j]*radial
                    # At the tip, soften the cross-section edge and taper
                    # behind the wider neck. Keep the closed topology and UVs.
                    ring[:,0]+=[0,.015,.08,-.005,-.24][j]*rear*(ring[:,0]-mid[0])
            else:
                x,y,z=original.T
                back=ease((-x-.16)/.60)
                rise=ease((z-1.70)/.32)*(1-ease((z-2.82)/.76))
                fullness=support*rise*(.033+.114*np.exp(-((z-2.18)/.58)**2))*back
                broad=.277*support*ease((z-1.63)/.52)*(1-ease((z-2.25)/1.13))*back
                fullness=fullness*(1-root)+broad*root
                # Under the feather the wood opens into a shallow one-piece
                # haunch. Ease this support in above the turned seat.
                fullness+=feather*.053*np.exp(-((z-1.88)/.16)**2)*ease((z-1.64)/.13)*back
                r[:,0]-=fullness
                r[:,1]+=root_flare*rise*back*y*.090
            new=world+(posed(r,*pose)-posed(original,*pose))
            distance=np.linalg.norm(new-world,axis=1)
            apply_world(obj,new)
            metrics[name]={"displaced_vertices":int(np.sum(distance>.0001)),"max_displacement":float(np.max(distance))}
        bpy.context.view_layer.update()
        return metrics
    return change

def loaded(name):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/name),load_ui=False)
    return bpy.context.scene

def test(refined=False):
    s=loaded("parent.blend");sculpt=setup(s);configure_render(s,32)
    s.render.resolution_percentage=55
    camera=s.camera
    state=(camera.matrix_world.copy(),camera.data.ortho_scale,camera.data.shift_x,camera.data.shift_y)
    options=[
        [.65,.50,.64,.70,.60],[.82,.72,.82,.90,.80],[.95,.90,1.0,1.0,1.0],
        [1.12,1.0,1.1,1.20,1.0],[.72,1.15,.99,.94,.85]]
    if refined:
        options=[[.68,.70,1.08,.90,.65,1.,1.],
                 [.79,.82,1.20,1.02,.87,1.,1.],
                 [.90,.95,1.22,1.10,.90,1.,1.],
                 [.80,.78,1.20,1.21,1.03,.84,1.],
                 [.66,1.09,1.19,1.05,.70,.85,.80]]
    for i,val in enumerate(options,start=5 if refined else 0):
        sculpt(val)
        camera.matrix_world=state[0]
        camera.data.ortho_scale,camera.data.shift_x,camera.data.shift_y=state[1:]
        bpy.context.view_layer.update()
        render(s,OUT/f"test-{i}-fixed.png")
        use_side_camera(s);render(s,OUT/f"test-{i}-side.png")
    json_file(OUT/("refined-options.json" if refined else "options.json"),options)

def build():
    s=loaded("parent.blend");val=json.loads((OUT/"selected.json").read_text())
    report={"parent_sha256":PARENT,"names":["mane_setback","mane_width","extension","neck_fullness","neck_width",
        "lower_station_focus","broad_root_weight","mane_tip_feather"],
            "values":val,"mesh_scope":setup(s)(val)}
    s["knight_improvement_004_B"]=json.dumps(report)
    configure_render(s,144);save_model(s,OUT/"knight.blend")
    s=loaded("knight.blend");configure_render(s,144)
    render(s,OUT/"wood.png");use_side_camera(s);render(s,OUT/"wood-side.png")
    report.update({"model_sha256":sha(OUT/"knight.blend"),"fixed_sha256":sha(OUT/"wood.png"),
        "side_sha256":sha(OUT/"wood-side.png"),"reopened_samples":144})
    json_file(OUT/"parameters.json",report)
    sys.path.insert(0,str(OUT))
    from diagnostics import diagnostics
    s=loaded("knight.blend");configure_render(s,32);diagnostics(s,"",True)

if __name__=="__main__":
    assert sha(OUT/"parent.blend")==PARENT
    if "--test" in sys.argv:test()
    if "--refine" in sys.argv:test(True)
    if "--final" in sys.argv:build()
