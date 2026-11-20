"""Identify the actual emitters responsible for light in unwanted regions."""
import argparse,json,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from fit_lighting import response
from mission_render import ROOT,BUILD,control,setup,fixed_camera,save_json,sha
from capture_pigment import reference_srgb

def main(source,out):
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    s=bpy.context.scene;fixed_camera(s);setup(s,128)
    s.render.resolution_percentage=50;s.cycles.use_denoising=False;s.cycles.use_adaptive_sampling=False
    s.render.image_settings.file_format="OPEN_EXR";s.render.image_settings.color_depth="32"
    ref=reference_srgb().reshape(627,2,627,2,3).mean((1,3));Y,X=np.mgrid[:627,:627];X=X*2+1;Y=Y*2+1
    def region(x0,x1,y0,y1):return (X>=x0)&(X<x1)&(Y>=y0)&(Y<y1)
    masks={"stem-streak":region(494,519,642,701),"socket-wall":region(445,550,765,802),
           "foot-wall":region(381,597,969,984)&(ref.max(2)<.4),
           "dark-groove":region(343,621,906,962)&(ref.max(2)<.16)&(ref.max(2)>.005)}
    out.mkdir(parents=True,exist_ok=True)
    lights=[o for o in s.objects if o.type=="LIGHT"]
    emitters=[o for o in lights if o.visible_glossy and not o.visible_diffuse]
    powers={ob.name:ob.data.energy for ob in lights}
    for ob in emitters:ob.data.energy=0
    baseline=response(s,out)
    masks={k:m&(baseline[:,:,3]>.995) for k,m in masks.items()}
    def measure(pixels):return {k:float(pixels[:,:,:3][m].mean()) for k,m in masks.items()}
    values={"diffuse/world":measure(baseline)}
    for ob in lights:ob.data.energy=0
    s.world.node_tree.nodes["Background"].inputs["Strength"].default_value=0
    for ob in emitters:
        ob.data.energy=powers[ob.name]
        values[ob.name]=measure(response(s,out))
        ob.data.energy=0
    result={k:sorted([[name,round(v[k],6)] for name,v in values.items()],key=lambda p:-p[1])[:7] for k in masks}
    save_json(out/"spill.json",{"source_sha256":sha(source),"values_linear_rgb_mean":values,"ranking":result,"pixels":{k:int(m.sum()) for k,m in masks.items()}})
    print(json.dumps(result),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("source");p.add_argument("output")
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);main(ROOT/a.source,BUILD/a.output)
