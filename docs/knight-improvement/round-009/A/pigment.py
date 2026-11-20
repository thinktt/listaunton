"""Develop a continuous local walnut stain and fine figure in the existing UV atlas."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from pigment_coordinates import stain,chart,ease,bell,orbit

def field(size,h,w):
    # First fill the footprint of each atlas island. Only empty padding texels
    # may acquire the nearby colour, never another part's wood.
    chart=json.loads((D/'charts.json').read_text())
    occupied=Image.new('1',(w,h));draw=ImageDraw.Draw(occupied)
    samples=[];index=[];parts=[]
    for part,name in enumerate(chart['names']):
        with np.load(D/f'chart-{part}.npz') as data:
            pos,tri,uv=data['position'],data['tri'],data['uv']*[w,-h]+[-.5,h-.5]
        for t in np.rint(uv).astype(np.int32):draw.polygon(t.flatten().tolist(),fill=1)
        if name not in ['Knight | continuous horse head and neck','Knight | near eye','Knight | far eye']:continue
        if name.endswith(' eye'):active=np.ones(len(tri),bool)
        else:
            x=pos[:,0];z=pos[:,2];near=(x>-.7)&(x<1.40)&(z>3.12)&(z<4.72)&(abs(pos[:,1])>.055)
            active=near[tri].any(1)
        for vids,tex in zip(tri[active],uv[active]):
            a,b=tex[1:]-tex[0];det=a[0]*b[1]-a[1]*b[0]
            if abs(det)<1e-8:continue
            lo=np.maximum(np.ceil(tex.min(0)).astype(int),0);hi=np.minimum(np.floor(tex.max(0)).astype(int),[w-1,h-1])
            if np.any(hi<lo):continue
            yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
            x=xx-tex[0,0];y=yy-tex[0,1];u=(x*b[1]-y*b[0])/det;v=(a[0]*y-a[1]*x)/det
            take=(u>=0)&(v>=0)&(u+v<=1)
            if not take.any():continue
            u,v=u[take],v[take]
            coords=np.column_stack((1-u-v,u,v))@pos[vids]
            samples.append(coords);index.append(yy[take]*w+xx[take]);parts.append(np.full(len(u),part,np.int16))
    return np.concatenate(index),np.vstack(samples),np.concatenate(parts),np.asarray(occupied).copy()
def noise(p,seed):
    # Deterministic interpolated value noise in the whole billet. Sampling
    # signed depth gives the far side its own continuous physical figure.
    ix=np.floor(p).astype(np.int32);f=ease(p-ix);result=np.zeros(len(p))
    for dx in (0,1):
        for dy in (0,1):
            for dz in (0,1):
                i=ix+[dx,dy,dz]
                h=(i[:,0].astype(np.uint32)*np.uint32(2654435761)^i[:,1].astype(np.uint32)*np.uint32(2246822519)^i[:,2].astype(np.uint32)*np.uint32(3266489917)^np.uint32(seed))
                h^=h>>16;h*=np.uint32(2246822519);h^=h>>13;h*=np.uint32(3266489917);h^=h>>16
                val=h.astype(float)/2147483647.5-1
                fx=f[:,0] if dx else 1-f[:,0];fy=f[:,1] if dy else 1-f[:,1];fz=f[:,2] if dz else 1-f[:,2]
                result+=val*fx*fy*fz
    return result
def fine_figure(p):
    x,y,z=p.T;along=.934*x-.358*z;cross=.358*x+.934*z
    warp=noise(p*[5.5,5.1,5.3],7203)+.29*noise(p*12,708)
    mid=noise(np.column_stack((along*26,cross*72+3.5*warp,44*y)),3912)
    fine=noise(np.column_stack((along*63,cross*141+4.6*warp,86*y)),9023)
    pore=noise(np.column_stack((along*27,cross*110+3.0*warp,87*y)),1146)
    return .14*mid+.118*fine-.085*np.maximum(0,pore-.19)+.028*np.sin(cross*35+.9*warp+4*y)
def main():
    source=np.asarray(Image.open(D/'source-atlas.png').convert('RGB'));h,w=source.shape[:2]
    cache=D/'atlas-samples.npz'
    if not cache.exists():
        idx,pos,part,occ=field(None,h,w);np.savez_compressed(cache,idx=idx,pos=pos.astype(np.float32),part=part,occ=occ)
    data=np.load(cache);idx,pos,part,occupied=(data[k] for k in ['idx','pos','part','occ'])
    # The inherited denser far-side heartwood has finer, darker figure.
    # Ease the stain across the billet so that figure keeps its separation.
    flank=1-.67*ease((pos[:,1]+.11)/.29)
    weight=stain(pos)*flank;eyes=part!=6
    weight[eyes]=.17*flank[eyes]
    active=weight>.0001;idx,pos,weight,eyes=idx[active],pos[active],weight[active],eyes[active]
    rr,cc=np.divmod(idx,w);old=source[rr,cc].astype(float);detail=fine_figure(pos)
    delta=weight[:,None]*(np.log([.774,.75,.676])+detail[:,None]*[1.,1.04,1.08])
    delta[eyes]=weight[eyes,None]*(np.log([.72,.70,.68])+detail[eyes,None]*.46)
    dyed=old*np.exp(delta)
    # Work denser heartwood into the seat and lower return. Replacing the
    # stretched grain there with billet-space fibres keeps the cut continuous.
    u,v=chart(pos);_,_,margin=orbit(pos)
    seat=ease((.358-abs(u+.004))/.144)*bell(v-margin+.010,.066)
    seat*=ease((abs(pos[:,1])-.11)/.14)*(1-.68*ease((pos[:,1]+.1)/.27))*(~eyes)
    heart=np.array([72.,38.,24.])*np.exp(detail[:,None]*.85)
    dyed+=(heart-dyed)*(.79*seat[:,None])
    adjusted=np.uint8(np.clip(np.rint(dyed),0,255))
    out=source.copy();out[rr,cc]=adjusted
    changed=np.any(adjusted!=old,axis=1);rr,cc=rr[changed],cc[changed]
    # Replicate the texture delta rather than the color into the existing
    # filtering margins. This retains the original wood across each UV seam.
    for _ in range(3):
        donors=[];recips=[]
        for oy,ox in [(1,0),(-1,0),(0,1),(0,-1)]:
            y,x=rr+oy,cc+ox
            ok=(y>=0)&(y<h)&(x>=0)&(x<w)
            ok&=~occupied[np.clip(y,0,h-1),np.clip(x,0,w-1)]
            donors.append((rr[ok],cc[ok]));recips.append((y[ok],x[ok]))
        for donor,rc in zip(donors,recips):
            ratio=(out[donor].astype(float)+.5)/(source[donor].astype(float)+.5)
            out[rc]=np.clip(np.rint(source[rc]*ratio),0,255).astype(np.uint8);occupied[rc]=True
        rr=np.concatenate([s[0] for s in recips]);cc=np.concatenate([s[1] for s in recips])
    path=D/'pigment.png';Image.fromarray(out).save(path)
    m={'input_sha256':hashlib.sha256((D/'source-atlas.png').read_bytes()).hexdigest(),
       'output_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'dimensions':[w,h],
       'covered_anatomical_samples':len(idx),'changed_rgb_texels':int(np.any(out!=source,axis=2).sum()),
       'strong_cheek_multipliers':[.774,.75,.676],'eye_floor_stain_weight':.17,'far_side_stain_fraction':.33,
       'fine_grain_seeds':[7203,708,3912,9023,1146]}
    (D/'pigment-parameters.json').write_text(json.dumps(m,indent=2)+'\n');print(m)
if __name__=='__main__':main()
