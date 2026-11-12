"""Check unchanged pawn form/rig/shader and collar-only finish-map changes."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,control,fixed_camera,save_json,sha
from validate_finish_scope import fingerprint
from validate_contact_checkpoint import graph
from mix_varnish import validate

MAPS=("Pawn walnut pigment","Pawn fine slope atlas","Pawn varnish roughness")

def pixels(image):
    out=np.empty(len(image.pixels),np.float32);image.pixels.foreach_get(out)
    return out.reshape(image.size[1],image.size[0],4)

def run(cfg,target,out):
    source=ROOT/cfg["source"];assert sha(source)==cfg["source_sha256"]
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;fixed_camera(scene);body=control(scene);old=fingerprint(scene,body)
    n=body.data.materials[0].node_tree.nodes
    old_graph=graph(n["Principled BSDF"].outputs["BSDF"],MAPS)
    old_band=validate(scene,body)
    prior={name:pixels(n[name].image) for name in MAPS[1:]}
    bpy.ops.wm.open_mainfile(filepath=str(target),load_ui=False)
    scene=bpy.context.scene;fixed_camera(scene);body=control(scene);new=fingerprint(scene,body)
    n=body.data.materials[0].node_tree.nodes
    for key in ("evaluated_mesh_normals_uv_sha256","lights","world","ray_depth"):
        assert old[key]==new[key],key
    assert graph(n["Principled BSDF"].outputs["BSDF"],MAPS)==old_graph,"Wood/relief/varnish graph changed"
    assert validate(scene,body)==old_band
    assert "pawn_collar_relief_source" not in scene and n.get("Updated collar grain relief") is None
    checks={}
    for name,spec in ((MAPS[0],cfg),(MAPS[1],cfg["slopes"]),(MAPS[2],cfg["finish"])):
        im=n[name].image;path=ROOT/spec["texture"]
        assert im.packed_file.data==path.read_bytes() and sha(path)==spec["texture_sha256"]
        assert im.colorspace_settings.name==("sRGB" if name==MAPS[0] else "Non-Color")
        checks[name]={"file":spec["texture"],"sha256":spec["texture_sha256"]}
        if name in prior:
            a=prior[name];b=pixels(im);assert a.shape==b.shape
            v=(np.arange(len(a))+.5)/len(a);outside=(v<.672)|(v>.746)
            assert np.array_equal(a[outside],b[outside]),name
            checks[name]["outside_collar_identical"]=True
            checks[name]["changed_fraction"]=float(np.any(a!=b,axis=2).mean())
    assert scene.cycles.samples==cfg["samples"] and scene.cycles.seed==cfg["seed"]
    assert scene.cycles.use_light_tree==cfg["light_tree"]
    report={"passed":True,"source_sha256":sha(source),"model_sha256":sha(target),"geometry_normals_uv_unchanged":True,"lights_unchanged":len(new["lights"]),"world_ray_depth_unchanged":True,"camera_above_board":54,"prior_shader_and_matte_band_preserved":True,"rejected_relief_change_absent":True,"maps":checks,"samples":scene.cycles.samples,"seed":scene.cycles.seed,"light_tree":scene.cycles.use_light_tree}
    save_json(out,report);print(json.dumps(report),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path);p.add_argument("model",type=Path);p.add_argument("output",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);run(json.loads(a.config.read_text(encoding="utf-8")),ROOT/a.model,ROOT/a.output)
