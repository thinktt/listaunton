"""Check that the polish checkpoint changes only its measured finish graph."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,control,fixed_camera,save_json,sha

def fingerprint(scene,body):
    ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=ev.to_mesh()
    try:
        h=hashlib.sha256()
        for seq,key,width,dtype in [(mesh.vertices,"co",3,np.float32),(mesh.loops,"vertex_index",1,np.int32),(mesh.polygons,"loop_total",1,np.int32),(mesh.corner_normals,"vector",3,np.float32),(mesh.uv_layers["Pawn pigment"].data,"uv",2,np.float32)]:
            a=np.empty(len(seq)*width,dtype=dtype);seq.foreach_get(key,a);h.update(a.tobytes())
    finally:ev.to_mesh_clear()
    lamps={}
    for o in scene.objects:
        if o.type!="LIGHT":continue
        d=o.data
        lamps[o.name]={"matrix":[list(row) for row in o.matrix_world],
                      "energy":d.energy,"color":list(d.color),"type":d.type,
                      "diffuse":o.visible_diffuse,"glossy":o.visible_glossy,
                      "settings":{k:getattr(d,k) for k in ("shape","size","size_y","spread","shadow_soft_size","normalize","use_shadow","use_nodes","diffuse_factor","specular_factor","volume_factor","transmission_factor") if hasattr(d,k)},
                      "visibility":{k:getattr(o,k) for k in ("visible_camera","visible_shadow","visible_transmission","visible_volume_scatter") if hasattr(o,k)}}
    n=body.data.materials[0].node_tree.nodes
    images={x.name:hashlib.sha256(x.image.packed_file.data).hexdigest() for x in n if x.type=="TEX_IMAGE" and x.image and x.image.packed_file and x.name!="Pawn varnish roughness"}
    bs=n["Principled BSDF"]
    inputs={}
    for key in ("Specular IOR Level","Coat Weight"):
        s=bs.inputs[key]
        if s.is_linked and n.get("Pawn polish strength"):
            mult=s.links[0].from_node
            if mult.type=="MATH" and mult.operation=="MULTIPLY" and mult.inputs[1].is_linked and mult.inputs[1].links[0].from_node==n["Pawn polish strength"]:
                s=mult.inputs[0]
        inputs[key]=[s.links[0].from_node.name,s.links[0].from_socket.name] if s.is_linked else float(s.default_value)
    bg=scene.world.node_tree.nodes["Background"]
    return {"evaluated_mesh_normals_uv_sha256":h.hexdigest(),"lights":lamps,"other_packed_images":images,
            "world":[list(bg.inputs["Color"].default_value),bg.inputs["Strength"].default_value],
            "ray_depth":[scene.cycles.diffuse_bounces,scene.cycles.glossy_bounces],
            "prior_finish_inputs":inputs}

def run(cfg,target,out):
    source=ROOT/cfg["source"];assert sha(source)==cfg["source_sha256"]
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;fixed_camera(scene);old=fingerprint(scene,control(scene))
    bpy.ops.wm.open_mainfile(filepath=str(target),load_ui=False)
    scene=bpy.context.scene;fixed_camera(scene);body=control(scene);new=fingerprint(scene,body)
    for key in ("evaluated_mesh_normals_uv_sha256","lights","other_packed_images","world","ray_depth"):
        assert new[key]==old[key],key
    n=body.data.materials[0].node_tree.nodes;bs=n["Principled BSDF"]
    im=n["Pawn varnish roughness"].image
    assert im.colorspace_settings.name=="Non-Color"
    assert hashlib.sha256(im.packed_file.data).hexdigest()==cfg["texture_sha256"]
    split=n["Pawn finish channels"];coverage=n["Pawn polish strength"]
    assert split.inputs["Color"].links[0].from_node==n["Pawn varnish roughness"]
    assert coverage.inputs["Value"].links[0].from_node==split and coverage.inputs["Value"].links[0].from_socket.name=="Green"
    assert np.allclose([coverage.inputs["To Min"].default_value,coverage.inputs["To Max"].default_value],cfg["polish_range"],atol=1e-7,rtol=0)
    for key in ("Specular IOR Level","Coat Weight"):
        mult=bs.inputs[key].links[0].from_node
        assert mult.type=="MATH" and mult.operation=="MULTIPLY"
        assert mult.inputs[1].links[0].from_node==coverage
        s=mult.inputs[0]
        value=[s.links[0].from_node.name,s.links[0].from_socket.name] if s.is_linked else float(s.default_value)
        assert value==old["prior_finish_inputs"][key],key
    for key,base in (("Roughness",.19),("Coat Roughness",.075)):
        remap=bs.inputs[key].links[0].from_node
        assert remap.type=="MAP_RANGE" and remap.inputs["Value"].links[0].from_node==split
        assert remap.inputs["Value"].links[0].from_socket.name=="Red"
        assert np.allclose([remap.inputs["To Min"].default_value,remap.inputs["To Max"].default_value],np.array(cfg["range"])*base,atol=1e-6,rtol=0)
    report={"passed":True,"model_sha256":sha(target),"source_sha256":sha(source),"camera_above_board":54,
            "unchanged_geometry_normals_uvs":True,"unchanged_lights":len(new["lights"]),"unchanged_world":True,
            "unchanged_ray_depth":new["ray_depth"],"unchanged_diffuse_and_normal_maps":new["other_packed_images"],
            "finish_sha256":cfg["texture_sha256"],"roughness_gain":cfg["range"],"polish_gain":cfg["polish_range"],
            "separate_channels_and_prior_groove_masks_preserved":True}
    save_json(out,report);print(json.dumps(report),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path);p.add_argument("model",type=Path);p.add_argument("output",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);run(json.loads(a.config.read_text()),ROOT/a.model,ROOT/a.output)
