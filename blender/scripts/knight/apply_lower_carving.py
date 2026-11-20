"""Apply the fitted lower-depth correction and clear the upper eyelid."""
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from mission_scene import BUILD,configure_render,json_file,render,save_model,sha,use_side_camera,visible_meshes,world_vertices
from mission_pose import posed
from lower_carving_fit import lower_offset,rest_coords
from refine_eye import apply_world,count_eye_pixels


def main():
    source=BUILD/"011-seated-brow/knight.blend";out=BUILD/"012-lower-carving"
    cfg=json.loads((out/"fit.json").read_text())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;cfg_pose=json.loads(scene["knight_mission_pose"])
    pose=[cfg_pose["dx"],cfg_pose["dy"],cfg_pose["twist_degrees"]]
    params=[cfg["forward"],cfg["mane_width_gain"],cfg["mane_rear_offset"]]
    for obj in scene.objects:
        if obj.type!="MESH" or "pedestal" in obj.name or obj.name.endswith(" eye"):continue
        world=world_vertices(obj);rest=rest_coords(world,pose)
        if obj.name.endswith("swept ear"):
            side=-1 if "near" in obj.name else 1
            rings=rest.reshape(7,64,3)
            for i,dy,dz in [(4,-.012,.020),(5,-.046,.079),(6,0,.040)]:
                rings[i,:,1]+=side*dy;rings[i,:,2]+=dz
            rest=rings.reshape(-1,3)
        else:
            rest=lower_offset(rest,"mane" in obj.name,params)
            assert np.array_equal(rest[:,2],world[:,2])
        apply_world(obj,posed(rest,*pose))
    bpy.context.view_layer.update()
    cfg["source_sha256"]=sha(source);cfg["eye_visibility"]=count_eye_pixels(scene)
    cfg["brow_adjustment"]="Raise the forward blade enough to expose the observed upper eye glint; preserve the length and seated tip."
    scene["knight_lower_carving"]=json.dumps(cfg,sort_keys=True)
    configure_render(scene,64);save_model(scene,out/"knight.blend");render(scene,out/"wood.png")
    wood=visible_meshes(scene)[0].data.materials[0];clay=bpy.data.materials["Neutral satin clay"]
    for obj in visible_meshes(scene):obj.data.materials[0]=clay
    render(scene,out/"neutral.png")
    for obj in visible_meshes(scene):obj.data.materials[0]=wood
    use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",cfg);print("KNIGHT_LOWER_CARVING_DONE",cfg["eye_visibility"],flush=True)


if __name__=="__main__":main()
