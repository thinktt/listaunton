"""Measure the bishop base geometry and existing light directions without edits."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();ob=bpy.data.objects['Bishop - continuous turned body']
ev=ob.evaluated_get(graph);me=ev.to_mesh();me.calc_loop_triangles();vertices=[ob.matrix_world@v.co for v in me.vertices]
triangles=[tuple(t.vertices) for t in me.loop_triangles];nm=ob.matrix_world.to_3x3().inverted().transposed()
normals=[[nm@me.corner_normals[li].vector for li in t.loops] for t in me.loop_triangles]
tree=BVHTree.FromPolygons(vertices,triangles,all_triangles=True);w=s.render.resolution_x;h=s.render.resolution_y
c=s.camera;view=(c.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
inverse=(c.calc_matrix_camera(graph,x=w,y=h)@c.matrix_world.inverted()).inverted();lamp=bpy.data.objects['base reflection']
records=[]
for x in [570,584]:
    for y in range(900,1041,2):
        p=inverse@Vector((x/w*2-1,1-y/h*2,-1,1));p=Vector((p.x/p.w,p.y/p.w,p.z/p.w))
        loc,facet,idx,dist=tree.ray_cast(p,-view,100)
        if loc is None:continue
        aa,bb,cc=[vertices[i] for i in triangles[idx]];u=bb-aa;v=cc-aa;q=loc-aa
        uu=u.dot(u);uv=u.dot(v);vv=v.dot(v);qu=q.dot(u);qv=q.dot(v);denom=uu*vv-uv*uv
        wb=(vv*qu-uv*qv)/denom;wc=(uu*qv-uv*qu)/denom
        n=sum((weight*nn for weight,nn in zip([1-wb-wc,wb,wc],normals[idx])),Vector()).normalized()
        direction=(lamp.location-loc).normalized();half=(direction+view).normalized()
        records.append({'pixel':[x,y],'position':list(loc),'normal':list(n),'half':list(half),
            'normal_tilt_degrees':math.degrees(math.asin(n.z)),'half_angle_error_degrees':math.degrees(n.angle(half)),
            'normal_dot_view':n.dot(view),'normal_dot_light':n.dot(direction)})
control=[]
for i in range(30):
    v=ob.data.vertices[i*128];control.append({'ring':i,'radius':math.hypot(v.co.x,v.co.y),'z':v.co.z})
points=sorted({(round(math.hypot(v.x,v.y),8),round(v.z,8)) for v in vertices if abs(v.x)<1e-5 and v.y<0 and v.z<1.4},key=lambda q:q[1])
mat=ob.data.materials[0];bs=mat.node_tree.nodes['Principled BSDF'];inputs={}
for key in ['Base Color','Roughness','Metallic','IOR','Specular IOR Level','Coat Weight','Coat Roughness','Coat IOR','Normal','Coat Normal']:
    if key not in bs.inputs:continue
    socket=bs.inputs[key];value=socket.default_value
    try:value=list(value)
    except TypeError:pass
    inputs[key]={'value':value,'links':[[l.from_node.name,l.from_socket.name] for l in socket.links]}
report={'source':a.source,'source_sha256':digest,'source_unchanged':True,'camera_elevation_degrees':54,
 'base_light':{'position':list(lamp.location),'energy':lamp.data.energy,'color':list(lamp.data.color),'shape':lamp.data.shape,'size':lamp.data.size,'size_y':lamp.data.size_y},
 'controls':control,'evaluated_meridian':points,'samples':records,'material_inputs':inputs,
 'modifiers':[{'name':m.name,'type':m.type,'levels':getattr(m,'levels',None),'render_levels':getattr(m,'render_levels',None)} for m in ob.modifiers],
 'note':'Geometric corner normals only, not shader bump or full reflection transport. No scene changes or render.'}
ev.to_mesh_clear();assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'base-surface.json').write_text(json.dumps(report,indent=2)+'\n')
for x in [570,584]:
    rows=[r for r in records if r['pixel'][0]==x];best=min(rows,key=lambda r:r['half_angle_error_degrees'])
    print('BASE_NORMAL_BEST',json.dumps(best),flush=True)
print('BASE_CURVATURE_INSPECTED',flush=True)
