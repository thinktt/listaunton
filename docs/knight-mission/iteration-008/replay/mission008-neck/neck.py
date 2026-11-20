"""Three approximately planar longitudinal faces in the neck's unbent rest frame."""
from pathlib import Path
from math import ceil as math_ceil
import sys
import numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D))
import survey as su
from mission_scene import world_vertices

def monotone(x,xs,ys):
    """Shape-preserving cubic for the two gently turning longitudinal splines."""
    xs=np.asarray(xs); ys=np.asarray(ys); h=np.diff(xs); slopes=np.diff(ys)/h
    m=np.r_[slopes[0],np.zeros(len(xs)-2),slopes[-1]]
    for k in range(1,len(xs)-1):
        a,b=slopes[k-1:k+1]
        if a*b>0:
            left=2*h[k]+h[k-1]; right=h[k]+2*h[k-1]
            m[k]=(left+right)/(left/a+right/b)
    i=np.clip(np.searchsorted(xs,x)-1,0,len(xs)-2)
    t=np.clip((x-xs[i])/h[i],0,1)
    return ((2*t**3-3*t*t+1)*ys[i]+(t**3-2*t*t+t)*h[i]*m[i]
            +(-2*t**3+3*t*t)*ys[i+1]+(t**3-t*t)*h[i]*m[i+1])

def field(variant):
    data=np.load(D/'sections-parent.npz')
    mask=(data['z']>=1.64)&(data['z']<=3.34)
    z=data['z'][mask]; th=data['angles'][:-1]
    rad=data[su.HEAD+'r'][mask,:-1]; center=data[su.HEAD+'info'][mask,1:3]
    abs_theta=np.abs(th); c=np.cos(th); sn=np.abs(np.sin(th)); degrees=np.degrees(abs_theta)
    strengths=[.85,.94,.95]; front_widths=[.47,.63,.56]
    faceting=strengths[variant]
    target=rad.copy()
    knots=[1.6,1.72,1.82,1.95,2.04,2.19,2.42,2.72,3.0,3.2,3.36]
    front=monotone(z,knots,[1.065,1.075,1.100,1.117,1.110,1.045,.904,.70,.491,.383,.315])
    back=monotone(z,knots,[-1.009,-1.020,-1.035,-1.061,-1.079,-1.100,-1.117,-1.105,-1.089,-1.098,-1.091])
    for i,height in enumerate(z):
        cx,cy=center[i]; face=front[i]-cx
        half_width=front_widths[variant]*.5*(rad[i,90]+rad[i,270])
        back_delta=back[i]-(cx-rad[i,0])
        proposed=rad[i].copy()
        for sign in [-1,1]:
            side=th*sign>=0; anchor_deg=78
            a=np.deg2rad(anchor_deg)
            edge_r=rad[i,int(180+sign*anchor_deg)]
            end_x,end_y=edge_r*np.cos(a),edge_r*np.sin(a)
            # The front and side facets intersect at an oblique arris in plan.
            corner_angle=np.arctan2(half_width,face)
            side_r=(face*end_y-half_width*end_x)/(c*(end_y-half_width)+sn*(face-end_x)+1.e-10)
            front_r=face/np.maximum(c,.1)
            plane=np.where(abs_theta<corner_angle,front_r,side_r)
            blend=1-su.ease((degrees-68)/30)
            proposed[side]=rad[i,side]+blend[side]*(plane[side]-rad[i,side])
        # The heel is one clean curve, feathered round the rear quarter.
        proposed-=back_delta*su.ease((degrees-93)/81)
        # A lightly buffed edge between the planes, with no added concave groove.
        sigma=3.5 if variant!=2 else 3.6+9.4*(1-su.ease((height-1.90)/.53))
        w=np.arange(-math_ceil(3*sigma),math_ceil(3*sigma)+1);g=np.exp(-.5*(w/sigma)**2);g/=g.sum()
        smooth=sum(k*np.roll(proposed,j) for j,k in zip(w,g))
        # The wide planar breast rolls into a more rounded foot. Use the
        # actual platform axis as center of the gentle, almost elliptic seat.
        low=1-su.ease((height-1.69)/.37)
        ax,ay=1.062,.928
        seat_x=.024
        p=(cx-seat_x)*c/ax**2+cy*np.sin(th)/ay**2
        q=c*c/ax**2+sn*sn/ay**2
        t=(cx-seat_x)**2/ax**2+cy*cy/ay**2-1
        seat=(-p+np.sqrt(p*p-q*t))/q
        if variant:
            # The inherited shell has a convex underside. Preserve that roll
            # through the contact instead of replacing it with a straight skirt.
            low=1-su.ease((height-1.71)/.50)
            seat=rad[i]*(1-.012*c*c+.059*sn*sn)
        if variant==2:
            low=1-su.ease((height-1.65)/.53)
        smooth=(1-low)*smooth+low*seat
        target[i]=1+faceting*(smooth/rad[i]-1)
    return z,np.r_[th,np.pi],center,np.column_stack([target,target[:,0]])

def apply(scene,variant=0):
    """Call on the accepted checkpoint-007 mesh or its mane-only derivative."""
    zgrid,agrid,center,scales=field(variant)
    stats={}
    for name in (su.HEAD,su.HIDDEN):
        obj=scene.objects[name]; original=world_vertices(obj); v=su.rest(scene,original)
        z=v[:,2];cx=np.interp(z,zgrid,center[:,0]);cy=np.interp(z,zgrid,center[:,1]);delta=v[:,:2]-np.column_stack([cx,cy])
        direction=np.arctan2(delta[:,1],delta[:,0]); indices=np.clip(np.searchsorted(agrid,direction)-1,0,len(agrid)-2)
        ai=(direction-agrid[indices])/(agrid[indices+1]-agrid[indices])
        zi=np.clip(np.searchsorted(zgrid,z)-1,0,len(zgrid)-2);t=np.clip((z-zgrid[zi])/(zgrid[zi+1]-zgrid[zi]),0,1)
        s=(1-t)*((1-ai)*scales[zi,indices]+ai*scales[zi,indices+1])+t*((1-ai)*scales[zi+1,indices]+ai*scales[zi+1,indices+1])
        w=su.ease((z-1.52)/.16)*(1-su.ease((z-3.10)/.31))
        # The native union has long, extremely thin axial triangles at its
        # rear weld under the mane. End the heel correction before that weld.
        rear=su.ease((np.abs(direction)-np.radians(84))/np.radians(36))
        w*=1-rear*su.ease((z-2.54)/.37)
        offset=delta*((s-1)*w)[:,None];u=v.copy();u[:,:2]+=offset
        world_delta=su.world(scene,u)-su.world(scene,v)
        mat=np.array(obj.matrix_world);local_delta=world_delta@np.linalg.inv(mat[:3,:3]).T
        co=np.empty((len(v),3),np.float32);obj.data.vertices.foreach_get('co',co.ravel())
        obj.data.vertices.foreach_set('co',np.asarray(co+local_delta,dtype=np.float32).ravel());obj.data.update()
        dist=np.linalg.norm(local_delta,axis=1)
        stats[name]={'changed_vertices':int((dist>1.e-6).sum()),'max_shift':float(dist.max())}
    return stats
