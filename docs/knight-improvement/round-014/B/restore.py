"""Recover the billet's colour and its own short figure across both mane faces."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image
from surface import W,H,Z0,Z1,sample
D=Path(__file__).resolve().parent
def ease(v):
    v=np.clip(v,0.,1.);return v*v*(3-2*v)
def blur(v,sx,sy):
    # True circumference wraps horizontally. Reflect the two ends in z.
    n=max(1,int(3.5*sy));v=np.pad(v,[(n,n),(0,0)],mode='reflect')
    freq=np.fft.fftfreq(len(v))[:,None];u=np.fft.rfftfreq(W)[None,:]
    k=np.exp(-2*np.pi**2*((sx*u)**2+(sy*freq)**2))
    return np.fft.irfft2(np.fft.rfft2(v)*k,s=v.shape,axes=(0,1))[n:-n]
def bell(x,width):return np.exp(-(x/width)**2)
PARAMS=[
    # Angular and axial scales of stain estimation, correction, donor,
    # near-to-edge wood tone and cross-grain intensity.
    (53,20,.93,.00,.10,.00),
    (62,23,1.02,.55,.18,1.45),
    (76,29,1.10,.77,.25,1.64),
    (73,25,1.10,.80,.20,1.08,1.14,.48,.94),
    (68,24,1.11,.85,.21,1.22,1.47,.54,.99),
    (70,27,1.10,.81,.20,1.17,1.32,.75,1.18),
    (70,25,1.12,.84,.21,1.34,1.29,.48,1.45,.62),
    (71,26,1.13,.85,.22,1.42,1.40,.49,1.59,.82),
    (68,25,1.11,.82,.21,1.31,1.21,.40,1.46,.87),
    (71,26,1.11,.82,.215,1.32,1.22,.32,1.40,.62,.48),
    (71,25,1.11,.82,.22,1.34,1.26,.38,1.34,.74,.62)]
def surface(data,i):
    sx,sy,strength,mix,sweep,contrast=PARAMS[i][:6]
    color=data['rgb'];y,x=np.indices((H,W));t=(x+.5-W/2)/(W/2)*np.pi;z=Z1-(y+.5)*(Z1-Z0)/H
    sigma=abs(t);zr=ease((z-1.93)/.53)*(1-ease((z-4.35)/.36))
    face=ease((sigma-.37)/.71)*(1-ease((sigma-2.13)/.74))*zr
    # The two dark longitudinal residues can be seen in the unlit native
    # surface. No registered image or camera ray is used in this adjustment.
    shoulder=bell(sigma-1.53,.38)
    confidence=1-.96*shoulder
    l=np.log(8+color@[.2126,.7152,.0722])
    long=blur(l,2.1,sy)
    broad=blur(long*confidence,sx,36)/blur(confidence,sx,36)
    delta=np.clip(broad-long,-.52,.85)
    # Recover the original gradual tone toward the real blade edge,
    # while leaving the rather different crown and distal end in place.
    delta=strength*delta+sweep*(.28+bell(sigma-.91,.52))
    # Donor is contiguous native rear wood at neighboring angle and height.
    # Its mean is removed so no copied illumination enters the repair.
    fine=l-blur(l,3.5,14.)
    donor_x=np.where(t<0,365.+.70*(x-240.),569.+.74*(x-714.))
    donor_x+=10*np.sin(y/156+np.sin(x/149))*np.sin(np.pi*y/H)
    donor_y=.86*y+56+9*np.sin(x/85+y/181)
    figure=sample(fine[:,:,None],donor_x,donor_y)[:,:,0]
    if len(PARAMS[i])>6:
        native=dict(np.load(D/'neck-figure.npz'));spacing=float(native['spacing'])
        scale,oblique,pore=PARAMS[i][6:9]
        radius=data['depth'];lat=abs(np.sin(t))*radius;fore=-np.cos(t)*radius
        # The donor is the native opposite-neck patch, sampled in model
        # units. Its buried-grain elevation varies through the thickness of
        # the billet; the new growth marks can end on the carved broad face.
        bx=-.408+scale*(fore+.09)+.052*np.sin(3.4*z+2.0*fore)
        bz=3.09+.76*(z-3.30)-oblique*(lat-.30)+.18*fore
        bx+=np.where(t<0,0.,.08);bz+=np.where(t<0,0.,.13)
        donor=sample(native['grain'][1],(bx-native['x_min'])/spacing,(bz-native['z_min'])/spacing)
        figure=(pore*donor[:,:,0]+(.82 if i>=9 else .77)*donor[:,:,1])
        if i>=9:
            guard=sample(native['guard'][1,:,:,None],(bx-native['x_min'])/spacing,(bz-native['z_min'])/spacing)[:,:,0]
            figure=guard*figure+(1-guard)*fine
        if len(PARAMS[i])>9:
            # Short dark vessels are drawn from a neighboring patch of
            # exactly the same walnut, independently of the broad rays.
            # Small pores terminate along the surface instead of forming
            # continuous rings as the mane turns toward the center back.
            px=bx+.084+.20*(lat-.30)+.062*(z-3.26)
            pz=bz+.104+.12*fore+.035*np.sin(2.7*z)
            pores=sample(native['grain'][1],(px-native['x_min'])/spacing,(pz-native['z_min'])/spacing)
            weight=PARAMS[i][9]
            if i>=9:
                weight=weight*sample(native['guard'][1,:,:,None],(px-native['x_min'])/spacing,(pz-native['z_min'])/spacing)[:,:,0]
            figure+=weight*(1.35*pores[:,:,0]+.30*pores[:,:,1]-1.10*np.maximum(0.,-pores[:,:,0]-.019))
        # The softer local stain near the inner returned rim is inherited
        # from the real mane, including its distinct wood at the shoulder.
        delta-=.092*ease((sigma-1.43)/.63)
    texture=mix*(contrast*figure-fine)*(.24+.76*bell(sigma-1.55,.78))
    correction=face*(delta+texture)
    if i>=9:
        # The two shoulder corrections meet over the center back. Retain
        # its real figure, easing only the compressed old centerline stain.
        rear=bell(sigma,.53)*zr
        correction+=PARAMS[i][10]*rear*(blur(l,30,22)-blur(l,2.2,16))
    return correction,np.clip(color*np.exp(correction[:,:,None]),0,255),face
def bake(i,data,orig):
    correction,shown,face=surface(data,i)
    y,x=data['atlas_y'].astype(int),data['atlas_x'].astype(int);xy=data['chart']
    value=sample(correction[:,:,None],xy[:,0]-.5,xy[:,1]-.5,True)[:,0]
    h,w=orig.shape[:2];f=np.zeros((h,w),np.float32);valid=np.zeros((h,w),bool)
    f[y,x]=value;valid[y,x]=True
    other=np.unpackbits(data['protected'])[:w*h].reshape(h,w)>0
    for k in range(2):
        old=valid.copy();oldf=f.copy()
        for shift in ((0,1),(1,0),(0,-1),(-1,0)):
            near=np.roll(old,shift,(0,1))&~valid&~other
            f[near]=np.roll(oldf,shift,(0,1))[near];valid|=near
    out=orig.copy();use=valid&(abs(f)>.0002)&~other
    out[use]=np.uint8(np.clip(np.round(orig[use]*np.exp(f[use,None])),0,255))
    file=D/f'atlas-{i}.png';Image.fromarray(out).save(file,compress_level=5)
    Image.fromarray(np.uint8(shown)).save(D/f'surface-{i}.png')
    changed=np.any(orig!=out,axis=2)
    q={'recipe':PARAMS[i],'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
       'mane_texels':len(x),'changed_texels_including_bleed':int(changed.sum()),'changed_protected':int(np.sum(changed&other)),
       'max_abs_channel_change':int(np.max(np.abs(out.astype(np.int16)-orig)))}
    (D/f'restoration-{i}.json').write_text(json.dumps(q,indent=2)+'\n');print(i,q,flush=True)
if __name__=='__main__':
    grid=dict(np.load(D/'surface-field.npz'));raw=np.asarray(Image.open(D/'parent-pigment.png').convert('RGB'))
    for key in sys.argv[1:]:bake(int(key),grid,raw)
