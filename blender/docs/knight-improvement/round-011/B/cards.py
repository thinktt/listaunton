"""Align the existing physical eye and cheek softboxes to the newly cut surfaces."""
from pathlib import Path
import sys,json
import bpy,numpy as np
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D))
from carve import load,sculpt,DESIGNS,border,configure_render,render
from probe_carving import point_probe

def rays(s,name,points,probe):
    view=np.asarray(s.camera.matrix_world.to_quaternion()@Vector((0,0,1)))
    ob=s.objects['Knight | '+name].evaluated_get(bpy.context.evaluated_depsgraph_get())
    m=np.asarray(ob.matrix_world);me=ob.to_mesh();me.calc_loop_triangles()
    co=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',co.ravel())
    co=co@m[:3,:3].T+m[:3,3]
    tris=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('vertices',tris.ravel())
    normals=np.array([[list(me.corner_normals[j].vector) for j in t.loops] for t in me.loop_triangles])
    bvh=BVHTree.FromPolygons(co.tolist(),tris.tolist(),all_triangles=True);ob.to_mesh_clear()
    out=[]
    for x,y in points:
        h=probe(x+.5,y+.5)
        if not h or h[1]!=ob.name:continue
        p=np.asarray(h[2]);_,_,i,_=bvh.find_nearest(Vector(p))
        a,b,c=co[tris[i]];u,v=np.linalg.lstsq(np.column_stack((b-a,c-a)),p-a,rcond=None)[0]
        n=np.array([1-u-v,u,v])@normals[i]@np.linalg.inv(m[:3,:3]);n/=np.linalg.norm(n)
        dr=2*n.dot(view)*n-view
        out.append([x,y,p.tolist(),dr.tolist()])
    return out
def locate(s,light,points,offset,dist,axes,energy):
    pts=np.array([q[2] for q in points]);dirs=np.array([q[3] for q in points])
    n=np.median(dirs,axis=0);n/=np.linalg.norm(n);mid=pts.mean(0)+dist*n
    k=((mid-pts)@n)/(dirs@n);plane=pts+dirs*k[:,None]
    center=np.median(plane,axis=0)
    if len(pts)>2:
        _,_,basis=np.linalg.svd(plane-center);long=basis[0]-basis[0].dot(n)*n
    else:long=np.cross(n,[0,0,1.])
    long/=np.linalg.norm(long);short=np.cross(n,long)
    ob=s.objects[light];ob.location=Vector(center+offset[0]*long+offset[1]*short)
    ob.rotation_euler=Matrix(np.column_stack((long,short,n))).to_euler()
    ob.data.shape='ELLIPSE';ob.data.size,ob.data.size_y=axes;ob.data.energy=energy
    ob.data.spread=np.radians(48.)
    bpy.context.view_layer.update()
    return {'name':light,'location':list(ob.location),'rotation':list(ob.rotation_euler),
            'watts':energy,'axes':axes,'samples':[[q[0],q[1]] for q in points]}
UPPER=[(493,471),(497,473),(500,474),(503,476),(506,477),(509,479),(512,480),(515,480)]
LOWER=[(495,496),(499,497),(503,498),(507,499),(511,500),(515,501),(519,501),(523,501)]
INNER=[(497,484),(501,485),(505,487),(509,488),(512,489),(516,489),(520,489),(524,490)]
def measured(scene):
    p=point_probe(scene)
    return {'upper':rays(scene,'near eye',UPPER,p),'inner':rays(scene,'near eye',INNER,p),
            'lower':rays(scene,'continuous horse head and neck',LOWER,p)}
SETUPS=[
    ([1,2,3,4,5],(.31,.17),.42,[2,3,4,5],(.31,.20),.100),
    ([2,3,4,5,6],(.40,.24),.72,[3,4,5,6],(.37,.24),.155),
    ([0,1,2,3,4],(.39,.25),.63,[1,2,3,4,5],(.38,.24),.17),
    ([1,2,3,4,5,6],(.47,.31),.85,[2,3,4,5],(.46,.28),.20),
    ([4,5,6],(.29,.18),.47,[2,3,4],(.37,.24),.13),
    ([3,4,5,6],(.45,.23),.135,[2,3,4,5],(.36,.23),.17),
    ([4,5,6,7],(.39,.19),.105,[2,3,4,5],(.38,.22),.21),
    ([2,3,4,5,6,7],(.52,.26),.18,[3,4,5,6],(.40,.21),.23),
    ([3,4,5,6,7],(.33,.19),.09,[1,2,3,4],(.33,.20),.14),
    ([2,3,4,5,6],(.41,.205),.139,[1,2,3,4,5],(.177,.110),.047),
    ([3,4,5,6],(.43,.19),.131,[1,2,3,4],(.190,.122),.053),
    ([3,4,5,6,7],(.40,.23),.147,[0,1,2,3,4,5],(.191,.099),.045)]
def apply(s,data,i):
    use,axes,e,low,la,le=SETUPS[i]
    setup=[locate(s,'Eye reflection upper',[data['upper'][j] for j in use if j<len(data['upper'])],(0.,0.),.66,axes,e),
           locate(s,'Eye reflection lower',[data['lower'][j] for j in low if j<len(data['lower'])],(0.,0.),.395 if i>=9 else .77,la,le)]
    if i>=5:
        # The close eye and cheek surfaces receive the same bounced light.
        # This is a real area emitter. Each part responds to its own normal.
        lower=s.objects['Eye reflection lower'];prior=lower.light_linking.receiver_collection
        coll=bpy.data.collections.get('Paired eyes and orbital cheek')
        if not coll:
            coll=bpy.data.collections.new('Paired eyes and orbital cheek')
            orig=list(prior.objects) if prior else [s.objects['Knight | continuous horse head and neck']]
            for o in orig+[s.objects['Knight | near eye'],s.objects['Knight | far eye']]:
                if o.name not in coll.objects:coll.objects.link(o)
        lower.light_linking.receiver_collection=coll;lower.data.spread=np.radians(17)
        setup[1].update({'receivers':list(coll.objects.keys()),'spread_degrees':17})
    if i>=9:
        lower=s.objects['Eye reflection lower'];lower.data.spread=np.radians(15.)
        for name in ['Eye reflection upper','Eye reflection lower']:
            s.objects[name].data.color=(1.,.91,.81)
        setup[1]['spread_degrees']=15
    return setup
def study():
    i=int(sys.argv[sys.argv.index('--')+1]);s=load('parent.blend');sculpt(s,DESIGNS[i])
    d=measured(s);(D/f'card-rays-{i}.json').write_text(json.dumps(d,indent=2)+'\n')
    configure_render(s,84);border(s,(448,444,565,524))
    for k in (range(9,len(SETUPS)) if i>=11 else (range(5,9) if i>=8 else range(5))):
        apply(s,d,k);render(s,D/f'card-{i}-{k}-fixed.png')
if __name__=='__main__':study()
