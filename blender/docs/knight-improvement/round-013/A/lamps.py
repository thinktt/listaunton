"""Aim the two existing physical reflection cards at the newly carved lips."""
from pathlib import Path
import json,sys,math,bpy,numpy as np
from mathutils import Matrix,Vector
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from cards import measure
def place(scene,aim,name,part,points,dist,axes,watts,spread):
    rays=[]
    for point in points:
        try:rays.append(aim(part,point))
        except RuntimeError:pass
    if len(rays)<2:raise ValueError(name)
    ps=np.array([k[1] for k in rays]);ns=np.array([k[2] for k in rays])
    n=np.median(ns,axis=0);n/=np.linalg.norm(n);p=np.median(ps,axis=0)+n*dist
    projected=ps+ns*(((p-ps)@n)/(ns@n))[:,None]
    midpoint=np.median(projected,axis=0)
    _,_,vt=np.linalg.svd(projected-midpoint);u=vt[0]-np.dot(n,vt[0])*n;u/=np.linalg.norm(u);v=np.cross(n,u)
    ob=scene.objects[name];ob.location=Vector(midpoint);ob.rotation_euler=Matrix(np.column_stack((u,v,n))).to_euler()
    ob.data.shape='ELLIPSE';ob.data.size,ob.data.size_y=axes;ob.data.energy=watts;ob.data.spread=np.radians(spread)
    bpy.context.view_layer.update()
    return {'name':name,'location':list(ob.location),'rotation':list(ob.rotation_euler),'ellipse':list(axes),'watts':watts,'spread_degrees':spread,'measured_pixels':[k[0] for k in rays]}
def configure(scene):
    aim=measure(scene)
    cards=[place(scene,aim,'Eye reflection upper','near eye',[(492,470),(497,472),(503,474),(510,478)],.61,(.355,.238),.074,24),
           place(scene,aim,'Eye reflection lower','continuous horse head and neck',[(488,496),(493,497),(500,499),(507,500),(514,501),(520,501)],.60,(.465,.266),.175,21)]
    scene.objects['Eye reflection lower'].data.color=(1.,.62,.37)
    cards[1]['color']=[1.,.62,.37]
    return cards
