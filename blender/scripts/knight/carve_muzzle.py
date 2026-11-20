"""Shape the conical snout and carve paired nostrils and the mouth into the wood."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
import bpy

sys.path.insert(0,str(Path(__file__).parent))
from fit_muzzle_profile import carved_profile, muzzle_shape
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import BUILD,MODEL,configure_render,json_file,render,save_model,sha,use_side_camera,visible_meshes,world_vertices
from probe_carving import point_probe
from refine_eye import apply_world

MOUTH=[(533,481),(549,490),(570,498),(594,504),(619,508),(643,509),(662,507),(677,502),(686,498)]
NOSTRIL=[(668,505),(678,500),(685,496),(691,497),(698,501),(704,505),(709,509),(712,512)]


def rest_curve(probe,pixels,pose):
    hits=[]
    for x,y in pixels:
        hit=probe(x,y)
        assert hit and hit[1].endswith("continuous horse head and neck"),(x,y,hit)
        hits.append(list(hit[2]))
    points=rest_coords(np.array(hits),pose)
    assert np.all(np.diff(points[:,0])>0)
    return points


def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,default=MODEL)
    p.add_argument("--fit",type=Path,default=BUILD/"muzzle-study/profile-fit.json")
    p.add_argument("--variant",default="018-carved-muzzle")
    p.add_argument("--nostril-depth",type=float,default=.112)
    p.add_argument("--mouth-depth",type=float,default=.036)
    p.add_argument("--nostril-width",type=float,default=.036)
    p.add_argument("--lip-size",type=float,default=.027)
    p.add_argument("--cut-slope",type=float,default=.30)
    p.add_argument("--samples",type=int,default=144)
    args=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    out=BUILD/args.variant;out.mkdir(parents=True,exist_ok=True)
    fit=json.loads(args.fit.read_text());assert sha(args.source)==fit["source_sha256"]
    bpy.ops.wm.open_mainfile(filepath=str(args.source),load_ui=False);scene=bpy.context.scene
    skin=bpy.data.objects["Knight | continuous horse head and neck"]
    parts=(skin,bpy.data.objects["Knight | coherent skull cheek and conical muzzle"])
    pose=fit["pose"]
    for obj in parts:
        rest=rest_coords(world_vertices(obj),pose)
        reshaped=muzzle_shape(rest,fit["advance_lift_underdrop_width"])
        apply_world(obj,posed(reshaped,*pose))
    bpy.context.view_layer.update()
    probe=point_probe(scene)
    nose=rest_curve(probe,NOSTRIL,pose)
    mouth=rest_curve(probe,MOUTH,pose)
    change={}
    for obj in parts:
        rest=rest_coords(world_vertices(obj),pose)
        nose_relief=carved_profile(rest,nose,args.nostril_width,args.nostril_depth,args.lip_size)
        mouth_relief=carved_profile(rest,mouth,.025,args.mouth_depth,min(.013,.28*args.mouth_depth))
        # Blend at the shared corner so neither recess is cut twice.
        incision=np.minimum(np.minimum(nose_relief,mouth_relief),0)+np.maximum(np.maximum(nose_relief,mouth_relief),0)
        side=np.sign(rest[:,1])
        rest[:,1]+=incision*side
        rest[:,2]+=args.cut_slope*incision
        apply_world(obj,posed(rest,*pose))
        change[obj.name]={"affected_vertices":int((abs(incision)>.002).sum()),
                          "deepest_incision":float(incision.min()),"highest_lip":float(incision.max())}
    bpy.context.view_layer.update()
    cfg={"source_sha256":sha(args.source),"samples":args.samples,"profile":fit,"mouth_pixels":MOUTH,"nostril_pixels":NOSTRIL,
         "mouth_curve_rest":mouth.tolist(),"nostril_curve_rest":nose.tolist(),"nostril_depth":args.nostril_depth,
         "mouth_depth":args.mouth_depth,"nostril_width":args.nostril_width,"lip_size":args.lip_size,
         "cut_slope":args.cut_slope,"change":change,"method":"Fit the nose envelope to the black original. Carve paired narrow channels and rolled lips in the actual skull and continuous surface using detail landmarks from black candidate 2."}
    scene["knight_muzzle_carving"]=json.dumps(cfg)
    configure_render(scene,args.samples);save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False);scene=bpy.context.scene
    configure_render(scene,args.samples);render(scene,out/"wood.png")
    use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",cfg)
    print("KNIGHT_MUZZLE_REOPENED",change,flush=True)


if __name__=="__main__":main()
