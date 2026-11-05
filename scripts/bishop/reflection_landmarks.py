"""Place trial reflectors using actual surface normals at reference glints."""
import bpy, json, sys, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/bishop/bishop-rebuilt.blend'),load_ui=False)
s=bpy.context.scene;c=s.camera;bpy.context.view_layer.update();g=bpy.context.evaluated_depsgraph_get()
view=c.matrix_world.to_3x3()@Vector((0,0,1));proj=c.calc_matrix_camera(g,x=1254,y=1254);inverse=(proj@c.matrix_world.inverted()).inverted()
def cast(px,py):
    p=inverse@Vector((px/1254*2-1,1-py/1254*2,-1,1));p=Vector((p.x/p.w,p.y/p.w,p.z/p.w))
    hits=[]
    for o in s.objects:
        if o.type=='MESH' and not o.hide_render:
            tree=BVHTree.FromObject(o,g);loc,n,face,d=tree.ray_cast(p,-view,100)
            if loc is not None:hits.append((d,loc,n,o.name))
    d,loc,n,name=min(hits,key=lambda x:x[0]);direction=2*view.dot(n)*n-view
    return {'pixel':[px,py],'surface':list(loc),'normal':list(n),'object':name,'position':list(loc+direction*7),'target':list(loc),'light_direction':list(direction)}
points=json.loads(sys.argv[sys.argv.index('--')+1]);report={name:cast(*pixel) for name,pixel in points.items()}
(ROOT/'build/bishop-mission/reflection-landmarks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
