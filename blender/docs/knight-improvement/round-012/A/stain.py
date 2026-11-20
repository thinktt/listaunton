"""Give the entire hanging blade a deeper walnut finish over its existing grain.

The near/far and end fades are defined by billet height and depth. Neither the
camera nor the line of contact enters this calculation.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
D=Path(__file__).resolve().parent
def ease(v):
    t=np.clip(v,0,1);return t*t*(3-2*t)
def main():
    a=np.asarray(Image.open(D/'source-atlas.png').convert('RGB'));h,w=a.shape[:2]
    chart=np.load(D/'mane-chart.npz')
    tex=chart['uv']*[w,-h]+[-.5,h-.5];other=chart['other_uv']*[w,-h]+[-.5,h-.5]
    mask=Image.new('1',(w,h));draw=ImageDraw.Draw(mask)
    for tri in np.rint(other).astype(np.int32):draw.polygon(tri.flatten().tolist(),fill=1)
    occupied=np.asarray(mask);weight=np.zeros((h,w),np.float32)
    for t,xyz in zip(tex,chart['xyz']):
        lo=np.maximum(np.ceil(t.min(0)).astype(int),0);hi=np.minimum(np.floor(t.max(0)).astype(int),[w-1,h-1])
        if (hi<lo).any():continue
        aa,bb=t[1:]-t[0];det=aa[0]*bb[1]-aa[1]*bb[0]
        if abs(det)<1e-8:continue
        yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];x=xx-t[0,0];y=yy-t[0,1]
        u=(x*bb[1]-y*bb[0])/det;v=(aa[0]*y-aa[1]*x)/det;on=(u>=0)&(v>=0)&(u+v<=1)
        if not on.any():continue
        u,v=u[on],v[on];p=np.column_stack((1-u-v,u,v))@xyz;yy,xx=yy[on],xx[on]
        height=ease((p[:,2]-2.03)/.65)*(1-ease((p[:,2]-4.18)/.39))
        side=1-.42*ease((p[:,1]+.30)/.64)
        heartwood=.21+.79*ease((p[:,0]+1.38)/.42)
        weight[yy,xx]=np.maximum(weight[yy,xx],height*side*heartwood)
    # Add three filtering texels on blank padding. Other parts retain every byte.
    w0=weight.copy()
    pad=np.asarray(Image.fromarray(np.rint(weight*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)),float)/255
    weight=np.where(weight>0,weight,pad);weight[occupied]=0
    dye=np.array([.615,.635,.660])
    out=np.rint(a*np.exp(weight[...,None]*np.log(dye))).clip(0,255).astype(np.uint8)
    Image.fromarray(out).save(D/'pigment.png',compress_level=5)
    notes={'input':hashlib.sha256((D/'source-atlas.png').read_bytes()).hexdigest(),'output':hashlib.sha256((D/'pigment.png').read_bytes()).hexdigest(),'near_srgb_multiplier':dye.tolist(),'far_strength':.58,'rear_to_inner_stain_fraction':[.21,1.0],'longitudinal_fade_x':[-1.38,-.96],'changed_texels':int(np.any(out!=a,axis=2).sum()),'other_island_changed_texels':int(np.any(out!=a,axis=2)[occupied].sum()),'map_size':[w,h],'unchanged_figure':'Original encoded figure on the complete mane, graded across rest-space billet length, height and depth.'}
    (D/'stain.json').write_text(json.dumps(notes,indent=2)+'\n');print(notes)
if __name__=='__main__':main()
