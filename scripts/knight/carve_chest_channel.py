"""Shape a bilateral chest channel on the editable horse and the matching loft."""
import argparse
import json
from pathlib import Path
import sys
import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from capture_material import read_pass
from export_mission import export
from fit_eye_reflection import display_transform
from fit_surface_polish import read_reference
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import ASSETS,BUILD,MODEL,ROOT,configure_render,json_file,render,save_model,sha,use_side_camera,visible_meshes,world_vertices
from refine_eye import apply_world
sys.path.insert(0,str(ROOT/"scripts/queen"))
from image_math import blur

NAMES=("trough","bevel","crest","shoulder","panel","far_lip")
WIDTHS=np.array([.043,.039,.052,.148,.145,.047])
SIGNS=np.array([-1,1,1,1,-1,1])
INITIAL=np.array([.042,.016,.020,.038,.022,.013])
CAPS=np.array([.105,.065,.075,.135,.085,.055])
CROP=(294,534,704,777)


def ease(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)


def setup_deformation(scene,paths):
    objects=[bpy.data.objects["Knight | continuous horse head and neck"],
             bpy.data.objects["Knight | curved neck and chest"]]
    pose=paths["pose"];foot=paths["foot_center_x"];prepared=[]
    for obj in objects:
        original=world_vertices(obj)
        untied=original.copy()
        untied[:,0]-=foot*ease((2.48-untied[:,2])/.72)
        rest=rest_coords(untied,pose);x,y,z=rest.T
        columns=[]
        for name,width,sign in zip(NAMES,WIDTHS,SIGNS):
            curve=np.array([r["rest"] for r in paths["curves"][name]])
            curve=curve[np.argsort(curve[:,2])]
            zc,xc=curve[:,2],curve[:,0]
            # A physical cross-section perpendicular to this carved line.
            axis=np.interp(z,zc,xc)
            slope=np.interp(z,zc,np.gradient(xc,zc))
            d=(x-axis)/np.sqrt(1+slope*slope)
            ends=ease((z-zc[0]+.047)/.225)*ease((zc[-1]+.052-z)/.23)
            side=ease((np.abs(y)-.20)/.29)
            columns.append(sign*ends*side*np.exp(-.5*(d/width)**2))
        basis=np.column_stack(columns)
        # Only depth changes. Preserve side-profile X and Z, closed topology,
        # pigment coordinates, the floor, and the top of the accepted carving.
        moved=rest.copy();moved[:,1]+=np.sign(y)
        direction=posed(moved,*pose)-posed(rest,*pose)
        prepared.append((obj,original,direction,basis))
    def apply(values):
        for obj,original,direction,basis in prepared:
            height=basis@values
            apply_world(obj,original+height[:,None]*direction)
        bpy.context.view_layer.update()
    return apply


def fit_rendered(scene,apply,values,out):
    x0,y0,x1,y1=CROP;w=1254
    configure_render(scene,96);scene.cycles.use_light_tree=False
    scene.render.use_border=True;scene.render.use_crop_to_border=True
    scene.render.border_min_x=(x0+.05)/w;scene.render.border_max_x=(x1+.05)/w
    scene.render.border_min_y=(w-y1+.05)/w;scene.render.border_max_y=(w-y0+.05)/w
    target=read_reference()[y0:y1,x0:x1]
    transform=display_transform(scene)
    yy,xx=np.indices(target.shape[:2]);yy+=y0;xx+=x0
    axis=np.interp(yy,[548,585,605,625,645,665,685,705,725,747],[400,432,450,473,493,514,533,554,574,602])
    mask=(yy>557)&(yy<740)&(xx>axis-101)&(xx<axis+89)&(target[:,:,3]>.94)
    weight=(1+.52*np.exp(-((xx-axis+32)/15)**2)+.5*np.exp(-((xx-axis)/8)**2))
    mask&=(xx%2==0)&(yy%2==0);importance=np.sqrt(weight[mask]).astype(np.float32)
    def representation(rgb):
        smooth=blur(rgb,2,2)
        gray=smooth@np.array([.24,.64,.12],np.float32)
        contrast=gray-blur(gray,7,3)
        return np.column_stack((smooth[mask]*importance[:,None],1.55*contrast[mask]*importance)).ravel()
    goal=representation(target[:,:,:3]);runs=[]
    def measure(v,name):
        apply(v)
        raw=read_pass(scene,out/(name+".exr"))
        rgb=np.ascontiguousarray(raw[:,:,:3],dtype=np.float32);transform.applyRGB(rgb)
        vector=representation(rgb)
        cost=float(np.mean(np.abs(vector-goal)))
        runs.append({"label":name,"depths":v.tolist(),"mean_feature_error":cost})
        return vector,cost
    current,loss=measure(values,"start")
    best=values.copy()
    for iteration in range(2):
        delta=np.array([.008,.006,.006,.011,.008,.006])*(1-.20*iteration)
        response=[]
        for i,step in enumerate(delta):
            attempt=best.copy();attempt[i]+=step
            sample,_=measure(attempt,f"round-{iteration}-{NAMES[i]}")
            response.append((sample-current)/step)
        jac=np.column_stack(response)
        residual=goal-current
        robust=1/np.sqrt(.045**2+residual**2)
        lhs=jac.T@(jac*robust[:,None])
        rhs=jac.T@(robust*residual)
        damping=.08*np.diag(lhs)+2.5
        update=np.linalg.solve(lhs+np.diag(damping),rhs)
        update=np.clip(update,-.026,.026)
        improved=False
        for fraction in (1,.5):
            attempt=np.clip(best+fraction*update,0,CAPS)
            sample,error=measure(attempt,f"round-{iteration}-check-{fraction}")
            if error<loss-1e-5:
                best,current,loss=attempt,sample,error;improved=True;break
        if not improved:break
    scene.render.use_border=False;scene.render.use_crop_to_border=False;scene.cycles.use_light_tree=True
    apply(best)
    return best,runs


def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,default=MODEL)
    p.add_argument("--paths",type=Path,required=True);p.add_argument("--variant",required=True)
    p.add_argument("--fit",action="store_true");p.add_argument("--samples",type=int,default=144)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    out=BUILD/a.variant;out.mkdir(exist_ok=True)
    paths=json.loads(a.paths.read_text());assert paths["source_sha256"]==sha(a.source)
    bpy.ops.wm.open_mainfile(filepath=str(a.source),load_ui=False);scene=bpy.context.scene
    apply=setup_deformation(scene,paths);values=INITIAL.copy();runs=[]
    if a.fit:values,runs=fit_rendered(scene,apply,values,out)
    apply(values)
    cfg={"source_sha256":sha(a.source),"landmarks_sha256":sha(a.paths),"samples":a.samples,
         "widths":dict(zip(NAMES,WIDTHS.tolist())),"depths":dict(zip(NAMES,values.tolist())),
         "crop":CROP,"render_measurements":runs,"method":"Carve six smooth bilateral cross-section terms in real mesh coordinates along the observed shoulder, channel, bevels and inset panel. The chosen model retains the accepted physical height and seated base."}
    configure_render(scene,a.samples);scene["knight_chest_carving"]=json.dumps(cfg)
    save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False);scene=bpy.context.scene
    configure_render(scene,a.samples)
    tex=ASSETS/json.loads((ASSETS/"mission-checkpoint.json").read_text())["texture_file"];export(scene,tex,output=out,source=out/"knight.blend")
    render(scene,out/"wood.png")
    objects=visible_meshes(scene);wood=objects[0].data.materials[0];clay=bpy.data.materials["Neutral satin clay"]
    for obj in objects:obj.data.materials[0]=clay
    render(scene,out/"neutral.png");use_side_camera(scene);render(scene,out/"side-neutral.png")
    for obj in objects:obj.data.materials[0]=wood
    render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",cfg);print("KNIGHT_CHEST_CARVING",dict(zip(NAMES,values)),flush=True)


if __name__=="__main__":main()
