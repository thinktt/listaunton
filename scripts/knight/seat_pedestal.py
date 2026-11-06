"""Register the turning axis and carry the bottom of the carving with its seat."""
from pathlib import Path
import argparse
import json
import sys
import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from export_mission import export
from mission_scene import ASSETS,BUILD,configure_render,json_file,render,save_model,sha,use_side_camera,world_vertices
from refine_eye import apply_world


def main():
    p=argparse.ArgumentParser();p.add_argument("--source",required=True,type=Path);p.add_argument("--fit",required=True,type=Path)
    p.add_argument("--variant",required=True);a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    out=BUILD/a.variant;out.mkdir(exist_ok=True);fit=json.loads(a.fit.read_text())
    assert sha(a.source)==fit["source_sha256"];dx=fit["selected"]["world_x"]
    assert abs(dx)<.055
    bpy.ops.wm.open_mainfile(filepath=str(a.source),load_ui=False);scene=bpy.context.scene
    foot=bpy.data.objects["Knight | turned pedestal"];assert abs(foot.location.x)<1e-6
    foot.location.x+=dx
    moved={}
    for ob in scene.objects:
        if ob.type!="MESH" or ob==foot:continue
        co=world_vertices(ob);t=np.clip((2.48-co[:,2])/(2.48-1.76),0,1)
        w=t*t*(3-2*t)
        if np.any(w>0):
            co[:,0]+=dx*w;apply_world(ob,co);moved[ob.name]=int(np.sum(w>0))
    bpy.context.view_layer.update()
    scene["knight_foot_center_x"]=dx
    cfg={"source_sha256":sha(a.source),"samples":112,"center_fit":fit["selected"],"carried_lower_vertices":moved,
         "lower_seat_rigid_through_z":1.76,"carving_fixed_above_z":2.48,
         "method":"A small physical X offset fits the shared round pedestal to the visible original. The carving follows rigidly at the wood joint and tapers to its previous position above it. Keep the 54-degree camera, aperture size, base diameter, floor and high points."}
    scene["knight_foot_seating"]=json.dumps(cfg)
    configure_render(scene,112);save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False);scene=bpy.context.scene
    configure_render(scene,112);tex=ASSETS/json.loads((ASSETS/"mission-checkpoint.json").read_text())["texture_file"]
    export(scene,tex,output=out,source=out/"knight.blend")
    render(scene,out/"wood.png");use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",cfg);print("KNIGHT_REGISTERED_FOOT",dx,moved,flush=True)


if __name__=="__main__":main()
