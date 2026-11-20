"""Trace which physical surface makes the upper-eye line at the fixed camera."""
import hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root,model,target,out=[Path(p).resolve() for p in sys.argv[sys.argv.index('--')+1:]]
sys.path.insert(0,str(root/'scripts/knight'))
from mission_scene import visible_meshes

source=hashlib.sha256(model.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
scene=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get()
cam=scene.camera
camera=np.array(cam.matrix_world);proj=np.asarray(cam.calc_matrix_camera(dep,x=1254,y=1254))
direction=-(cam.matrix_world.to_quaternion()@Vector((0,0,1)))
meshes=[]
for obj in visible_meshes(scene):
    inv=obj.matrix_world.inverted()
    name=obj.name.split('|')[-1].strip()
    meshes.append((name,obj.matrix_world.copy(),inv,BVHTree.FromObject(obj,dep),inv.to_3x3()@direction))
ids={'continuous horse head and neck':1,'near swept ear':2,'near eye':3}
xs=np.arange(466,560);ys=np.arange(453,502)
owners=np.zeros((len(ys),len(xs)),np.uint8)
depth=np.full(owners.shape,np.nan)
under=np.full(owners.shape,np.nan)
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        cp=np.array([((2*(x+.5)/1254-1)-proj[0,3])/proj[0,0],((1-2*(y+.5)/1254)-proj[1,3])/proj[1,1],0,1])
        camera_start=Vector((camera@cp)[:3]);hits=[]
        for name,world,inv,tree,ray in meshes:
            p,_,_,_=tree.ray_cast(inv@camera_start,ray,30)
            if p is not None:hits.append((((world@p)-camera_start).length,ids.get(name,4)))
        if not hits:continue
        hits.sort();depth[j,i],owners[j,i]=hits[0]
        skull=[t for t,name in hits if name==1]
        if skull:under[j,i]=skull[0]-depth[j,i]
record=json.loads(target.read_bytes())['results']['Black 2']['trace']
rows=np.array([y for x,y in record]);cols=np.array([x for x,y in record])
bands={}
for label,lo,hi in [('earward',472,486),('middle',487,522),('noseward',523,555)]:
    group=(cols>=lo)&(cols<=hi)
    bands[label]={}
    for delta in [-3,0,3,6]:
        t=rows[group]+delta-ys[0];k=cols[group]-xs[0]
        samples=owners[t,k];gaps=under[t,k][samples==2]
        bands[label][str(delta)]={'samples':len(samples),'skull':int((samples==1).sum()),'ear':int((samples==2).sum()),'insert':int((samples==3).sum()),'other':int((samples==4).sum()),
            'ear_to_skull_distance_along_camera_ray':round(float(np.nanmedian(gaps)),5) if len(gaps) else None}
np.savez_compressed(out.with_suffix('.npz'),xs=xs,ys=ys,owners=owners,depth=depth,under=under)
assert source==hashlib.sha256(model.read_bytes()).hexdigest()
out.with_suffix('.json').write_text(json.dumps({'model':source,'reference_trace_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
    'owner_ids':{'0':'background','1':'carved head','2':'near swept ear','3':'exposed eye insert','4':'other part'},'areas':bands,
    'method':'Cast the fixed camera through each pixel and intersect every visible evaluated component separately. Count foremost surfaces on the photographed upper crease and at the same columns three pixels above and three/six below. Ear-to-head distance is separation along the camera ray at the same pixel, which depends on camera elevation.'},indent=2)+'\n')
print(bands)
