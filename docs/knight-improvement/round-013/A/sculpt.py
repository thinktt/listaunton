"""A bilateral supraorbital fold, lower palpebral plane and seated ocular surface."""
from pathlib import Path
import sys,json,hashlib
import bpy,bmesh,numpy as np
D=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path[:0]=[str(D),str(D.parents[2]/'scripts/knight')]
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import world_vertices,configure_render,save_model,json_file,sha
PARENT='739bf4c1e3671770de868593ec10135c5345417bd80c043ee04ee7dea86efe4c'
ATLAS='1e35b27f1eea257ee9bacc6ae60aa26cbeaf80fad5139365d58be1db395dd78b'
A=np.array([1.,-.76])/np.hypot(1,.76);N=np.array([-A[1],A[0]]);C=np.array([.412,4.158])
def chart(p):
    q=p[:,[0,2]]-C;return q@A,q@N
def ease(x):
    t=np.clip(x,0,1);return t*t*(3-2*t)
def bell(x,w):return np.exp(-(x/w)**2)
def hermite(x,curve):
    z,c=np.array(curve).T;g=np.diff(c)/np.diff(z);m=np.zeros_like(c);use=g[1:]*g[:-1]>0
    m[1:-1][use]=2/(1/g[1:][use]+1/g[:-1][use])
    j=(np.searchsorted(z,x,side='right')-1).clip(0,len(z)-2);h=z[j+1]-z[j];t=np.clip((x-z[j])/h,0,1)
    return ((2*t**3-3*t*t+1)*c[j]+(t**3-2*t*t+t)*h*m[j]+(-2*t**3+3*t*t)*c[j+1]+(t**3-t*t)*h*m[j+1])
UPPER=[(-.56,.021),(-.42,.034),(-.30,.045),(-.21,.071),(-.13,.111),(-.055,.132),(.018,.135),(.11,.121),(.20,.101),(.28,.078),(.37,.058),(.48,.045),(.60,.041),(.73,.044)]
LOWER=[(-.29,.040),(-.217,.025),(-.17,-.006),(-.115,-.027),(-.030,-.041),(.050,-.039),(.13,-.028),(.20,-.008),(.27,.023),(.32,.053),(.385,.059)]
def upper(u):return hermite(u,UPPER)+.024*bell(u+.035,.155)
def lower(u):return hermite(u,LOWER)-.012*bell(u-.198,.131)
def basis(u,v):return np.stack([np.ones_like(u),u,v,u*u,u*v,v*v,u**3,u*u*v,u*v*v,v**3],axis=-1)
def baseline():
    dat=np.load(D/'parent-sections.npz');u,v=np.meshgrid(dat['u'],dat['v']);B=basis(u,v)
    # Fit the undisturbed horse flank beyond the cavity. The broad forehead
    # plane and the hanging cheek jointly constrain the smooth socket bed.
    outside=(u<-.34)|(u>.34)|(v<-.145)|(v>.224)
    window=(u>-.48)&(u<.68)&(v>-.245)&(v<.29)
    coeff={}
    for name in ['near','far']:
        h=dat[name+'_head'];sel=outside&window&np.isfinite(h);x=B[sel];y=h[sel];w=np.ones(len(y))
        for _ in range(5):
            c=np.linalg.lstsq(x*w[:,None],y*w,rcond=None)[0];w=1/(1+((y-x@c)/.026)**2)**.5
        coeff[name]=c
    return coeff
def skin_profile(u,v):
    hi=upper(u);lo=lower(u)
    length=ease((u+.49)/.15)*ease((.655-u)/.16)
    eye=ease((u+.256)/.060)*ease((.342-u)/.087)
    upper_roll=.018-.008*ease((u-.15)/.26)
    # The broad brow fills the gap below the swept ear. Its upper bank is a
    # gently convex plane, and the lower edge rolls under into the socket.
    t=v-hi
    brow=length*(upper_roll*bell(t-.036,.072)+.006*bell(t-.111,.125))
    carve=-eye*.055*ease((.015-t)/.056)*ease((v-lo+.028)/.064)
    crease=-length*(.006+.008*ease((u-.12)/.16))*bell(t+.004,.034)
    crease-=.011*bell(u+.050,.16)*bell(t+.015,.035)
    crease*=1-.65*ease((u-.27)/.23)
    # Past the front corner this progressively more delicate crease becomes
    # the natural division between the nasal ridge and the cheek below it.
    nose=ease((u-.195)/.106)*ease((.585-u)/.195)
    nasal=.009*nose*bell(t-.049,.085)-.012*nose*bell(t+.012,.052)
    cheek=ease((u+.246)/.12)*ease((.318-u)/.14)
    lower_face=cheek*(.015*bell(v-lo+.067,.089)-.004*bell(v-lo+.008,.046))
    return brow+carve+crease+nasal+lower_face
def warp(u,v):
    # Lengthen the nasal corner and let the upper half rise under the brow.
    end=ease((u-.005)/.285)
    du=.051*end*ease((.45-u)/.13)*bell(v-.025,.135)
    dv=.029*ease((v+.025)/.115)*ease((u+.26)/.10)*ease((.36-u)/.11)
    dv+=.018*end*bell(v-.022,.16)
    dv+=.032*ease((v+.032)/.091)*bell(u+.045,.164)-.012*ease((u-.135)/.16)*bell(v-.006,.13)
    return u+du,v+dv
def support(obj,pose):
    rest=rest_coords(world_vertices(obj),pose);u,v=chart(rest)
    zone=(u>-.39)&(u<.69)&(v>-.13)&(v<.29)&(abs(rest[:,1])>.17)
    bm=bmesh.new();bm.from_mesh(obj.data)
    edges=[e for e in bm.edges if all(zone[v.index] for v in e.verts)]
    bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True,smooth=0)
    bm.to_mesh(obj.data);bm.free();obj.data.update()
def grain_at_vertices(obj):
    grain=np.load(D/'grain-response.npy',mmap_mode='r');h,w=grain.shape
    uv=np.empty((len(obj.data.loops),2),np.float32);vi=np.empty(len(uv),np.int32)
    obj.data.uv_layers['Knight wood atlas'].data.foreach_get('uv',uv.ravel());obj.data.loops.foreach_get('vertex_index',vi)
    x=np.clip(uv[:,0]*w-.5,0,w-1.01);y=np.clip((1-uv[:,1])*h-.5,0,h-1.01)
    i=x.astype(int);j=y.astype(int);hx=x-i;hy=y-j
    z=((1-hx)*(1-hy)*grain[j,i]+hx*(1-hy)*grain[j,i+1]+(1-hx)*hy*grain[j+1,i]+hx*hy*grain[j+1,i+1])/65
    return np.bincount(vi,weights=z,minlength=len(obj.data.vertices))/np.maximum(1,np.bincount(vi,minlength=len(obj.data.vertices)))
def apply(obj,pose,coeff,insert):
    old=rest_coords(world_vertices(obj),pose);new=old.copy();U,V=chart(old)
    attr=obj.data.attributes.get('Knight varnish coverage');coverage=None
    if attr:
        coverage=np.empty(len(old),np.float32);attr.data.foreach_get('value',coverage.ravel())
    grain=grain_at_vertices(obj) if attr else np.zeros(len(old))
    for label,sign in [('near',-1),('far',1)]:
        ids=np.flatnonzero((sign*old[:,1]>.095)&(U>-.59)&(U<.71)&(V>-.28)&(V<.37))
        if not len(ids):continue
        x,y=U[ids],V[ids];depth=abs(old[ids,1]);cf=coeff[label]
        gate=ease((depth-.11)/.115)
        active=ease((x+.55)/.19)*ease((.70-x)/.16)*ease((y+.254)/.090)*(1-ease((y-.235)/.110))
        if insert:
            u,v=warp(x,y);xy=C+u[:,None]*A+v[:,None]*N;new[ids,0]=xy[:,0];new[ids,2]=xy[:,1]
            inherited=depth-basis(x,y)@cf
            # A shallower enclosed globe retains the substrate's carved
            # inner crescent and fine walnut relief, including beneath lids.
            core=bell(u+.035,.138)*bell(v-.028,.081)
            replacement=basis(u,v)@cf+(.56+.32*core)*inherited-.009+.0075*core
            new[ids,1]=sign*(depth+gate*(replacement-depth))
            if coverage is not None:coverage[ids]*=1-gate*(.31-.095*grain[ids])
        else:
            target=basis(x,y)@cf+skin_profile(x,y)
            hi=upper(x);lo=lower(x)
            f=active*gate*(1-ease((y-hi-.036)/.112))
            f*=1-(1-ease((x+.20)/.125))*ease((y-.042)/.046)
            f*=1-.52*ease((x-.33)/.23)
            floor=ease((hi-y+.024)/.048)*ease((y-lo+.055)/.060)*ease((.32-abs(x))/.085)
            limit=.042+.060*floor+.025*bell(x-.284,.086)*bell(y-hi+.015,.089)
            delta=target-depth
            delta=np.where(delta>0,limit*np.tanh(delta/limit),.078*np.tanh(delta/.078))
            malar=bell(x-.005,.208)*bell(y-lo+.065,.069)
            new[ids,1]=sign*(depth+f*(delta+.00105*grain[ids]*malar))
            if coverage is not None:
                # Wax follows the worked lid and cheek surfaces.
                satin=.067+.092*bell(x+.010,.16)*bell(y-hi-.037,.056)
                satin+=.270*malar*(1+.64*grain[ids])
                coverage[ids]+=f*(satin-coverage[ids])
    if coverage is not None:attr.data.foreach_set('value',coverage.clip(0,1))
    shift=posed(new,*pose)-posed(old,*pose);m=np.array(obj.matrix_world)
    p=np.empty((len(old),3),np.float32);obj.data.vertices.foreach_get('co',p.ravel())
    p+=shift@np.linalg.inv(m[:3,:3]).T;obj.data.vertices.foreach_set('co',p.ravel());obj.data.update()
    dist=np.linalg.norm(new-old,axis=1)
    return {'vertices':len(old),'changed_gt_1e-6':int((dist>1e-6).sum()),'maximum_shift':float(dist.max())}
def soften_corner(obj,pose):
    """Fair the small plane running from the lower corner into the bridge."""
    from survey import tree
    old=rest_coords(world_vertices(obj),pose);out=old.copy();u,v=chart(old)
    geom=tree(obj,pose);xs=np.linspace(.115,.455,69);ys=np.linspace(-.145,.185,67)
    X,Y=np.meshgrid(xs,ys);xz=C+X[...,None]*A+Y[...,None]*N
    attr=obj.data.attributes.get('Knight varnish coverage')
    finish=np.empty(len(old),np.float32) if attr else None
    if attr:attr.data.foreach_get('value',finish)
    def smooth(vals,axis,sd):
        rad=round(3.1*sd);t=np.arange(-rad,rad+1);w=np.exp(-.5*(t/sd)**2);w/=w.sum()
        return np.apply_along_axis(lambda a:np.convolve(np.pad(a,(rad,rad),mode='edge'),w,'valid'),axis,vals)
    for sign in [-1,1]:
        field=np.array([sign*geom.ray_cast((x,2*sign,z),(0,-sign,0))[0].y for x,z in xz.reshape(-1,2)]).reshape(X.shape)
        delta=smooth(smooth(field,0,5.7),1,7.5)-field
        ids=np.flatnonzero((sign*old[:,1]>.23)&(u>xs[0])&(u<xs[-1])&(v>ys[0])&(v<ys[-1]))
        x=(u[ids]-xs[0])/.005;y=(v[ids]-ys[0])/.005;i=x.astype(int);j=y.astype(int);h=x-i;k=y-j
        dy=(1-h)*(1-k)*delta[j,i]+h*(1-k)*delta[j,i+1]+(1-h)*k*delta[j+1,i]+h*k*delta[j+1,i+1]
        # Only the nasal turn receives this fairing. The upper lid and its
        # central crescent keep their deliberate cross section.
        w=bell(u[ids]-.28,.070)*bell(v[ids]-.018-.30*(u[ids]-.28),.062)
        w*=ease((upper(u[ids])-v[ids]+.002)/.038)*ease((sign*old[ids,1]-.23)/.055)
        out[ids,1]+=sign*w*dy
        if attr:finish[ids]+=w*(.020-finish[ids])
    offset=posed(out,*pose)-posed(old,*pose);m=np.array(obj.matrix_world)
    p=np.empty((len(old),3),np.float32);obj.data.vertices.foreach_get('co',p.ravel())
    p+=offset@np.linalg.inv(m[:3,:3]).T;obj.data.vertices.foreach_set('co',p.ravel())
    if attr:attr.data.foreach_set('value',finish)
    obj.data.update()
    return float(np.linalg.norm(out-old,axis=1).max())
def main():
    assert sha(D/'parent.blend')==PARENT and sha(D/'pigment.png')==ATLAS
    bpy.ops.wm.open_mainfile(filepath=str(D/'parent.blend'),load_ui=False);s=bpy.context.scene
    q=json.loads(s['knight_mission_pose']);pose=[q[k] for k in ('dx','dy','twist_degrees')];c=baseline()
    info={'parent_sha256':PARENT,'pose':pose,'packed_atlas_sha256':ATLAS,'upper':UPPER,'lower':LOWER,'source_fit':{k:v.tolist() for k,v in c.items()},'geometry':{}}
    for name in ['continuous horse head and neck','coherent skull cheek and conical muzzle','near eye','far eye']:
        obj=s.objects['Knight | '+name]
        if name=='continuous horse head and neck':support(obj,pose)
        info['geometry'][name]=apply(obj,pose,c,name.endswith('eye'))
    bpy.context.view_layer.update()
    info['nasal_fairing_max']=soften_corner(s.objects['Knight | continuous horse head and neck'],pose)
    from topology import repair
    info['transition_quads_split']=len(repair(s.objects['Knight | continuous horse head and neck']))
    bpy.context.view_layer.update()
    sys.path.insert(0,str(D));from lamps import configure
    info['physical_eye_lamps']=configure(s)
    s['knight_improvement_013_A']=json.dumps(info)
    configure_render(s,144);save_model(s,D/'knight.blend')
    info['model_sha256']=sha(D/'knight.blend');json_file(D/'parameters.json',info);print('MODEL',info['model_sha256'],info['geometry'])
if __name__=='__main__':main()
