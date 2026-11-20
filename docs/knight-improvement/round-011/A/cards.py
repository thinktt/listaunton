"""Measure actual surface normals and set two world-space elliptical studio cards."""
from pathlib import Path
import sys,json,math
import bpy,numpy as np
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from mission_scene import configure_render,render
from probe_carving import point_probe
def evaluator(obj,graph):
    ev=obj.evaluated_get(graph);me=ev.to_mesh();me.calc_loop_triangles()
    m=np.asarray(obj.matrix_world);pos=np.array([list(v.co) for v in me.vertices])@m[:3,:3].T+m[:3,3]
    tri=np.array([list(t.vertices) for t in me.loop_triangles]);loops=np.array([list(t.loops) for t in me.loop_triangles])
    norms=np.empty((len(me.corner_normals),3),np.float32);me.corner_normals.foreach_get('vector',norms.ravel())
    norms=norms@np.linalg.inv(m[:3,:3]);tree=BVHTree.FromPolygons(pos.tolist(),tri.tolist(),all_triangles=True)
    ev.to_mesh_clear()
    def at(point):
        _,_,idx,_=tree.find_nearest(Vector(point));a,b,c=pos[tri[idx]]
        u,v=np.linalg.lstsq(np.column_stack((b-a,c-a)),point-a,rcond=None)[0]
        n=np.array([1-u-v,u,v])@norms[loops[idx]];return n/np.linalg.norm(n)
    return at
def measure(scene):
    graph=bpy.context.evaluated_depsgraph_get();probe=point_probe(scene);normal={}
    cam=np.array(scene.camera.matrix_world.to_quaternion()@Vector((0,0,1)))
    def aim(name,xy):
        obj=scene.objects['Knight | '+name];key=obj.name
        if key not in normal:normal[key]=evaluator(obj,graph)
        x,y=xy;options=[]
        for ox in range(-3,4):
            for oy in range(-3,4):
                hit=probe(x+ox+.5,y+oy+.5)
                if hit and hit[1]==key:options.append((ox*ox+oy*oy,x+ox,y+oy,hit))
        if not options:raise RuntimeError((name,xy))
        _,x,y,hit=min(options,key=lambda a:a[0]);p=np.array(hit[2]);n=normal[key](p)
        return [x,y],p,2*n.dot(cam)*n-cam
    return aim
def set_card(scene,guide,lamp_name,part,xy,dist,axes,energy,angle):
    # Directions are frozen in object space by the saved emitter transforms.
    # The card therefore stays still when the piece is viewed from another angle.
    xy,p,n=guide(part,xy);n/=np.linalg.norm(n)
    ob=scene.objects[lamp_name];at=p+dist*n
    axis=np.array([0.,0.,1.]);h=np.cross(axis,n);h/=np.linalg.norm(h);v=np.cross(n,h)
    ob.location=Vector(at);ob.rotation_euler=Matrix(np.column_stack([h,v,n])).to_euler()
    ob.data.shape='ELLIPSE';ob.data.size,ob.data.size_y=axes;ob.data.energy=energy;ob.data.spread=np.radians(angle)
    bpy.context.view_layer.update()
    return {'lamp':lamp_name,'point_on_surface':xy,'location':list(ob.location),'rotation':list(ob.rotation_euler),'axes':axes,'watts':energy,'spread_degrees':angle}
def configure(scene,upper=None,lower=None):
    guide=measure(scene);out=[]
    if upper:out.append(set_card(scene,guide,'Eye reflection upper','near eye',*upper))
    if lower:out.append(set_card(scene,guide,'Eye reflection lower','continuous horse head and neck',*lower))
    return out
if __name__=='__main__':
    bpy.ops.wm.open_mainfile(filepath=str(D/'knight.blend'),load_ui=False);s=bpy.context.scene;guide=measure(s)
    table={}
    for part,probes in [('near eye',[(497,467),(498,468),(501,470),(500,473),(502,474),(504,476),(506,480)]),
                        ('continuous horse head and neck',[(490,497),(495,499),(500,500),(504,500),(509,500),(515,501)])]:
        table[part]=[(a,xyz.tolist(),vec.tolist()) for a,xyz,vec in (guide(part,xy) for xy in probes)]
    (D/'card-survey.json').write_text(json.dumps(table,indent=2)+'\n')
    configure_render(s,72);s.render.use_border=s.render.use_crop_to_border=True
    s.render.border_min_x=449.01/1254;s.render.border_max_x=555.01/1254
    s.render.border_min_y=(1254-515+.01)/1254;s.render.border_max_y=(1254-447+.01)/1254
    render(s,D/'card-parent.png')
    for label,upper,lower in [
        ('lower',None,((499,500),.64,(.24,.17),.055,16)),
        ('upper',((498,468),.62,(.075,.062),.032,20),((499,500),.64,(.24,.17),.055,16)),
        ('broad',((499,470),.64,(.136,.105),.049,23),((502,499),.58,(.18,.14),.056,18)),
        ('small',((502,473),.62,(.076,.060),.038,18),((499,499),.63,(.25,.22),.064,16))]:
        if upper:set_card(s,guide,'Eye reflection upper','near eye',*upper)
        if lower:set_card(s,guide,'Eye reflection lower','continuous horse head and neck',*lower)
        render(s,D/('card-'+label+'.png'))
