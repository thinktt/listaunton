"""Trace physical visibility from the collar to candidate studio directions."""
import argparse,json,math,sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,BUILD,Surface,control,fixed_camera,save_json,sha


def run(source,edge_file,out):
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene
    fixed_camera(scene)
    surface=Surface(scene,control(scene))
    data=json.loads(edge_file.read_text())
    edge=np.array(data["edge_xy"]["031-lower-cheek"])
    points={}
    for offset in (.8,2.,4.,6.,9.,13.):
        rays=[]
        for x,y in edge[::3]:
            if 434<=x<=529:
                hit,n=surface.hit(x,y+offset)
                rays.append(hit+0.00010*n)
        points[offset]=rays
    rows=[]
    for azimuth in (-9,0,9):
        phi=math.radians(azimuth)
        for elevation in (54.5,56,57.5,59,61,64,68,72,78):
            theta=math.radians(elevation)
            direction=Vector((math.sin(phi)*math.cos(theta),-math.cos(phi)*math.cos(theta),math.sin(theta)))
            fractions=[]
            for samples in points.values():
                visible=sum(surface.tree.ray_cast(p,direction,50)[0] is None for p in samples)
                fractions.append(visible/len(samples))
            rows.append({"angle":elevation,"azimuth":azimuth,"visible_fraction":fractions})
    save_json(out,{"source_sha256":sha(source),"offsets_pixels":list(points),"rays":rows,"method":"Visibility to distant studio directions from actual ray hits on the collar, offset by 0.00010 model units along the smooth normal."})
    for row in rows:
        if row["azimuth"]==0:print(row,flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("source",type=Path);p.add_argument("edge_file",type=Path);p.add_argument("out",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);run(ROOT/a.source,ROOT/a.edge_file,ROOT/a.out)
