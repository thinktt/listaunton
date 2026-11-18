"""Reopen a reviewed trial, preserve its editable scene, and export matching views."""
import argparse
import json
import sys
from pathlib import Path

import bpy
import bmesh
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT, ASSETS, BUILD, control, fixed_camera, render, save_json, setup, sha, side_camera
from capture_pigment import UV_NAME

def export(scene,body,model):
    graph=bpy.context.evaluated_depsgraph_get()
    ev=body.evaluated_get(graph);mesh=ev.to_mesh()
    try:
        mesh.calc_loop_triangles()
        xyz=np.empty(len(mesh.vertices)*3,np.float32);mesh.vertices.foreach_get("co",xyz);xyz=xyz.reshape(-1,3)
        corner=np.empty(len(mesh.loops)*3,np.float32);mesh.corner_normals.foreach_get("vector",corner)
        uv=np.empty(len(mesh.loops)*2,np.float32);mesh.uv_layers[UV_NAME].data.foreach_get("uv",uv)
        vertices=np.empty(len(mesh.loop_triangles)*3,np.int32);mesh.loop_triangles.foreach_get("vertices",vertices)
        loops=np.empty_like(vertices);mesh.loop_triangles.foreach_get("loops",loops)
        block=np.column_stack([xyz[vertices],corner.reshape(-1,3)[loops],uv.reshape(-1,2)[loops]]).astype("<f4")
        assert np.isfinite(block).all() and np.max(np.abs(np.linalg.norm(block[:,3:6],axis=1)-1))<.0001
        assert np.allclose(np.array(body.matrix_world),np.eye(4),atol=1e-7)
        bm=bmesh.new();bm.from_mesh(mesh)
        volume=bm.calc_volume(signed=True);bad_edges=sum(not e.is_manifold for e in bm.edges)
        euler=len(bm.verts)-len(bm.edges)+len(bm.faces);bm.free()
        assert bad_edges==0 and volume>0 and euler==2
    finally:ev.to_mesh_clear()
    lo=xyz.min(0);hi=xyz.max(0);bounds=hi-lo
    reference=json.loads((ROOT/"history/pawn-mission-start/mesh.json").read_text())["bounds"]["size"]
    assert abs(bounds[2]-reference[2])<.001 and abs(bounds[0]-reference[0])<.005,(bounds,reference)
    count=len(block);raw=block.tobytes()+np.arange(count,dtype="<u4").tobytes()
    (ASSETS/"mesh.bin").write_bytes(raw)
    cam=scene.camera;projection=cam.calc_matrix_camera(graph,x=1254,y=1254)
    camera={"type":cam.data.type,"worldToCamera":[float(v) for row in cam.matrix_world.inverted() for v in row],"projectionMatrix":[float(v) for row in projection for v in row],"width":1254,"height":1254,"orthoScale":cam.data.ortho_scale,"shiftX":cam.data.shift_x,"shiftY":cam.data.shift_y,"elevationDegrees":54}
    tex=ROOT/scene["pawn_texture_path"]
    report={"vertexCount":count,"indexCount":count,"triangleCount":count//3,"vertexStrideBytes":32,"vertexByteLength":block.nbytes,"indexByteOffset":block.nbytes,"totalByteLength":len(raw),"bounds":{"min":lo.tolist(),"max":hi.tolist(),"size":bounds.tolist(),"center":((lo+hi)/2).tolist()},"parts":[{"name":body.name,"vertexCount":count,"indexCount":count,"indexOffset":0,"vertexOffset":0,"triangleCount":count//3}],"sourceSha256":sha(model),"referenceCamera":camera,"texture":scene["pawn_texture_path"],"textureSha256":sha(tex),"uvLayer":UV_NAME}
    if "pawn_roughness_path" in scene:
        path=ROOT/scene["pawn_roughness_path"]
        packed=body.data.materials[0].node_tree.nodes["Pawn varnish roughness"].image
        assert packed.colorspace_settings.name=="Non-Color" and packed.packed_file.data==path.read_bytes()
        assert sha(path)==scene["pawn_roughness_sha256"]
        report["varnish"]={"file":scene["pawn_roughness_path"],"sha256":sha(path),"gain":list(scene["pawn_roughness_range"])}
        if "pawn_polish_range" in scene:
            report["varnish"]["polishGain"]=list(scene["pawn_polish_range"])
            assert body.data.materials[0].node_tree.nodes["Pawn finish channels"].inputs["Color"].links[0].from_node.image==packed
    if "pawn_slope_path" in scene:
        path=ROOT/scene["pawn_slope_path"]
        packed=body.data.materials[0].node_tree.nodes["Pawn fine slope atlas"].image
        assert packed.colorspace_settings.name=="Non-Color" and packed.packed_file.data==path.read_bytes()
        assert sha(path)==scene["pawn_slope_sha256"]
        report["slope"]={"file":scene["pawn_slope_path"],"sha256":sha(path),"limit":scene["pawn_slope_limit"]}
    from mix_varnish import validate as validate_coverage
    coverage=validate_coverage(scene,body)
    if coverage:report["matteBand"]=coverage
    save_json(ASSETS/"mesh.json",report);save_json(ASSETS/"camera.json",camera)
    return {"triangle_count":count//3,"closed_nonmanifold_edges":bad_edges,"signed_volume":volume,"euler_characteristic":euler,"height":float(bounds[2]),"diameter":float(bounds[0]),"height_to_diameter":float(bounds[2]/bounds[0]),"baseline_height_to_diameter":reference[2]/reference[0],"model_sha256":sha(model),"texture_sha256":sha(tex)}

def deliver(variant):
    directory=BUILD/variant
    source=directory/"pawn.blend"
    metrics=json.loads((directory/"metrics.json").read_text())
    assert metrics["render_sha256"]==sha(directory/"fixed.png") and metrics["model_sha256"]==sha(source)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;body=control(scene);fixed_camera(scene)
    tex=ROOT/scene["pawn_texture_path"];assert sha(tex)==scene["pawn_texture_sha256"]
    material=body.data.materials[0];pigment=material.node_tree.nodes["Pawn walnut pigment"].image
    assert pigment.packed_file and pigment.packed_file.data==tex.read_bytes()
    # Rebuilds or exports can be moved between Windows and WSL. Runtime
    # texture data is packed; this relative path is also valid on checkout.
    # The accepted file lives in models/pawn. Write paths relative to that
    # destination for every packed image still driving the wood material.
    known_images={sha(path):path for path in ASSETS.glob("pawn-*.png")}
    import hashlib
    for tex_node in material.node_tree.nodes:
        if tex_node.type=="TEX_IMAGE" and tex_node.image and tex_node.image.packed_file:
            key=hashlib.sha256(tex_node.image.packed_file.data).hexdigest()
            if key in known_images:
                tex_node.image.filepath="//../../"+known_images[key].relative_to(ROOT).as_posix()
    scene["pawn_accepted_trial"]=variant;scene.render.filepath="//../../assets/pawn/render.png"
    scene.cycles.device="CPU";bpy.context.preferences.filepaths.save_version=0
    model=ROOT/"models/pawn/pawn-rebuilt.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(model),relative_remap=False)
    bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
    scene=bpy.context.scene;body=control(scene);fixed_camera(scene)
    material=body.data.materials[0]
    node=material.node_tree.nodes["Pawn walnut pigment"]
    assert node.image.packed_file.data==tex.read_bytes()
    assert Path(bpy.path.abspath(node.image.filepath)).resolve()==tex.resolve()
    bs=material.node_tree.nodes.get("Principled BSDF")
    assert bs.inputs["Base Color"].links[0].from_node==node
    from mix_varnish import validate as validate_coverage
    validate_coverage(scene,body)
    setup(scene,scene.cycles.samples)
    report=export(scene,body,model)
    render(scene,ASSETS/"render.png")
    clay=bpy.data.materials.get("Satin clay - geometry study")
    if clay is None:
        clay=bpy.data.materials.new("Pawn inspection clay");clay.use_nodes=True
        cb=clay.node_tree.nodes.get("Principled BSDF")
        cb.inputs["Base Color"].default_value=(.28,.30,.34,1);cb.inputs["Roughness"].default_value=.30
    body.data.materials[0]=clay;render(scene,ASSETS/"neutral.png")
    side=scene
    if scene.get("pawn_side_scene"):
        side=bpy.data.scenes[scene["pawn_side_scene"]]
        assert control(side) is body, 'Side presentation must share the actual editable pawn.'
        bpy.context.window.scene=side;setup(side,scene.cycles.samples)
    else:
        side_camera(side)
    render(side,ASSETS/"side-seating.png")
    body.data.materials[0]=material;render(side,ASSETS/"profile.png")
    if side is not scene:
        from validate_finish_scope import fingerprint
        snapshot=fingerprint(side,body)
        save_json(ASSETS/"side-presentation.json",{"scene":side.name,"model_sha256":sha(model),
            "profile_sha256":sha(ASSETS/"profile.png"),"same_editable_object_and_material":True,
            "camera_elevation":0,"resolution":side.render.resolution_x,"lighting_preset":"balanced",
            "reference_lights_preserved":sum(o.type=='LIGHT' for o in scene.objects),
            "studio_lights":snapshot['lights'],"studio_world":snapshot['world'],"note":side['pawn_presentation']})
        bpy.context.window.scene=scene
    report.update(variant=variant,texture_packed_after_reopen=True,reference_camera_above_board=54,source_trial_sha256=sha(source),render_sha256=sha(ASSETS/"render.png"),side_sha256=sha(ASSETS/"profile.png"))
    save_json(ASSETS/"mission-validation.json",report);print("PAWN_DELIVERY_CHECKED",report,flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("variant")
    args=p.parse_args(sys.argv[sys.argv.index("--")+1:]);deliver(args.variant)
