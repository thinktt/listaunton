"""Bake a generated unlit color envelope into the actual lathe's static pigment.

The generated image is a material estimate, not acceptance ground truth.
Preserve the original atlas's fine variation and assess a real BSDF render.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from derive_wood import ROOT,linear,display,blur,sample,ramp
from lathe_projection import visible_tiles

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run(cfg):
    src=ROOT/cfg['source'];gen=ROOT/cfg['unlit_image']
    assert digest(src)==cfg['source_sha256'] and digest(gen)==cfg['unlit_sha256']
    pigment=linear(np.asarray(Image.open(src).convert('RGB'),np.float32)/255)
    raw=np.asarray(Image.open(gen).convert('RGB'),np.float32)/255
    assert raw.shape==(1254,1254,3)
    mask=(raw.max(2)>12/255).astype(np.float32)
    density=blur(mask,r=cfg['photo_radius'],passes=2)
    macro=blur(linear(raw)*mask[:,:,None],r=cfg['photo_radius'],passes=2)/np.maximum(density[:,:,None],1e-6)
    median=np.median(macro[density>.99],axis=0)
    # Select true body pigment, excluding nearly black grooves and bright glint
    # residues; this sets reflectance, not the output photograph's exposure.
    valid=(pigment[:,:,0]>.045)&(pigment[:,:,0]<.26)
    color=np.median(pigment[valid],axis=0)
    macro=macro*color/median
    low=blur(pigment,r=cfg['atlas_radius'],passes=2)
    detail=np.clip(pigment/np.maximum(low,.0001),.40,2.4)**cfg.get('detail_strength',1)
    mdir=ROOT/cfg['measurement'];meridian=np.load(mdir/'meridian.npy');depth=np.load(mdir/'depth.npy')[:,:,0]
    camera=json.loads((ROOT/'assets/pawn/camera.json').read_text())
    size=len(pigment);field=np.empty_like(pigment);visibility=np.zeros((size,size),np.float32)
    for rows,_,_,_,px,py,visible in visible_tiles(meridian,depth,camera,size):
        region=sample(macro,px,py)
        valid=sample(density,px,py)
        # The hidden fallback has consistent pigment instead of painted
        # illumination. The object's existing high-frequency grain remains.
        weight=visible*ramp(valid,.75,.98)
        field[rows]=color*(1-weight[:,:,None])+region*weight[:,:,None]
        visibility[rows]=weight
    # Remove only the requested share of the old broad color variation.
    mix=cfg['strength'];new=low**(1-mix)*np.maximum(field,.0001)**mix*detail
    out=ROOT/cfg['output'];out.parent.mkdir(parents=True,exist_ok=True)
    encoded=np.uint8(np.rint(np.clip(display(new),0,1)*255));Image.fromarray(encoded).save(out)
    report={'config':cfg,'source_pigment_median':color.tolist(),'generated_macro_median':median.tolist(),
        'sha256':digest(out),'method':'Static UV color envelope from unlit source; multiplicative original fine detail; real BSDF rendering required.'}
    out.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);a=p.parse_args();run(json.loads(a.config.read_text()))
