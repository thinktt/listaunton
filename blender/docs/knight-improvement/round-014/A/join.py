"""Balance linear-filter samples across physical chart cuts with identical 3D endpoints."""
import numpy as np
def join_chart_edges(image,allowed_x,allowed_y,uv,xyz):
    h,w=image.shape[:2];edges={}
    for t,p in zip(uv,xyz):
        for a,b in ((0,1),(1,2),(2,0)):
            k0,k1=tuple(p[a]),tuple(p[b])
            if k1<k0:a,b,k0,k1=b,a,k1,k0
            key=(k0,k1)
            chart=tuple(t[a])+tuple(t[b])
            edges.setdefault(key,set()).add(chart)
    sa=[];sb=[]
    for (p,q),charts in edges.items():
        if len(charts)<2 or max(p[2],q[2])<1.86 or min(p[2],q[2])>4.73:continue
        first,*others=sorted(charts)
        for other in others:
            a0,a1=np.reshape(first,(2,2));b0,b1=np.reshape(other,(2,2))
            n=max(1,int(np.ceil(max(np.linalg.norm(a1-a0),np.linalg.norm(b1-b0))*w/1.5)))
            f=(np.arange(n)+.5)[:,None]/n;sa.extend((1-f)*a0+f*a1);sb.extend((1-f)*b0+f*b1)
    def weights(uv):
        p=uv*np.array([w,-h])+[-.5,h-.5];i=np.floor(p).astype(int);x,y=i.T;f,g=(p-i).T
        return np.stack([y*w+x,y*w+x+1,(y+1)*w+x,(y+1)*w+x+1],axis=1),np.stack([(1-f)*(1-g),f*(1-g),(1-f)*g,f*g],axis=1)
    ia,wa=weights(np.array(sa));ib,wb=weights(np.array(sb));ix=np.concatenate([ia,ib],1);wt=np.concatenate([wa,-wb],1)
    allow=np.zeros(h*w,bool);allow[allowed_y.astype(np.int32)*w+allowed_x]=True
    mask=np.all(allow[ix],axis=1);ix=ix[mask];wt=wt[mask]
    ids,local=np.unique(ix,return_inverse=True);local=local.reshape(ix.shape)
    rgb=image.reshape(-1,3)[ids].astype(float);base=rgb.copy()
    den=np.bincount(local.ravel(),weights=np.abs(wt).ravel(),minlength=len(ids))
    for _ in range(16):
        diff=np.einsum('ik,ikc->ic',wt,rgb[local])
        corr=np.zeros_like(rgb);np.add.at(corr,local,-wt[:,:,None]*diff[:,None,:])
        rgb+=.48*corr/np.maximum(den[:,None],.2)
        rgb+=.012*(base-rgb)
    image.reshape(-1,3)[ids]=np.uint8(np.clip(np.rint(rgb),0,255))
    return {'paired_samples':int(len(ix)),'unique_boundary_filter_texels':int(len(ids))}
