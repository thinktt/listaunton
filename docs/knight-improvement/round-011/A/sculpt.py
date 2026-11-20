"""Fit a closed ocular surface below continuous paired upper and lower lids."""
from pathlib import Path
import json,sys
import bpy,bmesh,numpy as np
D=Path(__file__).resolve().parent;ROOT=D.parents[2];sys.dont_write_bytecode=True
sys.path[:0]=[str(D),str(ROOT/'scripts/knight')]
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import world_vertices,configure_render,save_model,json_file,sha,use_side_camera,render
from diagnostic_views import pictures,clay_studio
from anatomy import chart,contours,dress,ease,bell,ocular_coordinates
from cards import configure as focus_cards
PARENT='7fe492399fa2738d264e73e9e85c427c1531cb902234d43ce1e5012468488922'
def apply(obj,old,q,pose):
    offset=posed(q,*pose)-posed(old,*pose)
    offset[np.all(old==q,axis=1)]=0
    m=np.asarray(obj.matrix_world)
    v=np.empty((len(q),3),np.float32);obj.data.vertices.foreach_get('co',v.ravel())
    v+=np.float32(offset@np.linalg.inv(m[:3,:3]).T);obj.data.vertices.foreach_set('co',v.ravel());obj.data.update()
    norm=np.linalg.norm(q-old,axis=1)
    return {'moved_vertices_1e-5':int((norm>1e-5).sum()),'max_rest_shift':float(norm.max())}
def refine(mesh):
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=1,use_grid_fill=True,smooth=0)
    bm.to_mesh(mesh);bm.free();mesh.update()
def sphere():
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16)
    obj=bpy.context.object;mesh=obj.data
    fingerprint={tuple(sorted(tuple(e.vertices))) for e in mesh.edges}
    coords=np.array([list(v.co) for v in mesh.vertices])
    bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(mesh)
    return coords,fingerprint
def skin(obj,pose,coef):
    old=rest_coords(world_vertices(obj),pose).astype(float);out=old.copy();u,v=chart(old)
    attr=obj.data.attributes.get('Knight varnish coverage')
    prior=np.array([k.value for k in attr.data]) if attr is not None else None
    for side,c in coef.items():
        use=side*old[:,1]>.105;p=old[use];delta,blend,top,lower=dress(p,c)
        out[use,1]+=side*delta
        if prior is not None:
            a,b=u[use],v[use]
            # A dressed brow, narrow inner lower lid and wider malar surface
            # have distinct polishes in the billet. Corners carry satin wood.
            finish=.045+.27*bell(a+.035,.16)*bell(b-top-.010,.030)
            finish+=.23*bell(a+.005,.125)*bell(b-lower+.012,.033)
            finish+=.28*bell(a-.020,.147)*bell(b-lower+.053,.041)
            prior[use]+=blend*(finish-prior[use])
    if prior is not None:attr.data.foreach_set('value',np.float32(prior))
    return apply(obj,old,out,pose)
def eyes(obj,side,pose,c,unit,edges):
    assert {tuple(sorted(tuple(e.vertices))) for e in obj.data.edges}==edges
    # Carry the angular coordinate through the native UV-preserving split.
    # The order of new BMesh vertices need not agree between opposite eyes.
    angular=obj.data.attributes.new('Orbital source parameter','FLOAT_VECTOR','POINT')
    angular.data.foreach_set('vector',np.asarray(unit,np.float32).ravel())
    refine(obj.data);refine(obj.data)
    angular=obj.data.attributes['Orbital source parameter']
    unit=np.empty((len(angular.data),3),np.float32);angular.data.foreach_get('vector',unit.ravel())
    lengths=np.linalg.norm(unit,axis=1);assert min(lengths)>.94
    unit/=lengths[:,None];obj.data.attributes.remove(angular)
    old=rest_coords(world_vertices(obj),pose).astype(float)
    out=ocular_coordinates(unit,side,c);u,v=chart(out)
    wax=.085+.095*bell(u+.030,.140)*bell(v-.007,.067)
    obj.data.attributes['Knight varnish coverage'].data.foreach_set('value',np.float32(wax))
    return apply(obj,old,out,pose)
def build():
    assert sha(D/'parent.blend')==PARENT
    bpy.ops.wm.open_mainfile(filepath=str(D/'parent.blend'),load_ui=False);s=bpy.context.scene
    p=json.loads(s['knight_mission_pose']);pose=[p[k] for k in ('dx','dy','twist_degrees')]
    ref=json.loads(s['knight_improvement_005_A'])['cheek_polynomial']
    coef={int(k):np.array(v) for k,v in ref.items()}
    unit,edges=sphere();cfg={'parent_sha256':PARENT,'pose':pose,'orbital_fit':ref,'geometry':{}}
    for suffix in ['continuous horse head and neck','coherent skull cheek and conical muzzle']:
        cfg['geometry'][suffix]=skin(s.objects['Knight | '+suffix],pose,coef)
    for suffix,side in [('near eye',-1),('far eye',1)]:
        cfg['geometry'][suffix]=eyes(s.objects['Knight | '+suffix],side,pose,coef[side],unit,edges)
    bpy.context.view_layer.update()
    cfg['cards']=focus_cards(s,upper=((499,470),.68,(.108,.090),.031,21),
                     lower=((501,500),.52,(.40,.25),.084,15))
    s['knight_improvement_011_A']=json.dumps(cfg)
    configure_render(s,144);save_model(s,D/'knight.blend');cfg['model_sha256']=sha(D/'knight.blend')
    json_file(D/'parameters.json',cfg);print('ROUND_11A',cfg['model_sha256'],flush=True)
def preview():
    bpy.ops.wm.open_mainfile(filepath=str(D/'knight.blend'),load_ui=False);s=bpy.context.scene;configure_render(s,80)
    for name,side,clay,box in [('fixed',False,False,(378,407,600,546)),('side',True,False,(491,209,805,449)),('side-clay',False,True,(491,209,805,449))]:
        if side:use_side_camera(s)
        if clay:clay_studio(s,10.3)
        x,y,u,v=box;s.render.use_border=s.render.use_crop_to_border=True
        s.render.border_min_x=(x+.01)/1254;s.render.border_max_x=(u+.01)/1254
        s.render.border_min_y=(1254-v+.01)/1254;s.render.border_max_y=(1254-y+.01)/1254
        render(s,D/('preview-'+name+'.png'))
if __name__=='__main__':
    if '--render-only' not in sys.argv:build()
    if '--preview' in sys.argv:preview()
    elif '--build-only' not in sys.argv:pictures()
