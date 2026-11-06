"""Estimate a bounded, scalar varnish coverage on the actual knight carving.

Two Cycles measurements of the same wood isolate a plausible range of
reflected light. Only one material scalar is attached to each visible control
vertex. Color, shape, lights and the unseen surface's finish remain independent.
"""
import argparse
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from capture_material import read_pass
from fit_eye_reflection import display_transform
from mission_scene import ASSETS, BUILD, ROOT, configure_render, json_file, render, save_model, sha, use_side_camera, visible_meshes, world_vertices
from project_mission_pigment import surface_tree
sys.path.insert(0,str(ROOT/"scripts/queen"))
from image_math import blur

ATTRIBUTE="Knight varnish coverage"
PRIOR=.32


def varnish_endpoints(material):
    tree=material.node_tree
    polished=tree.nodes["Principled BSDF"]
    matte=tree.nodes.new("ShaderNodeBsdfPrincipled")
    matte.name="Satin walnut in open grain"
    for name in ("Base Color","Normal","Coat Normal"):
        tree.links.new(polished.inputs[name].links[0].from_socket,matte.inputs[name])
    matte.inputs["IOR"].default_value=polished.inputs["IOR"].default_value
    matte.inputs["Roughness"].default_value=.40
    matte.inputs["Specular IOR Level"].default_value=.055
    matte.inputs["Coat Weight"].default_value=.025
    matte.inputs["Coat Roughness"].default_value=.255
    polished.label="Burnished walnut"
    polished.inputs["Specular IOR Level"].default_value=.55
    polished.inputs["Coat Weight"].default_value=.72
    polished.inputs["Coat Roughness"].default_value=.077
    remap=polished.inputs["Roughness"].links[0].from_node
    assert remap.type=="MAP_RANGE"
    remap.inputs["To Min"].default_value=.165
    remap.inputs["To Max"].default_value=.26
    cover=tree.nodes.new("ShaderNodeMixShader");cover.name="Fraction of burnished surface"
    tree.links.new(matte.outputs[0],cover.inputs[1])
    tree.links.new(polished.outputs[0],cover.inputs[2])
    out=next(n for n in tree.nodes if n.type=="OUTPUT_MATERIAL" and n.is_active_output)
    tree.links.new(cover.outputs[0],out.inputs["Surface"])
    return cover


def read_reference():
    image=bpy.data.images.load(str(ASSETS/"ref.png"),check_existing=False)
    image.colorspace_settings.name="Non-Color"
    rgba=np.empty(1254*1254*4,dtype=np.float32)
    image.pixels.foreach_get(rgba)
    bpy.data.images.remove(image)
    return rgba.reshape(1254,1254,4)[::-1].copy()


def solve_field(scene,low,high,target,radius):
    transform=display_transform(scene)
    valid=(low[:,:,3]>.985)&(high[:,:,3]>.985)&(target[:,:,3]>.85)&(target[:,:,:3].max(2)>.045)
    a=low[:,:,:3][valid];delta=high[:,:,:3][valid]-a
    observed=target[:,:,:3][valid]
    best_loss=np.full(len(a),np.inf,np.float32)
    best=np.full(len(a),PRIOR,np.float32)
    rgb_weights=np.array([.20,.45,.35],np.float32)
    for factor in np.linspace(.015,.985,41,dtype=np.float32):
        predicted=a+factor*delta
        transform.applyRGB(predicted)
        loss=np.sum((predicted-observed)**2*rgb_weights,axis=1)+.00048*(factor-PRIOR)**2
        better=loss<best_loss;best_loss[better]=loss[better];best[better]=factor
    low_display=a.copy();high_display=a+delta
    transform.applyRGB(low_display);transform.applyRGB(high_display)
    contrast=np.linalg.norm(high_display-low_display,axis=1)
    confidence=np.zeros(valid.shape,np.float32)
    confidence[valid]=np.clip((contrast-.025)/.14,0,1)
    field=np.full_like(confidence,PRIOR);field[valid]=best
    smooth=blur(confidence*field,radius,2)/np.maximum(blur(confidence,radius,2),1e-6)
    gate=blur(confidence,radius,2)*blur(valid.astype(np.float32),3,2)
    return np.clip(PRIOR+np.minimum(.94,gate)*(smooth-PRIOR),.025,.94)


def attach_coverage(scene,objects,field,material,cover,region="all"):
    graph=bpy.context.evaluated_depsgraph_get()
    tree=surface_tree(objects)
    camera=scene.camera
    toward=camera.matrix_world.to_quaternion()@Vector((0,0,1))
    vp=np.asarray(camera.calc_matrix_camera(graph,x=1254,y=1254)@camera.matrix_world.inverted())
    stats={}
    for obj in objects:
        world=world_vertices(obj)
        uv=.5*(world@vp[:2,:3].T+vp[:2,3]+1)
        x=np.clip(np.rint(uv[:,0]*1254-.5).astype(int),0,1253)
        y=np.clip(np.rint((1-uv[:,1])*1254-.5).astype(int),0,1253)
        normals=np.empty(world.shape,np.float32)
        obj.data.vertices.foreach_get("normal",normals.ravel())
        normals=normals@np.linalg.inv(np.asarray(obj.matrix_world)[:3,:3])
        normals/=np.maximum(1e-7,np.linalg.norm(normals,axis=1))[:,None]
        facing=np.clip((normals@np.array(toward)-.035)/.29,0,1)
        weight=np.zeros(len(world),np.float32)
        for i in np.flatnonzero(facing):
            hit=tree.ray_cast(Vector(world[i])+15*toward,-toward,30)
            if hit[0] is not None:
                weight[i]=facing[i]*np.clip((.075-abs(hit[3]-15))/.05,0,1)
        attr=obj.data.attributes.get(ATTRIBUTE)
        previous=np.full(len(world),PRIOR,np.float32)
        if attr is not None:attr.data.foreach_get("value",previous)
        if region=="head":
            if obj.name.endswith("continuous horse head and neck"):
                weight*=np.clip((x-425)/60,0,1)*np.clip((555-y)/32,0,1)*np.clip((y-309)/47,0,1)
            elif not obj.name.endswith("swept ear"):
                weight.fill(0)
        values=previous+(field[y,x]-previous)*weight
        if attr is None:attr=obj.data.attributes.new(ATTRIBUTE,"FLOAT","POINT")
        attr.data.foreach_set("value",values.astype(np.float32))
        stats[obj.name]={"vertex_count":len(values),"minimum":float(values.min()),"mean":float(values.mean()),
                         "maximum":float(values.max()),"visible_fraction":float(np.mean(weight>.5))}
    node=next((n for n in material.node_tree.nodes if n.type=="ATTRIBUTE" and n.attribute_name==ATTRIBUTE),None)
    if node is None:
        node=material.node_tree.nodes.new("ShaderNodeAttribute");node.attribute_name=ATTRIBUTE
    material.node_tree.links.new(node.outputs["Fac"],cover.inputs[0])
    return stats


def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True)
    p.add_argument("--variant",required=True);p.add_argument("--radius",type=int,default=5)
    p.add_argument("--samples",type=int,default=144)
    p.add_argument("--region",choices=["all","head"],default="all")
    args=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    out=BUILD/args.variant;out.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(args.source),load_ui=False)
    scene=bpy.context.scene;objects=visible_meshes(scene);material=objects[0].data.materials[0]
    mix=material.node_tree.nodes.get("Fraction of burnished surface")
    if mix is None:
        mix=varnish_endpoints(material)
    else:
        assert mix.type=="MIX_SHADER" and mix.inputs[0].is_linked
        assert mix.inputs[0].links[0].from_node.attribute_name==ATTRIBUTE
        material.node_tree.links.remove(mix.inputs[0].links[0])
    configure_render(scene,112);mix.inputs[0].default_value=0
    satin=read_pass(scene,out/"satin.exr")
    mix.inputs[0].default_value=1;polished=read_pass(scene,out/"burnished.exr")
    field=solve_field(scene,satin,polished,read_reference(),args.radius)
    stats=attach_coverage(scene,objects,field,material,mix,args.region)
    cfg={"source_sha256":sha(args.source),"samples":args.samples,"measurement_samples":112,
         "attribute":ATTRIBUTE,"hidden_prior":PRIOR,"image_smoothing_radius":args.radius,"per_component":stats,"region":args.region,
         "method":"Two measured dielectric finishes share the same albedo and relief. Fit a smoothed coverage scalar only at visible 3D vertices; use a uniform prior elsewhere. No reference RGB is connected to a shader."}
    scene["knight_variable_polish"]=json.dumps(cfg)
    configure_render(scene,args.samples);save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False);scene=bpy.context.scene
    configure_render(scene,args.samples)
    render(scene,out/"wood.png");use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",cfg)
    print("KNIGHT_VARNISH_REOPENED",stats,flush=True)


if __name__=="__main__":main()
