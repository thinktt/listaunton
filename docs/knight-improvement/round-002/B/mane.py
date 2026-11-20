"""Extract the evaluated mane UV surface, install the candidate pigment and document its renders."""
from pathlib import Path
import hashlib
import json
import math
import sys
import bpy
import numpy as np
from mathutils import Vector

sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/"scripts/knight"))
from mission_scene import configure_render, json_file, render, save_model, sha, use_side_camera, visible_meshes, world_vertices

PARENT="3d2ccb939f7b96b114cabcd179d8856e8922f734eeb034eb8bc711f641b23f17"
MANE="Knight | swept rounded mane"
TEXTURE="wood-atlas-improvement-002-B.png"

def open_scene(name):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/name),load_ui=False)
    return bpy.context.scene

def atlas_node(scene):
    material=bpy.data.objects[MANE].data.materials[0]
    return material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].links[0].from_node

def prepare():
    assert sha(OUT/"parent.blend")==PARENT
    scene=open_scene("parent.blend")
    image=atlas_node(scene).image
    (OUT/"source-atlas.png").write_bytes(bytes(image.packed_file.data))
    obj=bpy.data.objects[MANE]
    rings=world_vertices(obj).reshape(-1,64,3)
    centers=rings.mean(1)
    lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(centers,axis=0),axis=1))]
    ang=2*np.pi*np.arange(64)/64
    coord=np.empty_like(rings)
    coord[:,:,0]=lengths[:,None]
    coord[:,:,1]=np.cos(ang)
    coord[:,:,2]=np.sin(ang)
    # Temporary, smoothly subdivided ring coordinates. The candidate build
    # reopens the parent. This extraction cannot alter the editable mesh.
    attr=obj.data.attributes.new("Mane sweep interpolation","FLOAT_VECTOR","POINT")
    attr.data.foreach_set("vector",coord.astype(np.float32).ravel())
    graph=bpy.context.evaluated_depsgraph_get()
    bpy.context.view_layer.update()
    ev=obj.evaluated_get(graph)
    mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=graph);mesh.calc_loop_triangles()
    sweep=np.empty((len(mesh.vertices),3),np.float32)
    mesh.attributes[attr.name].data.foreach_get("vector",sweep.ravel())
    normal=np.empty_like(sweep)
    mesh.vertices.foreach_get("normal",normal.ravel())
    normal=normal@np.linalg.inv(np.asarray(obj.matrix_world)[:3,:3])
    normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1.e-8)
    view=np.array(scene.camera.matrix_world.to_quaternion()@Vector((0,0,1)))
    tri=np.empty((len(mesh.loop_triangles),3),np.int32)
    looptri=np.empty_like(tri)
    mesh.loop_triangles.foreach_get("vertices",tri.ravel())
    mesh.loop_triangles.foreach_get("loops",looptri.ravel())
    layer=mesh.uv_layers["Knight wood atlas"]
    uv=np.empty((len(layer.uv),2),np.float32)
    layer.uv.foreach_get("vector",uv.ravel())
    np.savez_compressed(OUT/"surface.npz",sweep=sweep,normal=normal,view=view,tri=tri,uv=uv[looptri])
    ev.to_mesh_clear()
    json_file(OUT/"source.json",{"parent_sha256":PARENT,"source_atlas_sha256":sha(OUT/"source-atlas.png"),
                "ring_distances":lengths.tolist(),"evaluated_triangles":len(tri),"source_image":image.name})

def build():
    assert sha(OUT/"parent.blend")==PARENT
    scene=open_scene("parent.blend")
    target=atlas_node(scene)
    old=target.image
    raw=(OUT/"pigment.png").read_bytes()
    image=bpy.data.images.load(str(OUT/"pigment.png"),check_existing=False)
    image.name="Knight walnut | continuous rear mane 002-B"
    image.colorspace_settings.name=old.colorspace_settings.name
    image.pack(data=raw,data_len=len(raw))
    image.filepath="//../../assets/knight/"+TEXTURE
    target.image=image
    if old.users==0:
        bpy.data.images.remove(old)
    scene["knight_atlas_sha256"]=hashlib.sha256(raw).hexdigest()
    scene["knight_improvement_002_B"]=json.dumps({"scope":"rear mane pigment","parent":PARENT,
        "release_texture":TEXTURE,"texture_sha256":scene["knight_atlas_sha256"]})
    configure_render(scene,144)
    save_model(scene,OUT/"knight.blend")

def camera(scene,angle,elevation=10):
    a,e=map(math.radians,(angle,elevation))
    target=Vector((0,0,2.62))
    cam=scene.camera;cam.data.ortho_scale=6.1;cam.data.shift_x=cam.data.shift_y=0
    cam.location=target+Vector((12*math.sin(a)*math.cos(e),-12*math.cos(a)*math.cos(e),12*math.sin(e)))
    cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
    bpy.context.view_layer.update()

def diagnostics(scene, prefix, clay=False):
    scene.render.resolution_x=scene.render.resolution_y=640
    scene.cycles.samples=32
    yaw=json.loads(scene["knight_mission_pose"])["twist_degrees"]
    for name,az in (("front",90),("opposite",180),("rear-quarter",225),("rear",270),("near",0)):
        camera(scene,yaw+az)
        render(scene,OUT/f"{prefix}wood-{name}.png")
    if clay:
        for obj in visible_meshes(scene):
            for slot in obj.material_slots:slot.material=bpy.data.materials["Neutral satin clay"]
        for obj in scene.objects:
            if obj.type=="LIGHT":obj.hide_render=True
        target=Vector((0,0,2.62))
        for i,point in enumerate([(5,5,8),(5,-5,8),(-5,5,8),(-5,-5,8)]):
            light=bpy.data.lights.new(f"Clay softbox {i}","AREA");light.energy=420;light.shape="DISK";light.size=5.5
            box=bpy.data.objects.new(light.name,light);scene.collection.objects.link(box);box.location=point
            box.rotation_euler=(target-box.location).to_track_quat("-Z","Y").to_euler()
        for i in range(16):
            camera(scene,yaw+22.5*i,8)
            render(scene,OUT/f"clay-{i:02d}.png")

def pictures():
    scene=open_scene("knight.blend")
    assert bytes(atlas_node(scene).image.packed_file.data)==(OUT/"pigment.png").read_bytes()
    configure_render(scene,144)
    render(scene,OUT/"wood.png")
    use_side_camera(scene);render(scene,OUT/"wood-side.png")
    json_file(OUT/"reopened.json",{"parent_sha256":PARENT,"model_sha256":sha(OUT/"knight.blend"),
        "packed_png_matches_pigment":True,"texture_sha256":sha(OUT/"pigment.png"),"release_texture":TEXTURE,
        "fixed_sha256":sha(OUT/"wood.png"),"side_sha256":sha(OUT/"wood-side.png"),"samples":144})
    diagnostics(scene,"",True)

if __name__=="__main__":
    flags=sys.argv[sys.argv.index("--")+1:]
    if "--prepare" in flags:prepare()
    if "--build" in flags:build()
    if "--render" in flags:pictures()
    for name,prefix,flag in [("parent.blend","parent-","--parent-diagnostics"),
                             ("knight.blend","","--candidate-studio")]:
        if flag in flags:
            scene=open_scene(name)
            configure_render(scene,32)
            diagnostics(scene,prefix)
