"""Infer hidden pigment from a generated swatch without wrapping baked shading.

An isolated material experiment. Original reference pixels are never modified.
Reliable observed pigment is retained; a broad feather substitutes inferred
wood in low-confidence regions. The swatch contributes zero-mean grain only.
"""
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',required=True);p.add_argument('--coverage',required=True)
p.add_argument('--swatch',required=True);p.add_argument('--out',required=True)
p.add_argument('--preserve-from',type=float,default=.98)
p.add_argument('--replace-through',type=float,default=.35)
p.add_argument('--background-rgb',type=float,nargs=3,default=[.2,.08,.015])
p.add_argument('--grain-strength',type=float,default=.7)
a=p.parse_args();out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
def log_image(path):
    ar=np.array(Image.open(path).convert('RGBA'));v=ar[:,:,:3].astype(np.float32)/255
    lin=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
    return ar,np.log(np.maximum(lin,.0001))
old,log=log_image(ROOT/a.source);_,tile=log_image(ROOT/a.swatch)
coverage=np.clip(np.load(ROOT/a.coverage),0,1)
assert coverage.shape==old.shape[:2]==(2048,2048)
# Broad color in the generated image is inferred and not calibrated. Only its
# fine spatial pattern is used, with a separately declared linear base color.
grain=tile-blur(tile,32,2);grain=np.clip(grain,-.35,.35)*a.grain_strength
result=log.copy();weights=np.zeros(coverage.shape,np.float32);regions={}
for name,(v0,v1) in {'body':(.01,.70),'button':(.73,.88)}.items():
    y0,y1=int((1-v1)*2048),int((1-v0)*2048)+1
    x0,x1=int(.01*2048),int(.99*2048)+1;sl=np.s_[y0:y1,x0:x1]
    h,w=coverage[sl].shape
    # Reflecting sample coordinates makes a continuous periodic grain field.
    # Scale gives a physically fine grain at the piece's reference resolution.
    u=np.arange(w)/w;v=np.arange(h)/max(1,h-1)
    tx=(.5-.49*np.cos(2*np.pi*u))*(tile.shape[1]-1)
    ty=v*(tile.shape[0]-1)
    lx=np.floor(tx).astype(int);hx=np.minimum(lx+1,tile.shape[1]-1);fx=tx-lx
    ly=np.floor(ty).astype(int);hy=np.minimum(ly+1,tile.shape[0]-1);fy=ty-ly
    rows=grain[ly]*(1-fy[:,None,None])+grain[hy]*fy[:,None,None]
    mapped=rows[:,lx]*(1-fx[None,:,None])+rows[:,hx]*fx[None,:,None]
    inferred=np.log(np.array(a.background_rgb))[None,None,:]+mapped
    t=np.clip((a.preserve_from-coverage[sl])/(a.preserve_from-a.replace_through),0,1)
    weight=t*t*(3-2*t)
    # Blending full pigment replaces the boundary residue as well as its broad
    # tone. It deliberately does not preserve old high-frequency hidden pixels.
    result[sl]=log[sl]*(1-weight[:,:,None])+inferred*weight[:,:,None]
    weights[sl]=weight
    regions[name]={'preserved':int((weight==0).sum()),'changed':int((weight>0).sum()),'inferred':int((weight==1).sum())}
lin=np.exp(result);rgb=np.where(lin<=.0031308,12.92*lin,1.055*lin**(1/2.4)-.055)
new=old.copy();new[:,:,:3]=np.uint8(np.rint(np.clip(rgb,0,1)*255));new[weights==0]=old[weights==0]
Image.fromarray(new).save(out/'albedo.png');np.save(out/'weights.npy',weights)
Image.fromarray(np.uint8(coverage*255)).resize((768,768)).save(out/'coverage.png')
canvas=Image.new('RGB',(1024,550),'#171b21');d=ImageDraw.Draw(canvas)
for i,(label,ar) in enumerate([('Accepted pigment',old),('Inferred generated grain',new)]):
    canvas.paste(Image.fromarray(ar).convert('RGB').resize((512,512)),(i*512,38));d.text((i*512+10,12),label,fill='white')
canvas.save(out/'atlas-comparison.png')
report={'parameters':vars(a),'regions':regions,'protected_texels_identical':bool(np.array_equal(new[weights==0],old[weights==0])),
 'source_sha256':hashlib.sha256((ROOT/a.source).read_bytes()).hexdigest(),
 'swatch_sha256':hashlib.sha256((ROOT/a.swatch).read_bytes()).hexdigest(),
 'output_sha256':hashlib.sha256((out/'albedo.png').read_bytes()).hexdigest(),
 'status':'Isolated unaccepted generated-grain material interpretation. Requires actual front and rotated BSDF renders.'}
(out/'continuation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
