"""Replace the previous slit baked into the lathe UV map with neighbouring boxwood."""
import argparse
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
cli=argparse.ArgumentParser()
cli.add_argument('--input',type=Path,default=ROOT/'history/bishop-mission-026/bishop-boxwood-albedo.png')
cli.add_argument('--out',type=Path,default=ROOT/'build/bishop-mission/healed-boxwood.png')
args=cli.parse_args()
image=Image.open(args.input)
assert image.size==(2048,2048)
src=np.asarray(image);dst=src.copy();h,w=src.shape[:2]
low=np.asarray(image.filter(ImageFilter.GaussianBlur(4)),dtype=np.float32)
# The guide follows the top edge of the old diagonal in the 2048px lathe atlas.
# Each new texel borrows grain from wood on both sides at the same azimuth.
guide=np.array([[1033,793],[1045,786],[1060,777],[1085,765],[1130,748],[1190,730],[1250,717],[1330,705],
                [1420,696],[1510,692],[1560,691],[1610,693],[1670,697],[1740,705],[1810,717],
                [1870,732],[1920,748],[1960,765],[1994,782]])
source_sha=hashlib.sha256(args.input.read_bytes()).hexdigest()
assert source_sha=='c09df839f9ab363f5e4c2ed3d669293f99a81de59a449f85096a49e849aa8f2a'

def smooth(values):
    t=np.clip(values,0,1)
    return t*t*(3-2*t)

for x in range(1024,2009):
    top=float(np.interp(x,guide[:,0],guide[:,1]))
    thickness=float(np.interp(x,[1024,1050,1100,1650,1890,2009],[6,18,25,26,18,7]))
    lo=top-11; hi=top+thickness+3
    y=np.arange(int(lo)-8,int(hi)+9)
    alpha=smooth((y-(lo-7))/8)*smooth(((hi+7)-y)/8)
    alpha*=smooth((x-1026)/18)*smooth((2007-x)/28)
    local=np.clip((y-lo)/(hi-lo),0,1)[:,None]
    offset=int(np.ceil(hi-lo))+12
    upper=np.mean(low[int(lo)-9:int(lo)-4,x],axis=0)
    lower=np.mean(low[int(hi)+5:int(hi)+10,x],axis=0)
    donor=(1-local)*(upper+src[y-offset,x].astype(float)-low[y-offset,x])+local*(lower+src[y+offset,x].astype(float)-low[y+offset,x])
    changed=(1-alpha[:,None])*src[y,x].astype(float)+alpha[:,None]*donor
    dst[y,x]=np.clip(np.rint(changed),0,255).astype(src.dtype)
Image.fromarray(dst).save(args.out,optimize=True)
changed_pixels=int(np.any(src!=dst,axis=2).sum())
print('Changed',changed_pixels,'of',h*w,'atlas pixels',f'({100*changed_pixels/(w*h):.2f}%)')
