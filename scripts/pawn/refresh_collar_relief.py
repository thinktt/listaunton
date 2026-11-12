"""Test current recovered wood as the collar relief source, with a smooth UV join."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source,save_trial

def run(cfg):
    scene,body=open_source(cfg)
    tree=body.data.materials[0].node_tree;n=tree.nodes;l=tree.links
    bump=n["Walnut grain relief"];old=bump.inputs["Height"].links[0].from_socket
    gray=n.new("ShaderNodeRGBToBW");gray.name="Current collar grain value"
    l.new(n["Pawn walnut pigment"].outputs["Color"],gray.inputs[0])
    power=n.new("ShaderNodeMath");power.operation="POWER";power.inputs[1].default_value=.4
    l.new(gray.outputs[0],power.inputs[0])
    delta=n.new("ShaderNodeMath");delta.operation="SUBTRACT"
    l.new(power.outputs[0],delta.inputs[0]);l.new(old,delta.inputs[1])
    uv=n.new("ShaderNodeUVMap");uv.uv_map="Pawn pigment"
    split=n.new("ShaderNodeSeparateXYZ");l.new(uv.outputs["UV"],split.inputs["Vector"])
    a,b,c,d=cfg["uv_focus"];ramps=[]
    for lo,hi,start,end in ((a,b,0,1),(c,d,1,0)):
        node=n.new("ShaderNodeMapRange");node.interpolation_type="SMOOTHSTEP"
        for key,value in (("From Min",lo),("From Max",hi),("To Min",start),("To Max",end)):node.inputs[key].default_value=value
        l.new(split.outputs["Y"],node.inputs["Value"]);ramps.append(node)
    band=n.new("ShaderNodeMath");band.operation="MULTIPLY"
    l.new(ramps[0].outputs[0],band.inputs[0]);l.new(ramps[1].outputs[0],band.inputs[1])
    blend=n.new("ShaderNodeMath");blend.name="Updated collar grain relief";blend.operation="MULTIPLY_ADD"
    l.new(band.outputs[0],blend.inputs[0]);l.new(delta.outputs[0],blend.inputs[1]);l.new(old,blend.inputs[2])
    l.new(blend.outputs[0],bump.inputs["Height"])
    scene["pawn_collar_relief_source"]=json.dumps({"pigment":scene["pawn_texture_path"],"sha256":scene["pawn_texture_sha256"],"uv_focus":cfg["uv_focus"]},sort_keys=True)
    save_trial(scene,cfg)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);run(json.loads(a.config.read_text(encoding="utf-8")))
