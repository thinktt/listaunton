"""Verify the delivered scene using the chess viewer's actual export and validation routines."""
from pathlib import Path
import hashlib,json,runpy,shutil,sys
import bpy,numpy as np
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/"scripts/knight"));sys.path.insert(0,str(OUT))
from mission_scene import sha,world_vertices
import export_mission
from probe import readings

def state(name):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/name),load_ui=False)
    s=bpy.context.scene;geo={};lights={}
    for obj in s.objects:
        if obj.type=="MESH":geo[obj.name]=hashlib.sha256(world_vertices(obj).tobytes()).hexdigest()
        elif obj.type=="LIGHT":lights[obj.name]=[list(np.array(obj.matrix_world).ravel()),obj.data.energy,obj.data.size]
    cam=s.camera
    return {"geometry":geo,"lights":lights,"camera":[list(np.array(cam.matrix_world).ravel()),cam.data.ortho_scale,
        cam.data.shift_x,cam.data.shift_y,s.render.resolution_x,s.render.resolution_y],
        "images":{i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file},
        "eye":readings(s)}

prev=state("parent.blend");cur=state("knight.blend")
assert prev["camera"]==cur["camera"] and prev["images"]==cur["images"]
geos=[o for o in prev["geometry"] if prev["geometry"][o]!=cur["geometry"][o]]
lamps=[o for o in prev["lights"] if prev["lights"][o]!=cur["lights"][o]]
assert lamps==["Eye reflection upper"]
s=bpy.context.scene
root=OUT/"review-copy";mdl=root/"models/knight";asset=root/"assets/knight"
mdl.mkdir(parents=True,exist_ok=True);asset.mkdir(parents=True,exist_ok=True)
source=mdl/"knight-rebuilt.blend"
shutil.copyfile(OUT/"knight.blend",source)
image=bpy.data.objects["Knight | near eye"].data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Base Color"].links[0].from_node.image
tex=asset/"walnut.png";tex.write_bytes(bytes(image.packed_file.data))
export_mission.ROOT=root
export_mission.export(s,tex,output=asset,source=source)
sys.argv=["validate.py","--",str(root)]
runpy.run_path(str(ROOT/"scripts/knight/validate.py"),run_name="__main__")
validation=json.loads((asset/"validation.json").read_text())
out={"candidate_sha256":sha(OUT/"knight.blend"),"parent_sha256":sha(OUT/"parent.blend"),
    "actual_repository_mesh_and_viewer_export_validation":validation,"camera_unchanged":True,
    "packed_images_unchanged":True,"geometry_changes":geos,"light_changes":lamps,
    "eye_visible_fixed_2px_samples":{"parent":prev["eye"]["count"],"candidate":cur["eye"]["count"]},
    "eye_visible_bounds":{"parent":prev["eye"]["bounds"],"candidate":cur["eye"]["bounds"]}}
(OUT/"verified.json").write_text(json.dumps(out,indent=2)+"\n")
