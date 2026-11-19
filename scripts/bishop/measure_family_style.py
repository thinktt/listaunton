"""Measure actual before/after geometry at the preserved camera."""
from pathlib import Path
import json,sys,hashlib
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from inspect_shared_turning import measure
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/bishop-mission/iteration-030'
cfg=json.loads((DOC/'family-style.json').read_text())
out={}
for key,source in [('before',cfg['source']),('after','build/bishop-mission/'+cfg['variant']+'/bishop.blend')]:
    path=ROOT/source;bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    body=bpy.data.objects['Bishop - continuous turned body']
    for mod in body.modifiers:
        if mod.type=='SUBSURF':mod.levels=mod.render_levels
    bpy.context.view_layer.update()
    values,profile=measure(bpy.context.scene,body,True)
    tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
    # Width of each rounded rim at half of its radial protrusion from its
    # adjacent neck. This distinguishes rim thickness from stack spacing.
    rim={}
    for name,low,high,neck in [('lower',2.77,2.99,.545),('middle',2.99,3.20,.465),('upper',3.22,3.40,.475)]:
        points=[]
        for z in np.arange(low,high,.0005):
            hit,_,_,_=tree.ray_cast(Vector((3,0,z)),Vector((-1,0,0)),3)
            if hit is not None:points.append([float(hit.x),float(z)])
        ar=np.array(points);rmax=ar[:,0].max();q=ar[ar[:,0]>=(rmax+neck)/2]
        rim[name]={'radius':float(rmax),'half_protrusion_thickness':float(q[-1,1]-q[0,1])}
    values.update(source=source,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),rim_measurements=rim)
    out[key]=values
(DOC/'measurements.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
