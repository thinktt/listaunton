"""Fit a compact reflection rig and the carved wood's local polish together."""
import argparse
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from capture_material import read_pass
from fit_chest_reflections import panel_from_samples
from fit_eye_reflection import display_transform
from fit_surface_polish import ATTRIBUTE,PRIOR,attach_coverage,read_reference,solve_field
from mission_scene import BUILD,ROOT,configure_render,json_file,render,save_model,sha,use_side_camera,visible_meshes
from probe_reflections import surface_probe

CROP=(221,312,759,808)
WATTS=8.0


def add_reflectors(scene,source,paths):
    probe,digest=surface_probe(source.parent)
    assert digest==sha(source)
    collection=bpy.data.collections["Knight | chest reflection receivers"]
    replaced=[]
    for label in ("crest","narrow crest","far ridge","outer shoulder"):
        old=bpy.data.objects.get("Walnut | "+label)
        if old:
            replaced.append({"name":old.name,"watts":float(old.data.energy)})
            bpy.data.objects.remove(old,do_unlink=True)
    assert len(replaced)>=3
    lamps=[];details=[]
    settings=[("shoulder",1.58,(.40,.36),.95,35),
              ("bevel",1.05,(.09,.05),.58,38),
              ("crest",1.18,(.12,.05),.62,36),
              ("far_lip",1.60,(.13,.06),.67,42)]
    for feature,dist,margins,width,spread in settings:
        rows=[probe(*row["pixel"]) for row in paths["curves"][feature] if 592<=row["pixel"][1]<=703]
        rows=[r for r in rows if r and r["part"].endswith("continuous horse head and neck")]
        assert len(rows)>=6
        lamp,spec=panel_from_samples(scene,collection,"carved chest "+feature,rows,dist,margins)
        lamp.data.size_y=max(.07,lamp.data.size_y*width);lamp.data.spread=np.deg2rad(spread)
        lamp.data.color=(1,.90,.81);spec.update({"size_y":lamp.data.size_y,"spread":spread})
        lamps.append(lamp);details.append(spec)
    return lamps,details,replaced


def measure(scene,objects,lamps,out):
    skin=bpy.data.objects["Knight | continuous horse head and neck"]
    wood=skin.data.materials[0];study=wood.copy();skin.data.materials[0]=study
    tree=study.node_tree;cover=tree.nodes["Fraction of burnished surface"]
    attr=cover.inputs[0].links[0].from_node
    assert attr.attribute_name==ATTRIBUTE
    tree.links.remove(cover.inputs[0].links[0])
    x0,y0,x1,y1=CROP;w=1254
    configure_render(scene,128);scene.cycles.use_denoising=False;scene.cycles.use_light_tree=False
    scene.render.use_border=True;scene.render.use_crop_to_border=True
    scene.render.border_min_x=(x0+.05)/w;scene.render.border_max_x=(x1+.05)/w
    scene.render.border_min_y=(w-y1+.05)/w;scene.render.border_max_y=(w-y0+.05)/w
    bases=[];basis=[]
    for value,label in [(0,"satin"),(1,"polished")]:
        cover.inputs[0].default_value=value
        base=read_pass(scene,out/(label+"-base.exr"));responses=[]
        for i,lamp in enumerate(lamps):
            lamp.data.energy=WATTS
            lit=read_pass(scene,out/(label+f"-{i}.exr"))
            responses.append(np.maximum(lit[:,:,:3]-base[:,:,:3],0))
            lamp.data.energy=0
        bases.append(base);basis.append(responses)
    # A diagnostic pass measures the existing material scalar and identifies
    # the real continuous skin. Other components are black for this pass only.
    black=bpy.data.materials.new("Knight temporary receiver mask");black.use_nodes=True
    btree=black.node_tree;bout=btree.nodes["Material Output"]
    emitter=btree.nodes.new("ShaderNodeEmission");emitter.inputs["Color"].default_value=(0,0,0,1)
    btree.links.new(emitter.outputs[0],bout.inputs["Surface"])
    for obj in objects:
        if obj!=skin:obj.data.materials[0]=black
    combine=tree.nodes.new("ShaderNodeCombineColor");combine.mode="RGB";combine.inputs[1].default_value=1
    tree.links.new(attr.outputs["Fac"],combine.inputs[0])
    emitter=tree.nodes.new("ShaderNodeEmission");tree.links.new(combine.outputs[0],emitter.inputs["Color"])
    output=next(n for n in tree.nodes if n.type=="OUTPUT_MATERIAL" and n.is_active_output)
    tree.links.new(emitter.outputs[0],output.inputs["Surface"])
    scene.cycles.samples=8;identity=read_pass(scene,out/"prior-coverage.exr")
    for obj in objects:obj.data.materials[0]=wood
    bpy.data.materials.remove(study);bpy.data.materials.remove(black)
    return bases,basis,identity


def choose_powers(bases,basis,identity,target,linear,scene):
    x0,y0,x1,y1=CROP;yy,xx=np.indices(target.shape[:2]);yy+=y0;xx+=x0
    center=np.interp(yy,[547,585,625,665,705,745],[400,432,473,514,554,600])
    offset=xx-center
    active=np.clip((yy-533)/24,0,1)*np.clip((778-yy)/26,0,1)*np.clip((offset+135)/24,0,1)*np.clip((123-offset)/23,0,1)
    mask=(bases[0][:,:,3]>.99)&(target[:,:,3]>.87)&(identity[:,:,1]>.98)&(xx%2==0)&(yy%2==0)
    ref=target[:,:,:3][mask];reference_linear=linear[mask]
    prior=np.clip(identity[:,:,0][mask],0,1)
    gate=active[mask]
    # One free finish per small surface patch keeps the power fit from
    # explaining every noisy or mismatched image pixel independently.
    groups=((yy-y0)//9*((x1-x0+8)//9)+(xx-x0)//9)[mask].ravel()
    counts=np.bincount(groups)
    mean_prior=np.bincount(groups,weights=prior,minlength=len(counts))/np.maximum(counts,1)
    distance=offset[mask]
    weights=(1+.65*gate+1.8*gate*np.exp(-((distance+2)/9)**2)+.85*gate*np.exp(-((distance+60)/20)**2)).astype(np.float32)
    response=[[v[mask] for v in layer] for layer in basis]
    background=[v[:,:,:3][mask] for v in bases];transform=display_transform(scene)
    channel=np.array([.20,.43,.37],np.float32)
    exposure=1/np.maximum(.07+reference_linear@channel,.07)**2
    def loss(v):
        low=background[0].copy();high=background[1].copy()
        for i,power in enumerate(v):
            if power:low+=power*response[0][i];high+=power*response[1][i]
        difference=high-low
        h=exposure*np.sum(difference*difference*channel,axis=1)
        rhs=exposure*np.sum((reference_linear-low)*difference*channel,axis=1)
        regularizer=.024*counts
        tile=(np.bincount(groups,weights=rhs)+regularizer*mean_prior)/np.maximum(np.bincount(groups,weights=h)+regularizer,1e-8)
        blend=prior+gate*(np.clip(tile[groups],.035,.94)-prior)
        rgb=np.ascontiguousarray(low+blend[:,None].astype(np.float32)*difference);transform.applyRGB(rgb)
        err=rgb-ref
        cost=(np.sqrt(.05**2+err*err)-.05+.52*err*err).mean(1)
        return float(np.average(cost+.0009*(blend-prior)**2,weights=weights))
    v=np.zeros(len(basis[0]));initial=best=loss(v)
    for step in (2.,.45,.10,.024,.006):
        for _ in range(26):
            before=best
            for i in range(len(v)):
                for sign in (-1,1):
                    trial=v.copy();trial[i]+=sign*step
                    if not 0<=trial[i]<=40:continue
                    val=loss(trial)
                    if val<best-2e-8:v,best=trial,val
            if best==before:break
    return v,initial,best,len(ref)


def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True)
    p.add_argument("--paths",type=Path,required=True);p.add_argument("--variant",required=True)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    out=BUILD/a.variant;out.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(a.source),load_ui=False);scene=bpy.context.scene
    paths=json.loads(a.paths.read_text());lamps,details,replaced=add_reflectors(scene,a.source,paths)
    objects=visible_meshes(scene)
    bases,basis,identity=measure(scene,objects,lamps,out)
    x0,y0,x1,y1=CROP;target=read_reference()[y0:y1,x0:x1];linear=np.load(BUILD/"material-observations/reference-linear.npy")[y0:y1,x0:x1]
    v,initial,best,n=choose_powers(bases,basis,identity,target,linear,scene)
    end=[base.copy() for base in bases]
    for i,(factor,lamp,detail) in enumerate(zip(v,lamps,details)):
        detail["watts"]=float(WATTS*factor);lamp.data.energy=detail["watts"]
        for j in range(2):end[j][:,:,:3]+=factor*basis[j][i]
        if factor==0:bpy.data.objects.remove(lamp,do_unlink=True)
    local=solve_field(scene,end[0],end[1],target,3)
    field=np.full((1254,1254),PRIOR,np.float32);field[y0:y1,x0:x1]=local
    mat=objects[0].data.materials[0];cover=mat.node_tree.nodes["Fraction of burnished surface"]
    stats=attach_coverage(scene,objects,field,mat,cover,"chest")
    scene.render.use_border=False;scene.render.use_crop_to_border=False;scene.cycles.use_light_tree=True
    cfg={"source_sha256":sha(a.source),"samples":144,"measured_samples":128,"prior_rig":replaced,
         "candidate_cards":details,"initial_fit_loss":initial,"selected_fit_loss":best,"fit_pixels":n,"coverage":stats,
         "method":"Fit real area lights to the milled flank. Measure both real satin and burnished endpoints for each card, estimate mixture on local patches, then attach the full-resolution bounded finish estimate to visible chest vertices."}
    configure_render(scene,144);scene["knight_routed_wood"]=json.dumps(cfg);save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False);scene=bpy.context.scene;configure_render(scene,144)
    render(scene,out/"wood.png");use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",cfg);print("KNIGHT_ROUTED_WOOD",initial,best,[(s["name"],s["watts"]) for s in details],flush=True)


if __name__=="__main__":main()
