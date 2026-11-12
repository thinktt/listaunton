"""Validate the complete contact checkpoint against its preserved ninth pawn."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,control,fixed_camera,save_json,sha
from validate_finish_scope import fingerprint
from mix_varnish import validate

def scalar(value):
    if isinstance(value,(str,bool,int,float)):return value
    return list(value)

def graph(socket):
    node=socket.node
    attributes={k:scalar(getattr(node,k)) for k in ("operation","use_clamp","interpolation_type","clamp","data_type","blend_type","uv_map","space","interpolation","extension","projection","noise_dimensions","normalize","distribution","subsurface_method","invert","mute") if hasattr(node,k)}
    if node.type=="TEX_IMAGE":
        im=node.image
        attributes["image"]=[im.colorspace_settings.name,list(im.size),node.name if node.name in ("Pawn walnut pigment","Pawn fine slope atlas") else hashlib.sha256(im.packed_file.data).hexdigest()]
    inputs=[]
    for s in node.inputs:
        inputs.append([s.identifier,graph(s.links[0].from_socket) if s.is_linked else scalar(s.default_value) if hasattr(s,"default_value") else None])
    return [node.type,socket.identifier,attributes,inputs]

def run(cfg,target,out):
    source=ROOT/cfg["source"];assert sha(source)==cfg["source_sha256"]
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;fixed_camera(scene);body=control(scene)
    old=fingerprint(scene,body)
    prior_graph=graph(body.data.materials[0].node_tree.nodes["Principled BSDF"].outputs["BSDF"])
    old_slope=body.data.materials[0].node_tree.nodes["Pawn fine slope atlas"].image
    previous=np.empty(len(old_slope.pixels),np.float32);old_slope.pixels.foreach_get(previous)
    bpy.ops.wm.open_mainfile(filepath=str(target),load_ui=False)
    scene=bpy.context.scene;fixed_camera(scene);body=control(scene);new=fingerprint(scene,body)
    for key in ("evaluated_mesh_normals_uv_sha256","world","ray_depth"):
        assert old[key]==new[key],key
    n=body.data.materials[0].node_tree.nodes
    assert graph(n["Principled BSDF"].outputs["BSDF"])==prior_graph,"Prior wood/relief/varnish graph changed"
    assert validate(scene,body)==cfg["matte_band"]
    assert set(new["lights"])==set(old["lights"]) and len(new["lights"])==44
    powers={r["name"]:r["energy"] for r in cfg["reflectors"]}
    moved=set(cfg["shadow_lights"]["lights"])
    for name,before in old["lights"].items():
        after=dict(new["lights"][name]);before=dict(before)
        if name in powers:
            assert abs(after.pop("energy")-powers[name])<1e-6
            before.pop("energy")
        if name in moved:
            after.pop("matrix");before.pop("matrix")
        assert after==before,name
    # Independently calculate the two permitted lamp positions and their aims.
    from mathutils import Vector
    import math
    pivot=Vector(cfg["shadow_lights"]["pivot"])
    for name in moved:
        matrix=np.array(old["lights"][name]["matrix"]);offset=Vector(matrix[:3,3])-pivot
        d=offset.length;e=math.asin(offset.z/d)+math.radians(cfg["shadow_lights"]["elevation_delta"])
        horizontal=Vector((offset.x,offset.y,0)).normalized()
        position=pivot+horizontal*(d*math.cos(e))+Vector((0,0,d*math.sin(e)))
        lamp=scene.objects[name]
        assert (lamp.location-position).length<1e-6
        direction=(Vector(cfg["shadow_lights"]["aim"])-position).normalized()
        actual=lamp.matrix_world.to_3x3()@Vector((0,0,-1))
        assert (actual-direction).length<1e-6
    for name,path,expected in [("Pawn walnut pigment",cfg["texture"],cfg["texture_sha256"]),("Pawn fine slope atlas",cfg["slopes"]["texture"],cfg["slopes"]["texture_sha256"])]:
        raw=n[name].image.packed_file.data
        assert raw==(ROOT/path).read_bytes() and hashlib.sha256(raw).hexdigest()==expected
    slope=n["Pawn fine slope atlas"].image
    values=np.empty(len(slope.pixels),np.float32);slope.pixels.foreach_get(values)
    w,h=slope.size;previous=previous.reshape(h,w,4);values=values.reshape(h,w,4)
    v=(np.arange(h)+.5)/h
    outside=(v<.672)|(v>.746)
    assert np.array_equal(previous[outside],values[outside]),"Normal-map edits escaped collar band"
    report={"passed":True,"model_sha256":sha(target),"source_sha256":sha(source),"camera_above_board":54,"geometry_normals_uv_unchanged":True,"mesh_normals_uv_sha256":new["evaluated_mesh_normals_uv_sha256"],"light_count":44,"changed_reflector_powers":powers,"moved_diffuse_sources":sorted(moved),"other_light_and_world_settings_unchanged":True,"original_principled_graph_preserved":True,"matte_wood_uses_live_pigment_and_normal":True,"matte_band":cfg["matte_band"],"normal_map_changes_limited_to_collar_uv":True,"pigment_sha256":cfg["texture_sha256"],"slope_sha256":cfg["slopes"]["texture_sha256"],"secondary_ray_depth":new["ray_depth"]}
    save_json(out,report);print(json.dumps(report),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path);p.add_argument("model",type=Path);p.add_argument("output",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(a.config.read_text()),ROOT/a.model,ROOT/a.output)
