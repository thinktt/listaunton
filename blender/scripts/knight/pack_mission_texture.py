"""Load the exact delivery PNG into a fresh image and verify packed bytes."""
from pathlib import Path
import argparse
import hashlib
import shutil
import sys

import bpy

sys.path.insert(0,str(Path(__file__).parent))
from mission_scene import BUILD,configure_render,render,save_model,sha,use_side_camera,json_file
from complete_pedestal_bake import check_coverage


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",default="007-complete-atlas")
    parser.add_argument("--variant",default="008-packed-walnut")
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    src=BUILD/args.source;out=BUILD/args.variant;out.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(src/"knight.blend"),load_ui=False)
    scene=bpy.context.scene
    mat=bpy.data.objects["Knight | turned pedestal"].data.materials[0]
    target=mat.node_tree.nodes["Knight delivered albedo"]
    previous=target.image
    shutil.copyfile(src/"pigment.png",out/"pigment.png")
    raw=(out/"pigment.png").read_bytes()
    fresh=bpy.data.images.load(str(out/"pigment.png"),check_existing=False)
    fresh.name="Knight walnut | checked pigment"
    fresh.colorspace_settings.name="sRGB"
    fresh.pack(data=raw,data_len=len(raw))
    target.image=fresh
    if previous.users==0:bpy.data.images.remove(previous)
    scene["knight_atlas_sha256"]=hashlib.sha256(raw).hexdigest()
    configure_render(scene,64);save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False)
    scene=bpy.context.scene
    mat=bpy.data.objects["Knight | turned pedestal"].data.materials[0]
    saved=mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].links[0].from_node.image
    assert saved.packed_file and bytes(saved.packed_file.data)==raw
    coverage=check_coverage(scene,saved)
    configure_render(scene,64);render(scene,out/"wood.png")
    use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",{"source_sha256":sha(src/"knight.blend"),
              "texture_sha256":sha(out/"pigment.png"),"saved_sha256":sha(out/"knight.blend"),
              "packed_bytes_exact":True,"reopened_triangle_coverage":coverage,"samples":64})
    print("KNIGHT_CHECKED_ATLAS_RENDERED",flush=True)


if __name__=="__main__":main()
