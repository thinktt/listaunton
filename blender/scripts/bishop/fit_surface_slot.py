"""Trace the original slit on an uncut saved bishop and orient its real rounded saw."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).parent))
from shared_turning import BODY, BUTTON, ROOT


def place_cutter(cutter, plane):
    """Rotate the existing cutter about Y then Z; anchor its floor and mid-plane."""
    a, b = plane['dx_dz'], plane['dx_dy']
    points = np.array([list(cutter.matrix_world @ v.co) for v in cutter.data.vertices])
    wall = points[0] - points[1]
    assert abs(wall[1]) < 1e-5 and wall[2] > .4
    yaw = -math.atan(b)
    pitch = math.atan(a*math.cos(yaw)) - math.atan2(wall[0],wall[2])
    rotation = Matrix.Rotation(yaw,4,'Z') @ Matrix.Rotation(pitch,4,'Y')
    turned = points @ np.array(rotation)[:3,:3].T
    dz = plane['floor_z'] - turned[:,2].min()
    intercepts = turned[:,0]-a*turned[:,2]-b*turned[:,1]
    x,z = plane['anchor_xz']
    dx = x-a*z-(intercepts.min()+intercepts.max())/2+a*dz
    transform = Matrix.Translation((dx,0,dz)) @ rotation
    cutter.data.transform(cutter.matrix_world.inverted() @ transform @ cutter.matrix_world)
    cutter.data.update()
    return np.asarray(transform).tolist()


def fit(source):
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene
    body,button=bpy.data.objects[BODY],bpy.data.objects[BUTTON]
    for obj in (body,button):
        for mod in obj.modifiers:
            if mod.type=='SUBSURF':mod.levels=mod.render_levels
    next(m for m in body.modifiers if m.type=='BOOLEAN').show_viewport=False
    bpy.context.view_layer.update()
    graph=bpy.context.evaluated_depsgraph_get()
    body_tree=BVHTree.FromObject(body,graph)
    cap_tree=BVHTree.FromObject(button,graph)
    w,h=scene.render.resolution_x,scene.render.resolution_y
    cam=scene.camera
    projection=cam.calc_matrix_camera(graph,x=w,y=h)
    m=projection @ cam.matrix_world.inverted()
    inverse=m.inverted()
    source_evidence=ROOT/'docs/bishop-mission/iteration-027/fit-proposals.json'
    features=json.loads(source_evidence.read_text())['original_white_features']
    samples=features['slit_dark_center_samples']+[[512,420]]
    hits=[]
    for x,y in samples:
        ndc=(2*(x+.5)/w-1,1-2*(y+.5)/h)
        lo=inverse@Vector((*ndc,-1,1))
        hi=inverse@Vector((*ndc,1,1))
        start=lo.xyz/lo.w
        direction=(hi.xyz/hi.w-start).normalized()
        p,_,_,dist=body_tree.ray_cast(start,direction)
        cap=cap_tree.ray_cast(start,direction)
        if p is not None and (cap[0] is None or cap[3]>dist):
            hits.append([x,y,*p])
    assert len(hits)>=14 and hits[-1][:2]==[512,420]
    arr=np.asarray(hits);xx,yy,zz=arr[:,2:].T
    zref=zz[-1]
    fitrows={}
    for label,design in [('frontal',np.column_stack((np.ones(len(zz)),zz-zref))),
                         ('yawed',np.column_stack((np.ones(len(zz)),zz-zref,yy)))]:
        fit=np.linalg.lstsq(design,xx,rcond=None)[0]
        fitrows[label]={'dx_dz':float(fit[1]),'dx_dy':float(fit[2]) if len(fit)==3 else 0.,
                        'anchor_xz':[float(fit[0]),float(zref)],'floor_z':float(zref-.031),
                        'rms_horizontal_px':float(np.sqrt(np.mean((design@fit-xx)**2))*w*m[0][0]/2)}
    return {'source':source.relative_to(ROOT).as_posix(),'surface_samples_original_white':hits,
            'method':'Pixel-center rays from the saved camera onto the uncut subdivided mitre, with button occlusion. Floor lies below the final optical sample to allow for the rounded toe.',
            'fits':fitrows}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    report=fit(ROOT/args.source)
    (ROOT/args.out).write_text(json.dumps(report,indent=2)+'\n')
    print('Original-white saw fits',report['fits'],flush=True)
