"""Ray-project the actual mitre interior without using color or illumination.

Diagnostic only: do not save or change the scene. The mask labels which
surface is hit, not which reference pixels happen to be dark.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',default='models/bishop/bishop-rebuilt.blend')
p.add_argument('--out',default='build/bishop-mission/144-surface-audit')
p.add_argument('--border',nargs=4,type=int,default=[450,210,595,460])
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);source=ROOT/a.source;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
digest=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);scene=bpy.context.scene
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
vertices=[];triangles=[];labels=[]
for name in ['Bishop - continuous turned body','Bishop - domed button finial']:
    ob=bpy.data.objects[name].evaluated_get(deps);mesh=ob.to_mesh();mesh.calc_loop_triangles();offset=len(vertices)
    vertices += [ob.matrix_world@v.co for v in mesh.vertices]
    for tri in mesh.loop_triangles:
        triangles.append(tuple(offset+i for i in tri.vertices))
        labels.append(3 if 'finial' in name else 2 if mesh.polygons[tri.polygon_index].material_index==1 else 1)
    ob.to_mesh_clear()
bvh=BVHTree.FromPolygons(vertices,triangles,all_triangles=True)
w,h=scene.render.resolution_x,scene.render.resolution_y
camera=scene.camera;projection=camera.calc_matrix_camera(deps,x=w,y=h,scale_x=scene.render.pixel_aspect_x,scale_y=scene.render.pixel_aspect_y)
direction=camera.matrix_world.to_3x3()@Vector((0,0,-1))
elevation=math.degrees(math.asin(-direction.normalized().z))
assert camera.data.type=='ORTHO' and abs(elevation-54)<1e-4
inverse=(projection@camera.matrix_world.inverted()).inverted()
x0,y0,x1,y1=a.border;mask=np.zeros((h,w),dtype=np.uint8)
for y in range(y0,y1):
    for x in range(x0,x1):
        ndc_x=2*(x+.5)/w-1;ndc_y=1-2*(y+.5)/h
        p0=inverse@Vector((ndc_x,ndc_y,-1,1));p1=inverse@Vector((ndc_x,ndc_y,1,1))
        start=p0.xyz/p0.w;end=p1.xyz/p1.w
        hit,normal,index,distance=bvh.ray_cast(start,(end-start).normalized())
        if index is not None:mask[y,x]=labels[index]
np.save(out/'surface-labels.npy',mask)
records=[]
for y in range(y0,y1):
    xs=np.flatnonzero(mask[y]==2)
    if xs.size:records.append({'y':y,'left':int(xs[0]),'right':int(xs[-1]),'width':int(xs.size)})
assert records and sha(source)==digest
report={'source':a.source,'source_sha256':digest,'camera_degrees_measured':elevation,'border':a.border,
    'labels':{'0':'no hit or outside crop','1':'body exterior','2':'mitre interior','3':'button'},
    'method':'First-hit rays at native pixel centers against evaluated body and button triangles; exact saved orthographic camera, no material shading or image fitting.',
    'slit_rows':records,'source_unchanged':True}
(out/'slit-boundary.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'captured':True,'source_sha256':digest,'cut_pixels':int((mask==2).sum()),'last_cut_row':records[-1]}),flush=True)
