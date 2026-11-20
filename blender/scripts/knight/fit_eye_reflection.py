"""Fit a small real reflected catchlight to the carved lateral eye.

The fixed image guides light placement and evaluation. The final image is
rendered from the reopened scene with the ordinary wood BSDF.
"""
from pathlib import Path
import math
import sys

import bpy
import numpy as np
import PyOpenColorIO as ocio
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).parent))
from mission_scene import BUILD,configure_render,json_file,render,save_model,sha,use_side_camera
from probe_carving import point_probe
from capture_material import read_pass

SOURCE=BUILD/"012-lower-carving/knight.blend"
OUT=BUILD/"013-eye-reflection"
# Frame coordinates with a little room for the lower eyelid.
X0,Y0,X1,Y1=459,451,558,510


def smooth_normal(obj, point, fallback):
    graph=bpy.context.evaluated_depsgraph_get()
    ev=obj.evaluated_get(graph);mesh=ev.to_mesh();mesh.calc_loop_triangles()
    world=np.asarray(obj.matrix_world)
    co=np.array([tuple(v.co) for v in mesh.vertices])@world[:3,:3].T+world[:3,3]
    p=np.array(point);best=None
    for tri in mesh.loop_triangles:
        xyz=co[list(tri.vertices)];ab,ac=xyz[1]-xyz[0],xyz[2]-xyz[0]
        ab2,ac2,cross=np.dot(ab,ab),np.dot(ac,ac),np.dot(ab,ac)
        denominator=ab2*ac2-cross*cross
        if denominator<1e-15:continue
        d=p-xyz[0];u=(np.dot(d,ab)*ac2-np.dot(d,ac)*cross)/denominator
        v=(np.dot(d,ac)*ab2-np.dot(d,ab)*cross)/denominator
        if min(1-u-v,u,v)<-.003:continue
        dist=np.linalg.norm(d-u*ab-v*ac)
        if best is None or dist<best[0]:
            ns=np.array([tuple(mesh.corner_normals[i].vector) for i in tri.loops])
            n=(np.array([1-u-v,u,v])@ns)@np.linalg.inv(world[:3,:3])
            best=(dist,n/np.linalg.norm(n))
    ev.to_mesh_clear()
    return Vector(best[1]) if best and best[0]<.003 else fallback


def display_transform(scene):
    config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path("LOCAL"))/"datafiles/colormanagement/config.ocio"))
    assert scene.view_settings.look=="None" and scene.view_settings.exposure==0 and scene.view_settings.gamma==1
    return config.getProcessor(ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,
                display=scene.display_settings.display_device,view=scene.view_settings.view_transform)).getDefaultCPUProcessor()


def main():
    OUT.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False)
    scene=bpy.context.scene
    probe=point_probe(scene);view=scene.camera.matrix_world.to_quaternion()@Vector((0,0,1))
    collection=bpy.data.collections.new("Knight | eye reflection receivers")
    for side in ("near","far"):collection.objects.link(bpy.data.objects["Knight | "+side+" eye"])
    lights=[];details=[]
    for label,x,y,size in [("upper",504,473,.15),("lower",509,481,.22),("upper-wide",503,474,.30)]:
        hits=[]
        for cy in range(y-6,y+7):
            for cx in range(x-6,x+7):
                hit=probe(cx,cy)
                if hit and hit[1]=="Knight | near eye":hits.append(((cx-x)**2+(cy-y)**2,cx,cy,hit))
        if not hits:continue
        _,cx,cy,hit=min(hits,key=lambda row:row[0]);_,obj_name,point,n=hit
        n=smooth_normal(bpy.data.objects[obj_name],point,n)
        reflection=(2*max(.001,view.dot(n))*n-view).normalized()
        distance=1.15
        data=bpy.data.lights.new("Eye reflection "+label,"AREA")
        data.shape="DISK";data.size=size;data.color=(1,.91,.81);data.energy=0
        lamp=bpy.data.objects.new(data.name,data);scene.collection.objects.link(lamp)
        lamp.location=point+distance*reflection
        lamp.rotation_euler=(point-lamp.location).to_track_quat("-Z","Y").to_euler()
        lamp.visible_diffuse=False;lamp.visible_glossy=True
        lamp.light_linking.receiver_collection=collection
        lights.append(lamp)
        details.append({"name":lamp.name,"nominal_pixel":[x,y],"on_eye_pixel":[cx,cy],
                        "position":list(lamp.location),"size":size,"normal":list(n)})
    assert lights
    configure_render(scene,256);scene.cycles.use_denoising=False
    scene.cycles.use_light_tree=False
    scene.render.use_border=True;scene.render.use_crop_to_border=True
    # Blender uses integer truncation when setting cropped bounds. Put each
    # boundary just inside its integer bin; the exported crop is then exact.
    w=h=1254
    scene.render.border_min_x=(X0+.05)/w;scene.render.border_max_x=(X1+.05)/w
    scene.render.border_min_y=(h-Y1+.05)/h;scene.render.border_max_y=(h-Y0+.05)/h
    base=read_pass(scene,OUT/"no-added-glint.exr")[:,:,:3]
    assert base.shape[:2]==(Y1-Y0,X1-X0),base.shape
    basis=[]
    for i,lamp in enumerate(lights):
        lamp.data.energy=10
        measured=read_pass(scene,OUT/("response-"+str(i)+".exr"))[:,:,:3]
        basis.append(np.maximum(measured-base,0));lamp.data.energy=0
    basis=np.array(basis,dtype=np.float32)
    transform=display_transform(scene)
    target=np.load(BUILD/"material-observations/reference-display.npy")[Y0:Y1,X0:X1,:3]
    gy,gx=np.indices(target.shape[:2]);weight=(.15+np.exp(-((gx+X0-506)/21)**2-((gy+Y0-478)/11)**2))
    weight*=1+3*np.clip((target.min(2)-.25)/.4,0,1)
    def error(factors):
        linear=np.ascontiguousarray(base+np.tensordot(factors.astype(np.float32),basis,axes=1))
        transform.applyRGB(linear)
        return float(np.sum(weight[:,:,None]*(linear-target)**2)/weight.sum())
    factors=np.zeros(len(lights))
    initial=best=error(factors)
    for step in (4.,1.,.25,.06,.015):
        for _ in range(36):
            previous=best
            for i in range(len(factors)):
                for sign in (-1,1):
                    candidate=factors.copy();candidate[i]+=sign*step
                    if candidate[i]<0 or candidate[i]>32:continue
                    value=error(candidate)
                    if value<best-1e-8:factors,best=candidate,value
            if best==previous:break
    for i,lamp in enumerate(lights):
        lamp.data.energy=float(factors[i]*10)
        details[i]["energy"]=float(lamp.data.energy)
        if lamp.data.energy==0:bpy.data.objects.remove(lamp,do_unlink=True)
    scene.render.use_border=False;scene.render.use_crop_to_border=False
    configure_render(scene,96);scene.cycles.use_light_tree=True
    cfg={"source_sha256":sha(SOURCE),"crop":[X0,Y0,X1,Y1],"initial_display_loss":initial,
         "predicted_display_loss":best,"reflectors":details,"basis_samples":256,"samples":96,
         "method":"Only the eyes receive the added glossy light. Solve nonnegative powers against actual cropped Cycles responses with the saved AgX display transform."}
    scene["knight_eye_lights"]=__import__("json").dumps(cfg)
    save_model(scene,OUT/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(OUT/"knight.blend"),load_ui=False)
    scene=bpy.context.scene;configure_render(scene,96)
    render(scene,OUT/"wood.png");use_side_camera(scene);render(scene,OUT/"wood-side.png")
    json_file(OUT/"parameters.json",cfg)
    print("KNIGHT_EYE_LIGHTS",initial,best,details,flush=True)


if __name__=="__main__":main()
