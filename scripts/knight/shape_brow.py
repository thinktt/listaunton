"""Broaden and seat the swept ear/brow on both sides of the carved head."""
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from mission_pose import posed
from mission_scene import BUILD,configure_render,json_file,render,save_model,sha,use_side_camera,visible_meshes,world_vertices
from refine_eye import apply_world,count_eye_pixels,unpose


def main():
    source=BUILD/"010-convex-eye/knight.blend";out=BUILD/"011-seated-brow";out.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;pose=json.loads(scene["knight_mission_pose"])
    params=[pose["dx"],pose["dy"],pose["twist_degrees"]]
    # Rest-space offsets for the seven existing cross sections. The pointed
    # rear seats into the mane; the nose end slopes into the frontal ridge.
    dx=np.array([-.174,-.115,-.068,-.035,-.008,.032,.075])
    dz=np.array([.053,.050,.060,.050,.033,-.040,-.198])
    depth=np.array([-.118,-.085,-.042,.005,.022,.035,-.018])
    rise=np.array([1.12,1.26,1.32,1.36,1.30,1.25,1.0])
    for side,name in [(-1,"near"),(1,"far")]:
        obj=bpy.data.objects["Knight | "+name+" swept ear"]
        rings=unpose(world_vertices(obj),pose).reshape(7,64,3)
        for i,ring in enumerate(rings):
            center=ring.mean(0)
            ring[:,0]+=dx[i]
            ring[:,1]=center[1]+(ring[:,1]-center[1])*1.12+side*depth[i]
            ring[:,2]=center[2]+(ring[:,2]-center[2])*rise[i]+dz[i]
        apply_world(obj,posed(rings.reshape(-1,3),*params))
    bpy.context.view_layer.update()
    cfg={"source_sha256":sha(source),"x_offsets":dx.tolist(),"z_offsets":dz.tolist(),"lateral_offsets":depth.tolist(),
         "vertical_scales":rise.tolist(),"eye_visibility":count_eye_pixels(scene),
         "method":"Extend the mane-end point, widen the blade and lower the tip into the forehead symmetrically, using the original and selected side-face landmarks."}
    scene["knight_brow_trial"]=json.dumps(cfg,sort_keys=True)
    configure_render(scene,64);save_model(scene,out/"knight.blend");render(scene,out/"wood.png")
    wood=visible_meshes(scene)[0].data.materials[0];clay=bpy.data.materials["Neutral satin clay"]
    for obj in visible_meshes(scene):obj.data.materials[0]=clay
    render(scene,out/"neutral.png")
    for obj in visible_meshes(scene):obj.data.materials[0]=wood
    use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",cfg)
    print("KNIGHT_BROW_RENDERED",cfg["eye_visibility"],flush=True)


if __name__=="__main__":main()
