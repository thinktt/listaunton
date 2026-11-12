"""Measure smaller finite reflectors along the curved chest, retaining real BSDF shading."""
import argparse,json,math,shutil,sys
from pathlib import Path
import bpy
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from capture_material import read_pass
from export_mission import export
from fit_chest_reflections import panel_from_samples,fit
from fit_eye_reflection import display_transform
from fit_surface_polish import read_reference
from mission_scene import BUILD,configure_render,json_file,render,save_model,sha,use_side_camera
from probe_reflections import surface_probe

CROP=(221,312,759,808)
WATTS=4.0

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--paths",type=Path,required=True)
    p.add_argument("--variant",required=True)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    source=a.source.resolve();out=BUILD/a.variant;out.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);scene=bpy.context.scene
    mesh=out/"input-mesh";mesh.mkdir(exist_ok=True)
    export(scene,source.parent/"pigment.png",output=mesh,source=source)
    probe,digest=surface_probe(mesh);assert digest==sha(source)
    paths=json.loads(a.paths.read_text(encoding="utf-8"))
    receivers=bpy.data.collections["Knight | chest reflection receivers"]
    lamps=[];details=[]
    for obj in list(scene.objects):
        if obj.type=="LIGHT" and obj.name.startswith("Walnut | carved chest "):
            lamps.append(obj);details.append({"name":obj.name,"prior_watts":float(obj.data.energy),"kind":"prior"})
            obj.data.energy=0
    assert len(lamps)==4
    for feature,distance,width,spread in [("shoulder",1.25,1.3,32),
                                          ("bevel",.95,.48,27),
                                          ("crest",.95,.45,28),
                                          ("far_lip",1.35,.56,31)]:
        for i,(lo,hi) in enumerate([(581,628),(627,676),(675,724)]):
            samples=[probe(*r["pixel"]) for r in paths["curves"][feature] if lo<=r["pixel"][1]<=hi]
            samples=[s for s in samples if s and s["part"].endswith("continuous horse head and neck")]
            assert len(samples)>=3,(feature,lo,len(samples))
            margins=(.10,.13) if feature=="shoulder" else (.075,.035)
            lamp,info=panel_from_samples(scene,receivers,"chest segment "+feature+str(i+1),samples,distance,margins)
            lamp.data.size_y=max(.035,lamp.data.size_y*width)
            lamp.data.color=(1,.90,.81);lamp.data.spread=math.radians(spread)
            info.update({"kind":"segment","size_y":float(lamp.data.size_y),"spread_degrees":spread})
            lamps.append(lamp);details.append(info)
    configure_render(scene,128);scene.cycles.use_denoising=False;scene.cycles.use_light_tree=False
    x0,y0,x1,y1=CROP;w=1254
    scene.render.use_border=True;scene.render.use_crop_to_border=True
    scene.render.border_min_x=(x0+.05)/w;scene.render.border_max_x=(x1+.05)/w
    scene.render.border_min_y=(w-y1+.05)/w;scene.render.border_max_y=(w-y0+.05)/w
    base=read_pass(scene,out/"base.exr")
    target=read_reference()[y0:y1,x0:x1]
    yy,xx=np.indices(target.shape[:2]);yy+=y0;xx+=x0
    mask=(base[:,:,3]>.99)&(target[:,:,3]>.92)&(xx%3==0)&(yy%3==0)
    axis=np.interp(yy,[547,585,625,665,705,745],[400,432,473,514,554,600]);offset=xx-axis
    gate=np.clip((yy-533)/24,0,1)*np.clip((778-yy)/26,0,1)
    weight=(1+.65*gate+1.2*gate*np.exp(-((offset+2)/10)**2)+.65*gate*np.exp(-((offset+60)/21)**2))[mask]
    responses=[]
    for i,lamp in enumerate(lamps):
        lamp.data.energy=WATTS
        frame=read_pass(scene,out/(str(i).zfill(2)+"-response.exr"))
        responses.append(np.maximum(0,frame[:,:,:3][mask]-base[:,:,:3][mask]))
        lamp.data.energy=0
    powers,initial,best=fit(base[:,:,:3][mask],responses,target[:,:,:3][mask],weight,display_transform(scene))
    retained=0
    for factor,lamp,info in zip(powers,lamps,details):
        lamp.data.energy=float(WATTS*factor);info["watts"]=float(lamp.data.energy)
        if lamp.data.energy==0:bpy.data.objects.remove(lamp,do_unlink=True)
        else:retained+=1
    scene.render.use_border=False;scene.render.use_crop_to_border=False
    scene.cycles.use_light_tree=True;configure_render(scene,144)
    info={"source_sha256":sha(source),"samples":144,"measurement_samples":128,
        "base_loss":initial,"predicted_loss":best,"retained_reflectors":retained,
        "reflectors":details,"method":"Finite glossy-only warm rectangles fitted to shorter spans of reflected camera rays on the actual chest. Pixel color is never composited; wood, local finish and geometry are preserved."}
    scene["knight_chest_segment_lights"]=json.dumps(info)
    shutil.copyfile(source.parent/"pigment.png",out/"pigment.png")
    save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False)
    scene=bpy.context.scene;configure_render(scene,144)
    render(scene,out/"wood.png");use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",info)
    print("KNIGHT_SEGMENT_REFLECTORS",initial,best,retained,flush=True)

if __name__=="__main__":main()
