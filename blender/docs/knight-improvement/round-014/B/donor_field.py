"""Extract only pore-scale colour fluctuations from physical neck patches."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
from surface import sample
D=Path(__file__).resolve().parent
def make():
    atlas=np.asarray(Image.open(D/'parent-pigment.png').convert('RGB'));h,w=atlas.shape[:2]
    grid=dict(np.load(D/'neck-donor.npz'));fields=[];guards=[]
    for label,coords in zip(['near','far'],grid['uv']):
        good=np.isfinite(coords[:,:,0])
        # Taper donor contrast before the actual patch or model surface ends.
        # This avoids copying a stretched scanline from an unobserved area.
        padded=np.pad(np.uint8(good)*255,14)
        interior=Image.fromarray(padded).filter(ImageFilter.MinFilter(17)).filter(ImageFilter.GaussianBlur(3))
        guards.append(np.asarray(interior,float)[14:-14,14:-14]/255)
        # Fill missing chart points by the closest valid measure in that
        # physical cross section. Retain its actual native figure.
        for row in coords:
            ok=np.isfinite(row[:,0])
            if ok.all():continue
            if not ok.any():raise ValueError('Entire donor station outside neck')
            for j in [0,1]:row[:,j]=np.interp(np.arange(len(row)),np.flatnonzero(ok),row[ok,j])
        a=sample(atlas,coords[:,:,0]*w-.5,(1-coords[:,:,1])*h-.5)
        pic=Image.fromarray(np.uint8(np.clip(a,0,255)));pic.transpose(Image.Transpose.FLIP_TOP_BOTTOM).save(D/f'neck-grain-{label}.png')
        dim=lambda b:np.log(np.asarray(b,float)@[.2126,.7152,.0722]+8.)
        # Support both pore-sized ends and the slightly broader ripple.
        small=dim(pic)-dim(pic.filter(ImageFilter.GaussianBlur(2.5)))
        medium=dim(pic.filter(ImageFilter.GaussianBlur(2.5)))-dim(pic.filter(ImageFilter.GaussianBlur(13.)))
        fields.append(np.stack((np.clip(small,-.38,.38),np.clip(medium,-.43,.43)),axis=-1))
    np.savez_compressed(D/'neck-figure.npz',grain=np.array(fields,dtype=np.float32),guard=np.array(guards,dtype=np.float32),spacing=grid['spacing'],x_min=grid['x_min'],z_min=grid['z_min'])
if __name__=='__main__':make()
