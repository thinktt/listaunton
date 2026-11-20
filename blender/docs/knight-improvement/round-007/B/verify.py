"""Verify the delivered scene using the chess viewer's actual export and validation routines."""
from pathlib import Path
import hashlib,json,runpy,shutil,sys
import bpy,numpy as np
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/"scripts/knight"));sys.path.insert(0,str(OUT))
from mission_scene import sha,world_vertices
import export_mission
from refine_eye import count_eye_pixels

def state(name):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/name),load_ui=False)
    s=bpy.context.scene;geo={};lights={};topology={};surface_data={};uvs_digest={}
    for obj in s.objects:
        if obj.type=="MESH":
            geo[obj.name]=hashlib.sha256(world_vertices(obj).tobytes()).hexdigest()
            mesh=obj.data
            loops=np.empty(len(mesh.loops),np.int32)
            mesh.loops.foreach_get("vertex_index",loops)
            starts=np.empty(len(mesh.polygons),np.int32)
            mesh.polygons.foreach_get("loop_start",starts)
            topology[obj.name]=hashlib.sha256(loops.tobytes()+starts.tobytes()).hexdigest()
            digest=hashlib.sha256()
            for uvs in mesh.uv_layers:
                uv=np.empty((len(uvs.data),2),np.float32)
                uvs.data.foreach_get("uv",uv.ravel())
                digest.update(uvs.name.encode()+uv.tobytes())
            uvs_digest[obj.name]=digest.hexdigest()
            for attr in mesh.attributes:
                if attr.name in ("Knight varnish coverage","varnish"):
                    a=np.empty(len(attr.data),np.float32)
                    attr.data.foreach_get("value",a)
                    digest.update(a.tobytes())
            surface_data[obj.name]=digest.hexdigest()
        elif obj.type=="LIGHT":lights[obj.name]=[list(np.array(obj.matrix_world).ravel()),obj.data.energy,obj.data.size]
    cam=s.camera
    skull=world_vertices(s.objects['Knight | continuous horse head and neck'])
    return {"geometry":geo,"lights":lights,"topology":topology,"surface_data":surface_data,"uvs":uvs_digest,
        "upper_points":skull[skull[:,2]>=3.36],
        "camera":[list(np.array(cam.matrix_world).ravel()),cam.data.ortho_scale,
        cam.data.shift_x,cam.data.shift_y,s.render.resolution_x,s.render.resolution_y],
        "images":{i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file},
        "eye":count_eye_pixels(s)}

prev=state("parent.blend");cur=state("knight.blend")
assert prev["camera"]==cur["camera"] and prev["images"]==cur["images"]
assert prev["topology"]==cur["topology"] and prev["uvs"]==cur["uvs"]
finish=[obj for obj in prev["surface_data"] if prev["surface_data"][obj]!=cur["surface_data"][obj]]
assert set(finish)<={"Knight | continuous horse head and neck"}
upper_displacement=float(np.linalg.norm(prev["upper_points"]-cur["upper_points"],axis=1).max())
assert upper_displacement<1.e-6
geos=[o for o in prev["geometry"] if prev["geometry"][o]!=cur["geometry"][o]]
lamps=[o for o in prev["lights"] if prev["lights"][o]!=cur["lights"][o]]
assert set(lamps)<={"Eye reflection lower"}
assert set(geos)=={"Knight | continuous horse head and neck","Knight | curved neck and chest"}
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
    "packed_images_unchanged":True,"all_mesh_topology_unchanged":True,
    "all_mesh_uvs_unchanged":True,"varnish_changes":finish,"geometry_changes":geos,"light_changes":lamps,
    "max_skull_world_displacement_above_3_36":upper_displacement,
    "eye_visible_fixed_2px_samples":{"parent":prev["eye"]["visible_samples"],"candidate":cur["eye"]["visible_samples"]},
    "eye_visible_bounds":{"parent":prev["eye"]["bounds"],"candidate":cur["eye"]["bounds"]}}
(OUT/"verified.json").write_text(json.dumps(out,indent=2)+"\n")
