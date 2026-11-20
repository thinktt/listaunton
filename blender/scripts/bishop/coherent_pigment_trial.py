"""Infer continuous boxwood tone/fine grain for a joint material-lighting study."""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--capture',required=True);p.add_argument('--atlas',required=True);p.add_argument('--swatch',required=True);p.add_argument('--out',required=True)
a=p.parse_args();out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True);capture=ROOT/a.capture
def read(path):
    ar=np.array(Image.open(path).convert('RGB'),dtype=np.float32)/255
    return np.log(np.maximum(np.where(ar<=.04045,ar/12.92,((ar+.055)/1.055)**2.4),.0001))
old=np.array(Image.open(ROOT/a.atlas).convert('RGBA'));log=read(ROOT/a.atlas);tile=read(ROOT/a.swatch)
coverage=np.clip(np.load(capture/'legacy-coverage.npy')[:,:,0],0,1);visible=np.load(capture/'visible.npy')
valid=np.load(capture/'valid.npy');normal=np.load(capture/'normal.npy')[:,:,:3]*2-1
meta=json.loads((capture/'manifest.json').read_text());view=np.array(meta['view_direction'])
reliable=valid&visible&(coverage>.99)&((normal@view)>.4)
base=np.median(log[reliable],axis=0)
# Retain measured fine markings only well inside the old trusted projection.
# Remove the old broad illumination and do not carry transition-edge residue
# into unseen wood. The generated swatch supplies inferred zero-mean grain.
measured=np.clip(log-blur(log,24,2),-.3,.3)
generated=np.clip(tile-blur(tile,32,2),-.3,.3)
yy,xx=np.indices(valid.shape);u=(xx/2048-.01)/.98
sx=(.5-.49*np.cos(2*np.pi*u))*(tile.shape[1]-1);sy=yy/2047*(tile.shape[0]-1)
lx=np.floor(sx).astype(int);hx=np.minimum(lx+1,tile.shape[1]-1);fx=sx-lx
ly=np.floor(sy).astype(int);hy=np.minimum(ly+1,tile.shape[0]-1);fy=sy-ly
mapped=(generated[ly,lx]*(1-fx[:,:,None])+generated[ly,hx]*fx[:,:,None])*(1-fy[:,:,None])
mapped+=(generated[hy,lx]*(1-fx[:,:,None])+generated[hy,hx]*fx[:,:,None])*fy[:,:,None]
weight=np.clip((coverage-.90)/.10,0,1);weight=weight*weight*(3-2*weight)
result=base+measured*weight[:,:,None]+mapped*(1-weight[:,:,None])*.8
linear=np.exp(result);srgb=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)
new=old.copy();domain=old[:,:,:3].max(2)>5;new[:,:,:3][domain]=np.uint8(np.rint(np.clip(srgb[domain],0,1)*255))
Image.fromarray(new).save(out/'albedo.png')
sheet=Image.new('RGB',(1024,550),'#171b21');draw=ImageDraw.Draw(sheet)
for i,(label,ar) in enumerate([('Accepted pigment',old),('Continuous tone + measured/inferred fine grain',new)]):
    sheet.paste(Image.fromarray(ar).convert('RGB').resize((512,512),Image.Resampling.LANCZOS),(512*i,38));draw.text((512*i+10,12),label,fill='white')
sheet.save(out/'atlas-comparison.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(out/'pigment.json').write_text(json.dumps({'source_atlas':a.atlas,'source_sha256':sha(ROOT/a.atlas),
 'swatch':a.swatch,'swatch_sha256':sha(ROOT/a.swatch),'capture':a.capture,
 'base_linear_rgb':np.exp(base).tolist(),'output_sha256':sha(out/'albedo.png'),
 'method':'Constant robust boxwood base color plus bounded measured high-pass grain in trusted observed interiors and inferred periodic fine grain elsewhere. Broad old shading is removed everywhere. Geometry and references untouched.',
 'status':'Unaccepted joint lighting/material study. Fixed, side and rear BSDF renders determine usefulness.'},indent=2)+'\n')
print('COHERENT_PIGMENT_PREPARED',np.exp(base).tolist())
