"""Pack a scoped pigment grade into its actual Blender scene and render both views."""
from pathlib import Path
import argparse
import json
import sys
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from mission_scene import BUILD,configure_render,json_file,render,save_model,sha,use_side_camera,visible_meshes


def main():
    p=argparse.ArgumentParser();p.add_argument("--carving",required=True);p.add_argument("--variant",required=True)
    opt=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    out=BUILD/opt.variant;source=BUILD/opt.carving/"knight.blend"
    grade=json.loads((out/"grade.json").read_text())
    assert sha(source)==grade["source_sha256"]
    pigment=out/"pigment.png";raw=pigment.read_bytes()
    assert sha(pigment)==grade["pigment_sha256"]
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);scene=bpy.context.scene
    mat=visible_meshes(scene)[0].data.materials[0]
    source_node=mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].links[0].from_node
    prior=source_node.image
    fresh=bpy.data.images.load(str(pigment),check_existing=False)
    fresh.name="Knight | walnut on carved muzzle and eyes";fresh.colorspace_settings.name="sRGB"
    fresh.pack(data=raw,data_len=len(raw));source_node.image=fresh
    if prior.users==0:bpy.data.images.remove(prior)
    scene["knight_pigment_grade"]=json.dumps(grade)
    configure_render(scene,144);save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False);scene=bpy.context.scene
    saved=visible_meshes(scene)[0].data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Base Color"].links[0].from_node.image
    assert bytes(saved.packed_file.data)==raw
    configure_render(scene,144);render(scene,out/"wood.png");use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",{**grade,"samples":144,"reopened_packed_bytes_match":True})
    print("KNIGHT_GRADED_WOOD_REOPENED",sha(out/"knight.blend"),flush=True)


if __name__=="__main__":main()
