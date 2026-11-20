"""Isolate each normal layer in cropped real renders; never save these as a model."""
import argparse,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,BUILD,control,fixed_camera,setup,render,save_json,sha

def run(source,directory):
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    s=bpy.context.scene;fixed_camera(s);setup(s,256)
    out=BUILD/directory;out.mkdir(parents=True,exist_ok=True)
    s.render.use_border=True;s.render.use_crop_to_border=False
    box=[375,548,594,646]
    s.render.border_min_x=box[0]/1254;s.render.border_max_x=box[2]/1254
    s.render.border_min_y=1-box[3]/1254;s.render.border_max_y=1-box[1]/1254
    n=control(s).data.materials[0].node_tree.nodes
    nodes={"slopes":n["Measured fine varnish slopes"],"grain":n["Walnut grain relief"],"pores":n["Fine varnish relief"]}
    original={key:ob.inputs["Strength"].default_value for key,ob in nodes.items()}
    rows={}
    for label,omit in [("baseline",[]),("without-slopes",["slopes"]),("without-grain",["grain"]),("without-pores",["pores"]),("plain-normals",list(nodes))]:
        for key,node in nodes.items():node.inputs["Strength"].default_value=0 if key in omit else original[key]
        p=out/(label+".png");render(s,p);rows[label]={"disabled":omit,"sha256":sha(p)}
    save_json(out/"measurement.json",{"source_sha256":sha(source),"crop":box,"samples":256,"layers":original,"renders":rows})

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("source",type=Path);p.add_argument("directory")
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);run(ROOT/a.source,a.directory)
