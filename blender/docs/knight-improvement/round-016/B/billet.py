"""Return native short walnut figure to the crown, preserving the surrounding atlas."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from surface_math import raster,sample
MANE='swept rounded mane'
def ease(q):
    q=np.clip(q,0,1);return q*q*(3-2*q)
def map_texels():
    d=np.load(D/'surfaces.npz');tri=d['tri'];xyz=d['xyz'][tri];im=Image.open(D/'parent-pigment.png');w,h=im.size
    q=d[MANE]*[w,-h]+[0,h];mask=Image.new('L',(w,h));pen=ImageDraw.Draw(mask)
    for k in d.files:
        if k in [MANE,'tri','xyz']:continue
        for uv in d[k]*[w,-h]+[0,h]:pen.polygon(list(map(tuple,uv)),fill=255)
    marked=np.asarray(mask.filter(ImageFilter.MaxFilter(5)))>0
    pos=np.zeros((h,w,3),np.float32);active=np.zeros((h,w),bool)
    for i in np.where(xyz[:,:,2].max(1)>4.70)[0]:
        points=raster(q[i],w,h)
        if points is None:continue
        y,x,b=points;where=~marked[y,x];y,x=y[where],x[where];pos[y,x]=b[where]@xyz[i];active[y,x]=True
    yy,xx=np.nonzero(active)
    np.savez_compressed(D/'crown-address.npz',py=yy,px=xx,co=pos[yy,xx],protected=marked)
def restore():
    f=np.load(D/'crown-address.npz');Y,X=f['py'],f['px'];x,y,z=f['co'].T
    fig=np.load(D/'neck-figure.npz');step=float(fig['spacing']);don=fig['grain'][1];guard=fig['guard'][1]
    # The same oblique grain passes through both sides of the crown as it would in one billet.
    # This donor is high-pass grain from the released timber, sampled in physical model units.
    bx=-.052+.86*y+.144*x+1.38*(z-5.08)+.036*np.sin(5*x+2*y)
    bz=3.48+.92*x-.21*y+.12*(z-5.08)+.026*np.sin(6*y+4*x)
    dx=(bx-float(fig['x_min']))/step;dz=(bz-float(fig['z_min']))/step
    fine,coarse=sample(don,dx,dz).T;inside=sample(guard[:,:,None],dx,dz)[:,0]
    raw=Image.open(D/'parent-pigment.png').convert('RGB');old=np.asarray(raw);color=old[Y,X].astype(float)
    # Only the absolute native hue and broad growth pattern are retained from the original UV island.
    # A local weighted average of native neighbors avoids dark bleed at island borders.
    good=np.zeros(old.shape[:2],np.uint8);good[Y,X]=255
    def avg(channel):
        a=np.uint8(np.rint(channel*good.astype(float)/255))
        value=np.asarray(Image.fromarray(a).filter(ImageFilter.GaussianBlur(4.8)),float)[Y,X]
        return 255*value/np.maximum(1,weight)
    weight=np.asarray(Image.fromarray(good).filter(ImageFilter.GaussianBlur(4.8)),float)[Y,X]
    softened=np.stack([avg(old[:,:,k]) for k in range(3)],axis=-1)
    # A generous fade down both real flanks preserves the previously restored hanging mane.
    cover=ease((z-4.71)/.23)*ease((x+1.14)/.25)*ease((.285-x)/.085)*inside
    under=ease((abs(y)-.114)/.095)
    detail=sample(don,dx*1.12+23+.37*dz,dz*1.18-.22*dx+11)
    # The lateral carved face exposes the darker end of this billet; the finish varies smoothly across it.
    tone=np.exp(.73*fine+.21*coarse+.40*detail[:,0]+.14*detail[:,1]-.31*under)
    replacement=(.44*color+.56*softened)*tone[:,None]
    out=old.copy();out[Y,X]=np.uint8(np.clip(np.rint(color+cover[:,None]*(replacement-color)),0,255))
    changed=np.any(out!=old,axis=2);assert not np.any(changed&f['protected'])
    dest=D/'crown-walnut.png';Image.fromarray(out).save(dest,compress_level=5)
    (D/'pigment-proof.json').write_text(json.dumps({'changed_texels':int(changed.sum()),'changed_texels_on_other_parts':0,
       'minimum_height_of_changed_texel':float(z[changed[Y,X]].min()),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
       'rms_srgb_change_in_modified_texels':float(np.sqrt(np.mean((old[changed].astype(float)-out[changed])**2)))},indent=2)+'\n')
if __name__=='__main__':map_texels();restore()
