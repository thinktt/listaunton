"""Inspect and sculpt the applied ordered native cross-sections of the mane."""
from pathlib import Path
import bpy,numpy as np,json,sys,hashlib
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
ROOT=D.parents[2]
sys.path[:0]=[str(ROOT/'scripts/knight'),str(D)]
from mission_scene import world_vertices,configure_render,save_model,render,use_side_camera,sha
from lower_carving_fit import rest_coords
from mission_pose import posed
PARENT='1a8c2b2384ac360766d3a3121671199f231df21b2ceea6caee22c9ebdb5e9766'

def scene(name):
    bpy.ops.wm.open_mainfile(filepath=str(D/(name+'.blend')),load_ui=False)
    return bpy.context.scene

def state(s):
    ob=s.objects['Knight | swept rounded mane'];p=json.loads(s['knight_mission_pose'])
    p=[p[k] for k in ('dx','dy','twist_degrees')]
    chart=np.load(D/'ring-chart.npz')
    return ob, p, rest_coords(world_vertices(ob),p),chart

def survey():
    s=scene('parent');obj,p,old,chart=state(s);sec=[]
    for i,ids in enumerate(chart['grid']):
        pts=old[ids];out=pts[128,[0,2]]-pts[0,[0,2]];out/=np.linalg.norm(out)
        pr=(pts[:,[0,2]]-pts[128,[0,2]])@out
        sec.append(dict(station=i/4,center=pts[128].tolist(),inward=pts[0].tolist(),
                        y=pts[:,1].tolist(),r=pr.tolist(),out=out.tolist()))
    (D/'parent-sections.json').write_text(json.dumps(sec))
    np.save(D/'parent-rest.npy',old)
    for k in [0,2,4,8,12,16,20,24,28,32,36,40,44,48]:
        q=sec[k];print(k/4, [round(x,3) for x in q['center']], [tuple(round(q[a][128+j],3) for a in ['y','r']) for j in range(0,129,12)],flush=True)

def ease(t):
    t=np.clip(t,0.,1.)
    return t*t*(3.-2.*t)

def carve(s,registered):
    ob,pose,old,chart=state(s)
    new=old.copy();details=[]
    for i,idx in enumerate(chart['grid']):
        st=i/4;row=old[idx].copy();changed=row.copy()
        center=row[128].copy()
        direction=center[[0,2]]-row[0,[0,2]];direction/=np.linalg.norm(direction)
        weight=.98*ease(st/.85)*ease((12.-st)/.95)
        width_fraction=np.interp(st,[0,2,4.5,6,7.5,9.5,11,12],[.68,.64,.65,.67,.67,.62,.63,.59])
        transverse=[]
        for side in [-1,1]:
            j=np.arange(129);ids=(128+side*j)%256;half=row[ids]
            sign=np.sign(half[40,1]-center[1])
            y=(half[:,1]-center[1])*sign
            rad=(half[:,[0,2]]-center[[0,2]])@direction
            B=np.array([y[73],rad[73]])
            width=width_fraction*np.max(y)
            A=np.array([width,-.045*width])
            along=(B-A)/np.linalg.norm(B-A)
            before=.026+width*.018;after=.033+width*.018
            a=np.array([width-before,-.045*(width-before)**2/width])
            b=A+after*along
            # Position along the actual arc, keeping texture parameterization close to the accepted surface.
            arc=np.r_[0,np.cumsum(np.hypot(np.diff(y),np.diff(rad)))]
            corner=int(np.clip(np.searchsorted(arc[0:59],width),20,50));lo=corner-4;hi=corner+4
            dst=np.stack([y,rad],axis=1)
            t=arc[:lo+1]/arc[lo]
            dst[:lo+1,0]=a[0]*t
            dst[:lo+1,1]=-.045*dst[:lo+1,0]**2/width
            t=np.linspace(0,1,hi-lo+1)[:,None]
            dst[lo:hi+1]=(1-t)**2*a+2*t*(1-t)*A+t*t*b
            t=(arc[hi:74]-arc[hi])/(arc[73]-arc[hi])
            dst[hi:74]=b[None,:]+t[:,None]*(B-b)
            mixing=weight*(1-ease((j-61)/12))
            changed[ids,1]+=sign*mixing*(dst[:,0]-y)
            changed[np.ix_(ids,[0,2])]+=((dst[:,1]-rad)*mixing)[:,None]*direction
            transverse.append({'corner':corner,'width':float(width),'end':[float(x) for x in B]})
        new[idx]=changed
        details.append({'station':st,'mix':float(weight),'sides':transverse})
    # Carry the tip beneath the platform rim, continuing its descending tangent.
    # This spatial transform maps tube and cap together, including the buried cap fan.
    platform=s.objects['Knight | turned pedestal']
    platverts=world_vertices(platform)
    surface_z=float(platverts[:,2].max())
    t=ease((2.35-old[:,2])/.60); tip=float(old[:,2].min())
    extension=max(0.,tip-1.670)
    new[:,2]-=extension*t
    if registered:
        from registration import displacements,STATIONS
        fit=json.loads((D/'registration-fit.json').read_text())
        grid=chart['grid'];station=np.zeros(len(old));station[grid.ravel()]=np.repeat(np.arange(49)/4,256)
        radial,lateral=displacements(new,grid)
        new+=np.interp(station,STATIONS,fit['radial'])[:,None]*radial+np.interp(station,STATIONS,fit['width'])[:,None]*lateral
    displacement=posed(new,*pose)-posed(old,*pose);local=np.empty_like(old,dtype=np.float32)
    ob.data.vertices.foreach_get('co',local.ravel())
    local+=displacement@np.linalg.inv(np.asarray(ob.matrix_world)[:3,:3]).T
    ob.data.vertices.foreach_set('co',local.ravel());ob.data.update();bpy.context.view_layer.update()
    return dict(stations=details,max_displacement=float(np.linalg.norm(displacement,axis=1).max()),platform_top=surface_z,
                tip_before=tip,extension=extension,tip_after=float(new[:,2].min()))

def build(registered):
    assert sha(D/'parent.blend')==PARENT
    s=scene('parent');info=carve(s,registered)
    s['knight_mission008_mane']=json.dumps({'parent':PARENT,'construction':'Native ordered transverse sections. Crown, bilateral flanks, and a quadratic fillet.'})
    configure_render(s,144);save_model(s,D/'knight.blend')
    info['sha256']=sha(D/'knight.blend')
    (D/'geometry.json').write_text(json.dumps(info,indent=2))
    print({k:v for k,v in info.items() if k!='stations'},flush=True)

if __name__=='__main__':
    if sys.argv[-1] in ('fit','build'):build(sys.argv[-1]=='fit')
    else:survey()
