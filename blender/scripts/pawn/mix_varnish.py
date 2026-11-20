"""Blend a small matte-wood fraction into a smooth UV band, using two real BSDFs."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source,save_trial

def validate(scene,body):
    """Verify real BSDF coverage and the identical live pigment/normal inputs."""
    import math
    n=body.data.materials[0].node_tree.nodes
    bs=n["Principled BSDF"];out=next(node for node in n if node.type=="OUTPUT_MATERIAL")
    if "pawn_matte_band" not in scene:
        assert out.inputs["Surface"].links[0].from_node==bs
        return None
    cfg=json.loads(scene["pawn_matte_band"])
    assert 0<=cfg["fraction"]<=1 and cfg["rise"][0]<cfg["rise"][1]<=cfg["fall"][0]<cfg["fall"][1]
    mix=n["Wood varnish coverage"];diffuse=n["Matte walnut"]
    assert mix.type=="MIX_SHADER" and diffuse.type=="BSDF_DIFFUSE"
    assert out.inputs["Surface"].links[0].from_node==mix
    assert mix.inputs[1].links[0].from_node==bs and mix.inputs[2].links[0].from_node==diffuse
    assert diffuse.inputs["Color"].links[0].from_node==n["Pawn walnut pigment"]
    assert diffuse.inputs["Normal"].links[0].from_socket==bs.inputs["Normal"].links[0].from_socket
    assert diffuse.inputs["Roughness"].default_value==0
    amount=n["Matte grain fraction"];band=n["Matte grain band"]
    assert amount.type==band.type=="MATH" and amount.operation==band.operation=="MULTIPLY"
    assert mix.inputs[0].links[0].from_node==amount and amount.inputs[0].links[0].from_node==band
    assert math.isclose(amount.inputs[1].default_value,cfg["fraction"],abs_tol=1e-7)
    for i,(name,bounds,values) in enumerate([("Matte grain lower fade",cfg["rise"],(0,1)),("Matte grain upper fade",cfg["fall"],(1,0))]):
        ramp=n[name]
        assert ramp.type=="MAP_RANGE" and ramp.interpolation_type=="SMOOTHSTEP" and ramp.clamp
        assert band.inputs[i].links[0].from_node==ramp
        expected=[*bounds,*values]
        actual=[ramp.inputs[k].default_value for k in ("From Min","From Max","To Min","To Max")]
        assert all(math.isclose(a,b,abs_tol=1e-7) for a,b in zip(actual,expected))
        split=ramp.inputs["Value"].links[0].from_node
        assert split.type=="SEPXYZ" and ramp.inputs["Value"].links[0].from_socket.name=="Y"
        uv=split.inputs["Vector"].links[0].from_node
        assert uv.type=="UVMAP" and uv.uv_map=="Pawn pigment"
    assert not bs.inputs["Emission Color"].is_linked and bs.inputs["Emission Strength"].default_value==0
    return cfg

def install(scene,body,cfg):
    n=body.data.materials[0].node_tree.nodes;l=body.data.materials[0].node_tree.links
    bs=n["Principled BSDF"];out=next(node for node in n if node.type=="OUTPUT_MATERIAL")
    assert out.inputs["Surface"].links[0].from_node==bs
    uv=n.new("ShaderNodeUVMap");uv.uv_map="Pawn pigment";uv.name="Matte grain coordinate"
    split=n.new("ShaderNodeSeparateXYZ");l.new(uv.outputs["UV"],split.inputs["Vector"])
    ramps=[]
    for name,bounds,values in [("Matte grain lower fade",cfg["rise"],(0,1)),("Matte grain upper fade",cfg["fall"],(1,0))]:
        m=n.new("ShaderNodeMapRange");m.name=name;m.interpolation_type="SMOOTHSTEP"
        m.inputs["From Min"].default_value=bounds[0];m.inputs["From Max"].default_value=bounds[1]
        m.inputs["To Min"].default_value=values[0];m.inputs["To Max"].default_value=values[1]
        l.new(split.outputs["Y"],m.inputs["Value"]);ramps.append(m)
    band=n.new("ShaderNodeMath");band.name="Matte grain band";band.operation="MULTIPLY"
    l.new(ramps[0].outputs["Result"],band.inputs[0]);l.new(ramps[1].outputs["Result"],band.inputs[1])
    amount=n.new("ShaderNodeMath");amount.name="Matte grain fraction";amount.operation="MULTIPLY";amount.inputs[1].default_value=cfg["fraction"]
    l.new(band.outputs[0],amount.inputs[0])
    diffuse=n.new("ShaderNodeBsdfDiffuse");diffuse.name="Matte walnut";diffuse.inputs["Roughness"].default_value=0
    l.new(n["Pawn walnut pigment"].outputs["Color"],diffuse.inputs["Color"])
    l.new(bs.inputs["Normal"].links[0].from_socket,diffuse.inputs["Normal"])
    mix=n.new("ShaderNodeMixShader");mix.name="Wood varnish coverage"
    l.new(amount.outputs[0],mix.inputs[0]);l.new(bs.outputs["BSDF"],mix.inputs[1]);l.new(diffuse.outputs["BSDF"],mix.inputs[2])
    l.new(mix.outputs[0],out.inputs["Surface"])
    scene["pawn_matte_band"]=json.dumps(cfg,sort_keys=True)

def run(cfg):
    scene,body=open_source(cfg);install(scene,body,cfg["matte_band"]);save_trial(scene,cfg)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path);a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(a.config.read_text()))
