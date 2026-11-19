"""Measure several unaltered saved scenes on one set of physical and camera rulers."""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).parent))
from shared_turning import BODY,BUTTON,ROOT,digest
from inspect_shared_turning import measure,render_level


def capture(key,source,out):
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene
    body,button=bpy.data.objects[BODY],bpy.data.objects[BUTTON]
    for obj in (body,button):
        for m in obj.modifiers:
            if m.type=='SUBSURF':m.levels=m.render_levels
    bpy.context.view_layer.update()
    result,unused=measure(scene,body,True)
    result['source_sha256']=digest(source)
    result['native_height_to_foot']=result['height']/result['foot_diameter']
    body_tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
    diameters=[]
    for z in np.linspace(1.65,2.66,220):
        hit,_,_,_=body_tree.ray_cast(Vector((-2.,0.,float(z))),Vector((1.,0.,0.)),4.)
        if hit is None:raise ValueError(f'Missing meridian at {z}')
        diameters.append([-2*float(hit.x),float(z)])
    diameter,waist_z=min(diameters)
    root_z=float(body.data.vertices[31*128].co.z)
    collar_z=float(body.data.vertices[39*128].co.z)
    result['stem']={'minimum_evaluated_diameter':diameter,'waist_height':waist_z,
                    'socket_join_ring_31_z':root_z,'collar_join_ring_39_z':collar_z,
                    'socket_to_collar_control_span':collar_z-root_z}
    tree=BVHTree.FromObject(button,bpy.context.evaluated_depsgraph_get())
    dome=[]
    for radius in (0.,.05,.10,.15,.20,.23,.25):
        location,_,_,_=tree.ray_cast(Vector((radius,0,5)),Vector((0,0,-1)),2)
        if location is not None:dome.append([radius,location.z])
    result['radial_button_top']=dome
    d=out/key;d.mkdir(exist_ok=True,parents=True)
    result['side']=render_level(scene,body,True,d)
    (d/'measures.json').write_text(json.dumps(result,indent=2)+'\n')
    print(key,result['height'],result['front_collar_rim_rows'],result['front_groove_row'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('cases',nargs='+')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    for case in args.cases:
        source=(ROOT/'history/bishop-mission-024/bishop-rebuilt.blend' if case=='024'
                else ROOT/'build/bishop-mission'/('185-'+case)/'bishop.blend')
        capture(case,source,ROOT/'build/bishop-mission/185-geometry')
