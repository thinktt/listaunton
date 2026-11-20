"""Place reflectors using interpolated shading normals at measured reference glints."""
import argparse, bpy, hashlib, json, math, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('points',help='JSON object or repo-relative JSON file of named [x,y] image points')
p.add_argument('--source',default='models/bishop/bishop-rebuilt.blend')
p.add_argument('--out',default='build/bishop-mission/reflection-landmarks.json')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
points=json.loads(a.points) if a.points.lstrip().startswith('{') else json.loads((ROOT/a.points).read_text())
source=ROOT/a.source;bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;c=s.camera;bpy.context.view_layer.update();g=bpy.context.evaluated_depsgraph_get()
w=s.render.resolution_x;h=s.render.resolution_y
view=(c.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
inverse=(c.calc_matrix_camera(g,x=w,y=h)@c.matrix_world.inverted()).inverted()
surfaces=[]
for ob in s.objects:
    if ob.type!='MESH' or ob.hide_render:continue
    evaluated=ob.evaluated_get(g);mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
    vertices=[ob.matrix_world@v.co for v in mesh.vertices]
    triangles=[tuple(tri.vertices) for tri in mesh.loop_triangles]
    normal_matrix=ob.matrix_world.to_3x3().inverted().transposed()
    normals=[[normal_matrix@mesh.corner_normals[li].vector for li in tri.loops] for tri in mesh.loop_triangles]
    surfaces.append((ob.name,BVHTree.FromPolygons(vertices,triangles,all_triangles=True),vertices,triangles,normals))
    evaluated.to_mesh_clear()

def cast(px,py):
    point=inverse@Vector((px/w*2-1,1-py/h*2,-1,1));point=Vector((point.x/point.w,point.y/point.w,point.z/point.w))
    hits=[]
    for name,tree,vertices,triangles,normals in surfaces:
        loc,facet,index,distance=tree.ray_cast(point,-view,100)
        if loc is None:continue
        aa,bb,cc=[vertices[i] for i in triangles[index]]
        u=bb-aa;v=cc-aa;q=loc-aa
        uu=u.dot(u);uv=u.dot(v);vv=v.dot(v);qu=q.dot(u);qv=q.dot(v)
        denom=uu*vv-uv*uv;wb=(vv*qu-uv*qv)/denom;wc=(uu*qv-uv*qu)/denom;wa=1-wb-wc
        normal=sum((weight*n for weight,n in zip([wa,wb,wc],normals[index])),Vector()).normalized()
        hits.append((distance,loc,normal,facet,name,[wa,wb,wc]))
    distance,loc,normal,facet,name,weights=min(hits,key=lambda item:item[0])
    direction=2*view.dot(normal)*normal-view
    return {'pixel':[px,py],'surface':list(loc),'normal':list(normal),'facet_normal':list(facet),
            'normal_difference_degrees':math.degrees(normal.angle(facet)), 'barycentric_weights':weights,
            'object':name,'position':list(loc+direction*7),'target':list(loc),'light_direction':list(direction)}

result={name:cast(*pixel) for name,pixel in points.items()}
result['_provenance']={'source':a.source,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                       'method':'Barycentric interpolation of evaluated triangle-corner shading normals, preserving split normals; bumps are not included.'}
path=ROOT/a.out;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
