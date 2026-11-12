"""Vary real bump distance across a smooth band in the pawn's existing lathe UV."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT
from polish_trial import open_source,save_trial

def install(body,cfg):
    n=body.data.materials[0].node_tree.nodes;l=body.data.materials[0].node_tree.links
    bump=n["Walnut grain relief"]
    assert not bump.inputs["Distance"].is_linked
    base=bump.inputs["Distance"].default_value
    uv=n.new("ShaderNodeUVMap");uv.uv_map="Pawn pigment";uv.name="Collar relief coordinate"
    split=n.new("ShaderNodeSeparateXYZ");l.new(uv.outputs["UV"],split.inputs["Vector"])
    ramps=[]
    for name,bounds,values in [("Collar relief lower fade",cfg["rise"],(0,1)),("Collar relief upper fade",cfg["fall"],(1,0))]:
        m=n.new("ShaderNodeMapRange");m.name=name;m.interpolation_type="SMOOTHSTEP"
        m.inputs["From Min"].default_value=bounds[0];m.inputs["From Max"].default_value=bounds[1]
        m.inputs["To Min"].default_value=values[0];m.inputs["To Max"].default_value=values[1]
        l.new(split.outputs["Y"],m.inputs["Value"]);ramps.append(m)
    band=n.new("ShaderNodeMath");band.operation="MULTIPLY";band.name="Collar relief band"
    l.new(ramps[0].outputs["Result"],band.inputs[0]);l.new(ramps[1].outputs["Result"],band.inputs[1])
    amount=n.new("ShaderNodeMapRange");amount.name="Collar relief distance"
    amount.inputs["To Min"].default_value=base;amount.inputs["To Max"].default_value=base*cfg["factor"]
    l.new(band.outputs[0],amount.inputs["Value"]);l.new(amount.outputs["Result"],bump.inputs["Distance"])
    body["pawn_collar_relief"]=json.dumps(dict(cfg,base_distance=base))
    return base

def run(cfg):
    scene,body=open_source(cfg)
    install(body,cfg["relief"])
    save_trial(scene,cfg)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path);a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(a.config.read_text()))
