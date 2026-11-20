"""Carve the bilateral upper orbital fold, lower ear seat and recessed eye into a single sweep."""
from pathlib import Path
import sys,json,hashlib
import bpy,numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path[:0]=[str(D),str(R/'scripts/knight')]
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import world_vertices,configure_render,save_model,sha
AX=np.array([1.,-.76])/np.hypot(1,.76);UP=np.array([-AX[1],AX[0]]);C=np.array([.412,4.158])
PARENT='c404e26928309df6233e2e7b3595d5d10025632a18e61e635294eb08b411f33e'
ATLAS='f6e6b26fad1baf22bbf7dd0eb0427cb61b9064245af6acbd268d31068502f4c8'
def chart(xyz):
    q=xyz[:,[0,2]]-C;return q@AX,q@UP
def ease(x):
    t=np.clip(x,0,1);return t*t*(3-2*t)
def g(x,w):return np.exp(-(x/w)**2)
def smooth(field,vert,along):
    out=field.copy()
    for dim,scale in [(1,along),(0,vert)]:
        sz=round(scale*3);offs=np.arange(-sz,sz+1);w=np.exp(-.5*(offs/scale)**2);w/=w.sum()
        out=np.apply_along_axis(lambda a:np.convolve(np.pad(a,(sz,sz),mode='edge'),w,'valid'),dim,out)
    return out
def fill(field):
    out=field.copy()
    for row in out:
        ix=np.flatnonzero(np.isfinite(row))
        if len(ix):row[:]=np.interp(np.arange(len(row)),ix,row[ix])
    for col in out.T:
        ix=np.flatnonzero(np.isfinite(col));col[:]=np.interp(np.arange(len(col)),ix,col[ix])
    return out
def shell_interior(field):
    valid=np.isfinite(field)
    remaining=valid.copy();distance=np.zeros(valid.shape,float)
    for _ in range(24):
        remaining=remaining&np.roll(remaining,1,0)&np.roll(remaining,-1,0)&np.roll(remaining,1,1)&np.roll(remaining,-1,1)
        distance+=remaining*.005
    return ease((distance-.019)/.052)
def herm(x,pts):
    a,b=np.array(pts,float).T
    sec=np.diff(b)/np.diff(a);m=np.zeros(len(a));use=sec[:-1]*sec[1:]>0
    m[1:-1][use]=2/(1/sec[1:][use]+1/sec[:-1][use]);j=(np.searchsorted(a,x)-1).clip(0,len(a)-2)
    h=a[j+1]-a[j];t=((x-a[j])/h).clip(0,1)
    return (2*t**3-3*t**2+1)*b[j]+(t**3-2*t**2+t)*h*m[j]+(-2*t**3+3*t**2)*b[j+1]+(t**3-t**2)*h*m[j+1]
MARGIN=[(-.38,.018),(-.29,.029),(-.232,.042),(-.195,.074),(-.14,.112),(-.084,.137),(-.03,.148),(.040,.140),(.116,.119),(.193,.098),(.267,.073),(.334,.063),(.42,.056),(.52,.051)]
def probe(field,x,y,dat):
    xx=np.clip((x-dat['u'][0])/.005,0,len(dat['u'])-1.01);yy=np.clip((y-dat['v'][0])/.005,0,len(dat['v'])-1.01)
    i=xx.astype(int);j=yy.astype(int);h=xx-i;k=yy-j
    return (1-h)*(1-k)*field[j,i]+h*(1-k)*field[j,i+1]+(1-h)*k*field[j+1,i]+h*k*field[j+1,i+1]
def write(ob,old,new,pose):
    delta=posed(new,*pose)-posed(old,*pose)
    xyz=np.empty((len(new),3),np.float32);ob.data.vertices.foreach_get('co',xyz.ravel());xyz+=delta@np.linalg.inv(np.array(ob.matrix_world)[:3,:3]).T
    ob.data.vertices.foreach_set('co',xyz.ravel());ob.data.update()
    dist=np.linalg.norm(new-old,axis=1)
    return {'vertices':len(old),'moved':int((dist>1e-6).sum()),'max_shift':round(float(dist.max()),6)}
def fair_temporal_fold(ob,pose):
    from survey import tree
    old=rest_coords(world_vertices(ob),pose);new=old.copy();u,v=chart(old);tr=tree(ob,pose)
    us=np.arange(-.57,-.09,.005);vs=np.arange(-.155,.272,.005)
    X,Y=np.meshgrid(us,vs);pts=(C+X[...,None]*AX+Y[...,None]*UP).reshape(-1,2)
    for sg in [-1,1]:
        height=np.array([sg*tr.ray_cast((x,sg*2,z),(0,-sg,0))[0].y for x,z in pts]).reshape(X.shape)
        change=smooth(height,11.5,15.5)-height
        ids=np.flatnonzero((sg*old[:,1]>.29)&(u>us[0])&(u<us[-1])&(v>vs[0])&(v<vs[-1]))
        x,y=u[ids],v[ids];w=ease((x+.55)/.09)*ease((-.160-x)/.087)*ease((y+.096)/.082)*ease((.25-y)/.083)
        # Fair the inherited temporal pucker into the broad skull; the lip starts as a tapered line above the actual corner.
        new[ids,1]+=sg*.99*w*probe(change,x,y,{'u':us,'v':vs})
    return write(ob,old,new,pose)
def carve(s):
    p=json.loads(s['knight_mission_pose']);pose=[p[k] for k in ['dx','dy','twist_degrees']];dat=np.load(D/'parent-sections.npz')
    out={}
    for name in ['continuous horse head and neck','coherent skull cheek and conical muzzle','near eye','far eye','near swept ear','far swept ear']:
        ob=s.objects['Knight | '+name];old=rest_coords(world_vertices(ob),pose);new=old.copy();u,v=chart(old);depth=abs(old[:,1])
        attr=ob.data.attributes.get('Knight varnish coverage') if name.endswith('eye') else None
        finish=np.empty(len(old),np.float32) if attr else None
        if attr:attr.data.foreach_get('value',finish)
        for side,sg in [('near',-1),('far',1)]:
            ids=np.flatnonzero((sg*old[:,1]>.19)&(u>-.54)&(u<.61)&(v>-.18)&(v<.46))
            if not len(ids):continue
            x=u[ids];y=v[ids];h=depth[ids];gate=ease((h-.19)/.1);line=herm(x,MARGIN);t=y-line
            if name.endswith('ear'):
                bottom=.216+.38*x-.36*x*x
                w=ease((x+.51)/.24)*ease((.42-x)/.12)*ease((.425-y)/.102)*ease((y-bottom+.16)/.12)
                # Round the tucked underside inward. The free blade and its upper ridgeline are completely outside this cut.
                lift=-.006*w;dent=-.069*w
                xy=C+x[:,None]*AX+(y+lift)[:,None]*UP
                new[ids,0]=xy[:,0];new[ids,2]=xy[:,1];new[ids,1]+=sg*dent
            elif name.endswith('eye'):
                # Move the illuminated plane bodily up under the arch; carry both layers together.
                core=g(x+.040,.172)*g(y-.053,.104)
                dv=.038*core;du=-.021*core
                xy=C+(x+du)[:,None]*AX+(y+dv)[:,None]*UP
                new[ids,0]=xy[:,0];new[ids,2]=xy[:,1]
                front=fill(dat[side+'_eye']);relax=smooth(front,3.7,5.8)-front
                polished=.72*probe(relax,x,y,dat)*g(x+.02,.199)*g(y-.068,.112)
                new[ids,1]+=sg*(-.32*dv-.14*du-.007*g(x+.115,.18)*g(y-.065,.125)+polished)
                if attr:finish[ids]+=.095*g(x+.055,.13)*g(y-.066,.082)
            else:
                field=fill(dat[side+'_head']);soft=smooth(field,4.8,7.2)
                # A slightly lower tail, higher center and longer nasal fall define the lid line in the skull.
                move=-.014*g(x+.205,.074)+.013*g(x+.06,.135)+.020*g(x-.202,.128)
                d=probe(soft,x,y-move,dat)-probe(field,x,y,dat)
                w=ease((x+.42)/.16)*ease((.53-x)/.18)*ease((t+.065)/.052)*ease((.146-t)/.066)*gate
                lip=.018*g(t-.021-move,.040)-.011*g(t+.010-move,.027)
                lip*=ease((x+.30)/.12)*ease((.39-x)/.16)*(1-.28*ease((x-.11)/.17))
                # The noseward cross-section broadens and loses its edge as it meets the bridge.
                w*=1-.19*ease((x-.28)/.18)
                seat=.023*ease((x+.46)/.19)*ease((.37-x)/.20)*g(t-.09,.083)
                new[ids,1]+=sg*(w*(.82*d+lip)+gate*seat)
            if not name.endswith('ear'):
                # Lift the outer commissure in the skull and its matching insert together.
                lift=.049*g(x-.155,.155)*g(t+.002,.116)*gate
                new[ids,2]+=lift
            if name.endswith('eye'):
                # The exterior skirt is built from long, narrow triangles.
                # Carry it with a single affine transformation; restrict local relief to the broad inner cap.
                w=probe(shell_interior(dat[side+'_eye']),x,y,dat)[:,None]
                carried=old[ids].copy();carried[:,2]+=.039+.042*x+.047*y
                carried[:,0]+=.003-.019*x;carried[:,1]+=sg*(-.015-.022*x-.030*y)
                new[ids]=carried+w*(new[ids]-carried)
        if attr:attr.data.foreach_set('value',finish.clip(0,1))
        out[name]=write(ob,old,new,pose)
    bpy.context.view_layer.update()
    out['temporal fairing']=fair_temporal_fold(s.objects['Knight | continuous horse head and neck'],pose)
    bpy.context.view_layer.update();return out
def build(draft=False):
    assert sha(D/'parent.blend')==PARENT and sha(D/'pigment.png')==ATLAS
    bpy.ops.wm.open_mainfile(filepath=str(D/'parent.blend'),load_ui=False);s=bpy.context.scene
    parts=carve(s);q=json.loads(s['knight_mission_pose'])
    info={'parent_sha256':PARENT,'packed_atlas_sha256':ATLAS,'pose':[q[k] for k in ['dx','dy','twist_degrees']],'geometry':parts,'upper_margin':MARGIN,'studio':'Accepted parent studio.','recipe':'Bilateral orbital roll, tucked ear undersides, carried double-surface ocular plane.'}
    dest=D/('inspection.blend' if draft else 'knight.blend')
    s['knight_improvement_015_A']=json.dumps(info);configure_render(s,144);save_model(s,dest)
    info['model_sha256']=sha(dest);(D/('inspection.json' if draft else 'parameters.json')).write_text(json.dumps(info,indent=2)+'\n');print(info,flush=True)
if __name__=='__main__':
    if sys.argv[-1]=='trial':
        from pictures import render_trial
        render_trial('trial',carve)
    else:build(sys.argv[-1]=='inspection')
