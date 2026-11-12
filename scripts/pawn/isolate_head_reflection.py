"""Separate direct fixtures and reflected surroundings at the lower head edge."""
import argparse,json,sys
from pathlib import Path
import bpy
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from capture_pigment import reference_srgb
from fit_lighting import response
from mission_render import ROOT,BUILD,control,fixed_camera,setup,save_json,sha


def run(source,edge_file,out):
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;fixed_camera(scene);setup(scene,160)
    scene.render.use_border=True;scene.render.use_crop_to_border=False
    scene.render.border_min_x=410/1254;scene.render.border_max_x=557/1254
    scene.render.border_min_y=1-613/1254;scene.render.border_max_y=1-541/1254
    scene.render.image_settings.file_format="OPEN_EXR";scene.render.image_settings.color_depth="32"
    out.mkdir(parents=True,exist_ok=True)
    pts=np.asarray(json.loads(edge_file.read_text())["edge_xy"]["031-lower-cheek"])
    yy,xx=np.mgrid[:1254,:1254];dy=yy-np.interp(xx,pts[:,0],pts[:,1])
    strip=(xx>429)&(xx<538)&(dy>=-5)&(dy<-.1)
    ref=reference_srgb()
    def measure(image):
        return {k:np.round(image[:,:,:3][m].mean(0),6).tolist() for k,m in {"left":strip&(xx<464),"center":strip&(xx>=464)&(xx<502),"right":strip&(xx>=502)}.items()}
    # The zero-diffuse material preserves all actual normals, roughness,
    # IOR and varnish strength. It identifies the radiance floor from gloss.
    material=control(scene).data.materials[0];bs=material.node_tree.nodes["Principled BSDF"]
    color=bs.inputs["Base Color"]
    for link in list(color.links):material.node_tree.links.remove(link)
    color.default_value=(0,0,0,1)
    lamps=[o for o in scene.objects if o.type=="LIGHT"]
    powers={o.name:o.data.energy for o in lamps}
    world=scene.world.node_tree.nodes["Background"].inputs["Strength"];ws=world.default_value
    full=measure(response(scene,out))
    original_bounces=[scene.cycles.diffuse_bounces,scene.cycles.glossy_bounces]
    scene.cycles.diffuse_bounces=0;scene.cycles.glossy_bounces=0
    direct=measure(response(scene,out))
    scene.cycles.diffuse_bounces,scene.cycles.glossy_bounces=original_bounces
    for lamp in lamps:lamp.data.energy=0
    groups={}
    for o in lamps:
        if o.visible_diffuse:group="diffuse fixtures"
        elif "collar" in o.name.lower():group=o.name
        elif "head" in o.name.lower() or "polish core" in o.name:group="head reflectors"
        else:group="other reflectors"
        groups.setdefault(group,[]).append(o)
    measures={}
    for label,group in [("world",[])]+list(groups.items()):
        world.default_value=ws if label=="world" else 0
        for o in group:o.data.energy=powers[o.name]
        measures[label]=measure(response(scene,out))
        if label=="diffuse fixtures" and all(hasattr(o.data,"specular_factor") for o in group):
            old=[o.data.specular_factor for o in group]
            for o in group:o.data.specular_factor=0
            measures["diffuse fixtures, data specular zero"]=measure(response(scene,out))
            for o,v in zip(group,old):o.data.specular_factor=v
        for o in group:o.data.energy=0
    save_json(out/"reflection-floor.json",{"source_sha256":sha(source),"original_diffuse_and_glossy_bounces":original_bounces,"all_gloss_floor":full,"zero_secondary_bounce_floor":direct,"isolated_lights":measures,"mask":"Three sections of the visible ball 0.1 to 5 pixels above its true occlusion edge. Scene-linear RGB."})
    print(json.dumps(measures),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("source",type=Path);p.add_argument("edge",type=Path);p.add_argument("out")
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);run(ROOT/a.source,ROOT/a.edge,BUILD/a.out)
