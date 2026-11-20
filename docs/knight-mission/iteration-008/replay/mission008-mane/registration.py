"""Build a physical radial offset and transverse-width fit against the two registered sources."""
import json,sys
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(D))
STATIONS=np.array([0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.])
def smooth(t):
    t=np.clip(t,0.,1.);return t*t*(3-2*t)

def displacements(rest,grid):
    # Rest-space changes, independent of camera once fitted. The two flanks use the same parameters.
    out=np.zeros((2,len(rest),3),np.float32)
    for i,idx in enumerate(grid):
        row=rest[idx];center=row[128];n=center[[0,2]]-row[0,[0,2]];n/=np.linalg.norm(n)
        st=i/4;weight=smooth(st/.85)*smooth((12-st)/.80)
        j=np.abs(np.arange(256)-128);t=weight*(1-smooth((j-53)/34))
        out[0][np.ix_(idx,[0,2])]=t[:,None]*n
        out[1,idx,1]=t*(row[:,1]-center[1])/max(.09,np.max(abs(row[:,1]-center[1])))
    return out

def raw():
    import bpy
    from mathutils import Vector
    from bpy_extras.object_utils import world_to_camera_view
    from geometry import scene,state,world_vertices,posed
    s=scene('knight');ob,p,rest,ch=state(s);grid=ch['grid']
    W=s.render.resolution_x
    def project(pt):
        u=world_to_camera_view(s,s.camera,Vector(pt))
        return np.array([u.x*W,(1-u.y)*W])
    z=project([0.,0.,0.]);M=np.stack([project(a)-z for a in np.eye(3)]);project_array=lambda a:a@M+z
    pos=world_vertices(ob);base=project_array(pos)
    df=displacements(rest,grid)
    # Exact rest-space basis, serialized with canonical pose and native section indices.
    proj=np.array([(posed(rest+.01*f,*p)-posed(rest,*p))@M/.01 for f in df])
    ed=np.array([e.vertices[:] for e in ob.data.edges],int)
    other=[]
    for o in s.objects:
        if o!=ob and o.type=='MESH' and not o.hide_render:
            m=o.data;v=project_array(world_vertices(o));oi=np.array([e.vertices[:] for e in m.edges],int);other.append(v[oi])
    other=np.concatenate(other)
    np.savez(D/'projection.npz',base=base,proj=proj,edges=ed,other=other[(other[:,:,0].min(1)<650)&(other[:,:,1].min(1)<695)&(other[:,:,1].max(1)>275)],grid=grid)

def edge_ext(edges,levels,axis,trim):
    # Returns the minimum x at each y, or minimum y at each x.
    u=edges[:,:,axis];v=edges[:,:,1-axis];lo=np.min(u,axis=1);hi=np.max(u,axis=1)
    res=[]
    for point in levels:
        take=(lo<=point)&(point<hi)&(v.min(1)<trim)
        uv=u[take];vv=v[take];w=(point-uv[:,0])/(uv[:,1]-uv[:,0])
        res.append(np.min(vv[:,0]+w*(vv[:,1]-vv[:,0]),initial=9999))
    return np.array(res)

def fit():
    from evidence import refs,mask
    a=np.load(D/'projection.npz');xy=a['base'];pr=a['proj'];edges=a['edges'];other=a['other'];grid=a['grid']
    yy=np.arange(307.5,665,5.);xx=np.arange(278.5,471,7.)
    # Include the leading edge under the ear; stop before the interior of the head owns the outline.
    other_x=edge_ext(other,yy,1,355);other_y=edge_ext(other,xx,0,385)
    # Dynamic probe list limits edge calculations to the rim neighbourhood once.
    fixed=[]
    for levs,axis,oth in [(yy,1,other_x),(xx,0,other_y)]:
        pts=xy[edges];u=pts[:,:,axis];v=pts[:,:,1-axis];lo=u.min(1);hi=u.max(1);l=v.min(1);h=v.max(1)
        orig=edge_ext(pts,levs,axis,600)
        fixed.append([edges[(lo<=k+17)&(hi>=k-17)&(l<g+28)&(h>g-28)] for k,g in zip(levs,orig)])
    # Each section interpolates between adjacent shape controls along the growth direction.
    station=np.zeros(len(xy));station[grid.ravel()]=np.repeat(np.arange(49)/4,256)
    def outline(params):
        dx=np.interp(station,STATIONS,params[:13]);dy=np.interp(station,STATIONS,params[13:])
        moved=xy+pr[0]*dx[:,None]+pr[1]*dy[:,None];res=[]
        for fi,(levs,axis,other_opt) in enumerate([(yy,1,other_x),(xx,0,other_y)]):
            for lev,eds,bound in zip(levs,fixed[fi],other_opt):
                pt=moved[eds];u=pt[:,:,axis];vr=pt[:,:,1-axis];t=(u[:,0]<=lev)^(u[:,1]<=lev);u=u[t];vr=vr[t];mix=(lev-u[:,0])/(u[:,1]-u[:,0])
                res.append(np.min(vr[:,0]+mix*(vr[:,1]-vr[:,0]),initial=bound))
        return np.array(res)
    goal=[]
    for k in ['original','Black 2']:
        m=mask(refs()[k],True)
        goal.append(np.r_[m[np.floor(yy).astype(int)].argmax(1),m[:,np.floor(xx).astype(int)].argmax(0)])
    goal=.65*goal[0]+.35*goal[1];n=26;x=np.zeros(n);initial=outline(x);cur=x.copy()
    # Solve smooth regional radial and width corrections. Stronger transverse penalty keeps broad physical facets.
    rr=np.eye(n);dd=np.diff(np.eye(13),n=2,axis=0);der=np.zeros((22,n));der[:11,:13]=dd;der[11:,13:]=dd
    A=np.vstack((rr*np.r_[np.full(13,55),np.full(13,82)],der*131))
    for _ in range(7):
        now=outline(x);jac=np.stack([(outline(x+.0007*v)-now)/.0007 for v in rr],axis=1)
        step=np.linalg.lstsq(np.vstack((jac,A)),np.r_[goal-now,-A@x],rcond=1.e-5)[0]
        x=np.clip(x+.67*step,-.125,.065)
    end=outline(x)
    (D/'registration-fit.json').write_text(json.dumps({'radial':x[:13].tolist(),'width':x[13:].tolist(),'projected_mae_before':float(np.mean(abs(initial-goal))),'projected_mae_after':float(np.mean(abs(end-goal))),'target':goal.tolist(),'initial':initial.tolist(),'final':end.tolist(),'source_rows':yy.tolist(),'source_columns':xx.tolist()},indent=2))
    print(np.mean(abs(initial-goal)),np.mean(abs(end-goal)),x,flush=True)

if __name__=='__main__':
    raw() if sys.argv[-1]=='raw' else fit()
