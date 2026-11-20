"""Transfer non-reflected local walnut variation continuously across rear mane UV islands."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]

def smooth(t):
    t=np.clip(t,0.,1.)
    return t*t*(3.-2.*t)

def rasterize(data,w,h):
    uv=data["uv"].astype(float)*[w,-h]+[-.5,h-.5]
    attrs=np.column_stack([data["sweep"],data["normal"]@data["view"]])
    fields=[]
    indices=[]
    for face,polygon in zip(data["tri"],uv):
        a,b=polygon[1:]-polygon[0]
        det=a[0]*b[1]-a[1]*b[0]
        if abs(det)<1.e-8:continue
        low=np.maximum(np.ceil(polygon.min(0)).astype(int),0)
        high=np.minimum(np.floor(polygon.max(0)).astype(int),[w-1,h-1])
        if np.any(high<low):continue
        yy,xx=np.mgrid[low[1]:high[1]+1,low[0]:high[0]+1]
        x=xx-polygon[0,0];y=yy-polygon[0,1]
        u=(x*b[1]-y*b[0])/det;v=(a[0]*y-a[1]*x)/det
        inside=(u>=0)&(v>=0)&(u+v<=1.)
        if not inside.any():continue
        u=u[inside];v=v[inside]
        fields.append(np.column_stack([1.-u-v,u,v])@attrs[face])
        indices.append((yy[inside]*w+xx[inside]))
    return np.concatenate(indices),np.concatenate(fields)

def random_grain():
    source=ROOT/"assets/knight/ref.png"
    rgb=np.asarray(Image.open(source).convert("RGB"),dtype=np.float32)
    patch=rgb[888:963,350:604]@np.array([.2126,.7152,.0722])
    # Extract diffuse detail. Slow falloff across the photographed pedestal
    # and any lighting gradients do not belong in the surface pigment.
    log=np.log(np.maximum(patch,1))
    for_blur=np.pad(log,((21,21),(21,21)),mode="reflect")
    freq_y=np.fft.fftfreq(for_blur.shape[0])[:,None]
    freq_x=np.fft.rfftfreq(for_blur.shape[1])[None,:]
    filt=np.exp(-2*np.pi**2*8.**2*(freq_y**2+freq_x**2))
    low=np.fft.irfft2(np.fft.rfft2(for_blur)*filt,s=for_blur.shape,axes=(0,1))[21:-21,21:-21]
    detail=np.clip(log-low,-.36,.24)
    # Overlap independent, unreflected pieces of the measured timber. The
    # periodic edges join only once around the full circumference.
    grid=512;stride=32
    texture=np.zeros((grid,grid));weight=np.zeros_like(texture)
    kernel=(np.sin((np.arange(64)+.5)*np.pi/64)**2)
    window=kernel[:,None]*kernel[None,:]
    rng=np.random.default_rng(996251)
    for row in range(0,grid,stride):
        for col in range(0,grid,stride):
            sx=int(rng.integers(0,detail.shape[1]-64+1))
            sy=int(rng.integers(0,detail.shape[0]-64+1))
            idx=np.ix_((row+np.arange(64))%grid,(col+np.arange(64))%grid)
            texture[idx]+=window*detail[sy:sy+64,sx:sx+64]
            weight[idx]+=window
    texture/=weight
    texture-=np.mean(texture)
    return texture, float(np.std(detail))

def sample(tile,x,y):
    h,w=tile.shape
    ix=np.floor(x).astype(int);iy=np.floor(y).astype(int)
    u=x-ix;v=y-iy
    return ((1-u)*(1-v)*tile[iy%h,ix%w]+u*(1-v)*tile[iy%h,(ix+1)%w]+
            v*(1-u)*tile[(iy+1)%h,ix%w]+v*u*tile[(iy+1)%h,(ix+1)%w])

def main():
    named=OUT/"source-atlas.png"
    parent=np.asarray(Image.open(named).convert("RGB"))
    h,w=parent.shape[:2]
    index,fields=rasterize(np.load(OUT/"surface.npz"),w,h)
    s,c,q,facing=fields.T
    theta=np.arctan2(q,c)
    # The visible fixed hemisphere and both caps retain their accepted pigment.
    active=smooth((-.012-facing)/.30)*smooth((s-.16)/.38)*smooth((3.95-s)/.15)
    ys,xs=np.divmod(index,w)
    prior=parent[ys,xs].astype(float)
    tile,observed_std=random_grain()
    # The angular field is periodic at +/-pi. Only the unwrapped angle term
    # traverses the full tile once. All distortions meet exactly at the seam.
    grain_x=144*s+17*np.sin(theta+.54*s)+9*np.sin(2*theta-.71*s)+5*np.sin(2.1*s)
    grain_y=512*theta/(2*np.pi)+23*s+5.4*np.sin(1.72*s+theta)+2.1*np.sin(3.8*s-2*theta)
    broad=.028*np.sin(2*theta+.94*s)+.018*np.sin(3.2*s+theta)
    # Robust medians taken along the original far-side material keep its
    # natural walnut colour and avoid retaining the folded diamond figure.
    bins=np.linspace(.18,3.90,20)
    measured=[]
    for distance in bins:
        mask=(abs(s-distance)<.29)&(facing<-.20)
        measured.append(np.median(prior[mask],axis=0) if mask.sum()>20 else np.median(prior[facing<-.24],axis=0))
    measured=np.asarray(measured)
    base=np.column_stack([np.interp(s,bins,measured[:,k]) for k in range(3)])
    delta=1.32*sample(tile,grain_x,grain_y)+broad
    replacement=base*np.exp(delta[:,None]*[1.,1.09,1.13])
    result=parent.copy()
    out=np.clip(np.rint(prior+(replacement-prior)*active[:,None]),0,255).astype(np.uint8)
    result[ys,xs]=out
    # Expand values one and two texels along UV borders for bilinear texture
    # reads. Never expand into another covered mane island.
    occupied=np.zeros((h,w),bool)
    occupied[ys,xs]=True
    adjusted=np.any(prior!=out,axis=1)
    rows,cols=ys[adjusted],xs[adjusted]
    for distance in (1,2):
        donors=[];targets=[]
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ry=rows+dy;rx=cols+dx
            valid=(ry>=0)&(ry<h)&(rx>=0)&(rx<w)
            valid &= ~occupied[np.clip(ry,0,h-1),np.clip(rx,0,w-1)]
            donors.append((rows[valid],cols[valid]));targets.append((ry[valid],rx[valid]))
        for donor,recipient in zip(donors,targets):
            result[recipient]=result[donor]
            occupied[recipient]=True
        rows=np.concatenate([k[0] for k in targets]);cols=np.concatenate([k[1] for k in targets])
    output=OUT/"pigment.png"
    Image.fromarray(result).save(output)
    jsonfile={"previous_texture":hashlib.sha256(named.read_bytes()).hexdigest(),
        "pigment_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
        "seed":996251,"sample_pixels_in_candidate_2":[350,888,604,963],
        "lengthwise_samples_per_world_unit":144,"circumference_samples":512,
        "hemisphere_facing_start":-.012,"hemisphere_facing_full":-.312,
        "covered_mane_texels":int(len(index)),"changed_texels_including_padding":int(np.any(result!=parent,axis=2).sum()),
        "original_measured_log_grain_stddev":observed_std,"replacement_log_grain_stddev":float(np.std(delta[active>.95])),
        "rear_median_rgb_before":np.median(prior[active>.95],0).tolist(),
        "rear_median_rgb_after":np.median(out[active>.95],0).tolist(),"rear_longitudinal_median_rgb":measured.tolist()}
    (OUT/"parameters.json").write_text(json.dumps(jsonfile,indent=2)+"\n")
    print(jsonfile)

if __name__=="__main__":
    main()
