"""Refine the existing turned foot and collar in place at their original scale."""
import argparse
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from export_mission import export
from mission_scene import ASSETS,BUILD,MODEL,ROOT,configure_render,json_file,render,save_model,sha,use_side_camera,visible_meshes


FOOT={
    3:(1.467,.070),4:(1.482,.105),5:(1.484,.341),
    6:(1.486,.380),7:(1.484,.407),8:(1.470,.425),
    9:(1.452,.440),10:(1.447,.461),11:(1.462,.481),
    12:(1.484,.521),13:(1.495,.640),
}
COLLAR={
    18:(1.246,1.270),19:(1.202,1.340),20:(1.184,1.393),
    21:(1.186,1.430),22:(1.213,1.451),23:(1.226,1.474),
    24:(1.226,1.500),25:(1.211,1.521),26:(1.160,1.565),
    27:(1.102,1.633),28:(1.076,1.690),
}


def bounds(obj):
    graph=bpy.context.evaluated_depsgraph_get()
    ev=obj.evaluated_get(graph);me=ev.to_mesh()
    co=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get("co",co.ravel())
    ev.to_mesh_clear()
    return np.min(co,axis=0),np.max(co,axis=0)


def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,default=MODEL)
    p.add_argument("--variant",required=True);p.add_argument("--collar",action="store_true")
    p.add_argument("--samples",type=int,default=112)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);out=BUILD/a.variant;out.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(a.source),load_ui=False);scene=bpy.context.scene
    obj=bpy.data.objects["Knight | turned pedestal"];before=bounds(obj)
    assert np.allclose(obj.matrix_world,np.eye(4),atol=1e-7)
    measured=np.empty((len(obj.data.vertices),3),np.float32);obj.data.vertices.foreach_get("co",measured.ravel())
    rings=measured.astype(float).reshape(-1,64,3)
    radii=np.linalg.norm(rings[:,:,:2],axis=2).mean(axis=1)
    old=np.column_stack((radii,rings[:,:,2].mean(1)))
    source=np.array(json.loads((ROOT/"scripts/knight/profile.json").read_text())["base"])
    assert np.allclose(old,source,atol=.00002), "This trial expects the original turned control rings."
    profile=old.copy()
    edits=dict(FOOT)
    if a.collar:edits.update(COLLAR)
    for i,pair in edits.items():profile[i]=pair
    def update():
        points=rings.copy()
        points[:,:,:2]*=(profile[:,0]/radii)[:,None,None]
        points[:,:,2]=profile[:,1,None]
        obj.data.vertices.foreach_set("co",points.astype(np.float32).ravel())
        obj.data.update();bpy.context.view_layer.update()
    update()
    # Hold the established side-guide foot scale and the floor. Correct only
    # the equator of the barrel for the small shift induced by subdivision.
    equator=np.exp(-((profile[:,1]-.735)/.135)**4)
    for _ in range(5):
        delta=before[1][0]-bounds(obj)[1][0]
        if abs(delta)<.000001:break
        profile[:,0]+=delta*equator
        update()
    after=bounds(obj)
    assert np.allclose(before,after,atol=.000003),(before,after)
    cfg={"source_sha256":sha(a.source),"samples":a.samples,"before_profile":old.tolist(),"after_profile":profile.tolist(),
         "collar_changed":a.collar,"fixed_bounds_before":[v.tolist() for v in before],
         "fixed_bounds_after":[v.tolist() for v in after],"method":"Re-turn the control rings of the same closed pedestal. Lower and widen the shallow foot groove. Optional collar changes narrow the outer bead and replace its rounded top with a smoother transition into the seated carving. Preserve the floor and evaluated envelope."}
    configure_render(scene,a.samples);scene["knight_pedestal_fit"]=json.dumps(cfg)
    save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False);scene=bpy.context.scene
    configure_render(scene,a.samples)
    texture=ASSETS/json.loads((ASSETS/"mission-checkpoint.json").read_text())["texture_file"]
    export(scene,texture,output=out,source=out/"knight.blend")
    render(scene,out/"wood.png");use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",cfg);print("KNIGHT_TURNED_PEDESTAL",a.variant,before,after,flush=True)


if __name__=="__main__":main()
