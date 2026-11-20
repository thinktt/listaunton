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
    s=bpy.context.scene;geo={};lights={};topology={};surface_data={};uvs_digest={};heights={}
    dg=bpy.context.evaluated_depsgraph_get()
    for obj in s.objects:
        if obj.type=="MESH":
            geo[obj.name]=hashlib.sha256(world_vertices(obj).tobytes()).hexdigest()
            if not obj.hide_render:
                evaluated=obj.evaluated_get(dg)
                post=evaluated.to_mesh()
                points=np.empty((len(post.vertices),3),np.float32)
                post.vertices.foreach_get('co',points.ravel())
                matrix=np.asarray(evaluated.matrix_world)
                worldz=points@matrix[2,:3]+matrix[2,3]
                heights[obj.name]=[float(worldz.min()),float(worldz.max())]
                evaluated.to_mesh_clear()
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
        elif obj.type=="LIGHT":
            lamp=obj.data
            lights[obj.name]=[list(np.array(obj.matrix_world).ravel()),lamp.energy,list(lamp.color),
                getattr(lamp,'size',None),getattr(lamp,'size_y',None),getattr(lamp,'shape',None),getattr(lamp,'spread',None)]
    cam=s.camera
    skull=world_vertices(s.objects['Knight | continuous horse head and neck'])
    return {"geometry":geo,"lights":lights,"topology":topology,"surface_data":surface_data,"uvs":uvs_digest,
        "skull":skull,"evaluated_z":heights,
        "camera":[list(np.array(cam.matrix_world).ravel()),cam.data.ortho_scale,
        cam.data.shift_x,cam.data.shift_y,s.render.resolution_x,s.render.resolution_y],
        "images":{i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file},
        "eye":count_eye_pixels(s)}

prev=state("parent.blend");cur=state("knight.blend")
assert prev["camera"]==cur["camera"]
old_image='Knight walnut | figured cheek pigment 008-A';new_image='Knight walnut | orbital grain 011-B'
assert {k:v for k,v in prev['images'].items() if k!=old_image}=={k:v for k,v in cur['images'].items() if k!=new_image}
assert prev['images'][old_image]==sha(OUT/'parent-pigment.png')
assert cur['images'][new_image]==sha(OUT/'pigment.png')
eyes={'Knight | near eye','Knight | far eye'}
topology_changes={o for o in prev["topology"] if prev["topology"][o]!=cur["topology"][o]}
uv_changes={o for o in prev["uvs"] if prev["uvs"][o]!=cur["uvs"][o]}
assert topology_changes==eyes and uv_changes==eyes
finish=[obj for obj in prev["surface_data"] if prev["surface_data"][obj]!=cur["surface_data"][obj]]
assert set(finish)==eyes|{'Knight | continuous horse head and neck'}
from carve import chart,pose,rest_coords
rest=rest_coords(prev['skull'],pose(bpy.context.scene))
u,v=chart(rest);outside=(abs(u-.025)>.395)|(abs(v-.011)>.274)
outside_displacement=float(np.linalg.norm(prev['skull'][outside]-cur['skull'][outside],axis=1).max())
assert outside_displacement<1e-6
geos=[o for o in prev["geometry"] if prev["geometry"][o]!=cur["geometry"][o]]
lamps=[o for o in prev["lights"] if prev["lights"][o]!=cur["lights"][o]]
assert set(lamps)<= {"Eye reflection upper","Eye reflection lower"}
assert set(geos)==eyes|{'Knight | continuous horse head and neck','Knight | coherent skull cheek and conical muzzle'}
s=bpy.context.scene
root=OUT/"review-copy";mdl=root/"models/knight";asset=root/"assets/knight"
mdl.mkdir(parents=True,exist_ok=True);asset.mkdir(parents=True,exist_ok=True)
source=mdl/"knight-rebuilt.blend"
shutil.copyfile(OUT/"knight.blend",source)
image=bpy.data.objects["Knight | near eye"].data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Base Color"].links[0].from_node.image
image_name=image.name
tex=asset/"wood-atlas-improvement-011-B.png";tex.write_bytes(bytes(image.packed_file.data))
assert sha(tex)==sha(OUT/'pigment.png')=='beee98c4ee1af2c55823485a4c0149dea5332c7eaeaa07e06d82ae7022918fe7'
export_mission.ROOT=root
export_mission.export(s,tex,output=asset,source=source)
sys.argv=["validate.py","--",str(root)]
runpy.run_path(str(ROOT/"scripts/knight/validate.py"),run_name="__main__")
validation=json.loads((asset/"validation.json").read_text())
out={"candidate_sha256":sha(OUT/"knight.blend"),"parent_sha256":sha(OUT/"parent.blend"),
    "texture_sidecar":"pigment.png","packed_image_name":image_name,
    "texture_sha256":sha(tex),"texture_export_filename":tex.name,
    "actual_repository_mesh_and_viewer_export_validation":validation,"camera_unchanged":True,
    "only_packed_image_change":[old_image,new_image],"simple_subdivided_topology":sorted(topology_changes),
    "interpolated_uvs_on_subdivided_eyes":sorted(uv_changes),"surface_data_changes":finish,"geometry_changes":geos,"light_changes":lamps,
    "max_skull_world_displacement_outside_orbital_window":outside_displacement,
    "physical_heights":{name:{"whole_height":max(q[1] for q in data['evaluated_z'].values())-min(q[0] for q in data['evaluated_z'].values()),
                "top_z":{part:data['evaluated_z']['Knight | '+part][1] for part in
                         ['swept rounded mane','near swept ear','far swept ear','continuous horse head and neck']}}
                for name,data in [('parent',prev),('candidate',cur)]},
    "eye_visible_fixed_2px_samples":{"parent":prev["eye"]["visible_samples"],"candidate":cur["eye"]["visible_samples"]},
    "eye_visible_bounds":{"parent":prev["eye"]["bounds"],"candidate":cur["eye"]["bounds"]}}
(OUT/"verified.json").write_text(json.dumps(out,indent=2)+"\n")
