"""Check a saved chest revision against the accepted full knight scene."""
import argparse
from pathlib import Path
import sys
import bpy
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from mission_scene import json_file,sha,world_vertices

def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    scene=bpy.context.scene
    camera=scene.camera
    records={}
    for obj in scene.objects:
        if obj.type!="MESH":continue
        m=obj.data
        uv=np.empty(len(m.loops)*2 if m.uv_layers.active else 0,np.float32)
        if len(uv):m.uv_layers.active.data.foreach_get("uv",uv)
        records[obj.name]={"points":world_vertices(obj),"uv":uv,
            "faces":[tuple(p.vertices) for p in m.polygons],
            "hidden":bool(obj.hide_render)}
    return records,{"world":[list(r) for r in camera.matrix_world],
        "type":camera.data.type,"scale":camera.data.ortho_scale,
        "shift":[camera.data.shift_x,camera.data.shift_y],
        "resolution":[scene.render.resolution_x,scene.render.resolution_y],
        "foot_center_x":float(scene.get("knight_foot_center_x",0))}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--previous",type=Path,required=True)
    p.add_argument("--current",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    old,oldcamera=snapshot(a.previous)
    new,camera=snapshot(a.current)
    assert camera==oldcamera and set(new)==set(old)
    allowed={"Knight | continuous horse head and neck","Knight | curved neck and chest"}
    report={}
    for name,now in new.items():
        prev=old[name]
        assert prev["faces"]==now["faces"] and np.array_equal(prev["uv"],now["uv"]),name
        assert prev["hidden"]==now["hidden"],name
        A=prev["points"];B=now["points"]
        delta=np.linalg.norm(B-A,axis=1)
        assert np.isfinite(B).all()
        zerror=float(np.max(np.abs(A[:,2]-B[:,2])))
        assert zerror<2e-6,(name,zerror)
        if name in allowed:
            protected=(A[:,2]<=1.76)|(A[:,2]>=4.20)
            assert float(delta[protected].max(initial=0))<3e-6,name
            assert float(delta.max())<.10,(name,delta.max())
        else:assert np.array_equal(A,B),name
        report[name]={"vertices":len(A),"changed_vertices":int((delta>3e-6).sum()),
            "maximum_displacement":float(delta.max()),"maximum_height_change":zerror,
            "uvs_and_faces_preserved":True}
    result={"prior_sha256":sha(a.previous),"source_sha256":sha(a.current),
        "camera_and_foot_center_preserved":True,"parts":report,
        "scope":"Only the chest and matching hidden construction loft may move; all heights, upper head, lower seat, UVs, topology and other components are preserved."}
    json_file(a.output,result)
    print("KNIGHT_CHEST_SCOPE_OK",report,flush=True)

if __name__=="__main__":main()
