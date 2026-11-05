"""Infer unseen wood from a front strip, replacing both tone and boundary residue."""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--coverage',required=True);p.add_argument('--out',required=True)
p.add_argument('--center',type=float,default=.39);p.add_argument('--amplitude',type=float,default=.05)
p.add_argument('--preserve-from',type=float,default=.98);p.add_argument('--replace-through',type=float,default=.6)
a=p.parse_args();assert 0<=a.replace_through<a.preserve_from<=1
source=ROOT/a.source;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
old=np.array(Image.open(source).convert('RGBA'));rgb=old[:,:,:3].astype(np.float32)/255
linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
confidence=np.clip(np.load(ROOT/a.coverage),0,1);result=linear.copy();weights=np.zeros(confidence.shape,np.float32);records={}
for name,(v0,v1) in {'body':(.01,.70),'button':(.73,.88)}.items():
    y0,y1=int((1-v1)*2048),int((1-v0)*2048)+1;x0,x1=int(.01*2048),int(.99*2048)+1;sl=np.s_[y0:y1,x0:x1]
    ar=linear[sl];coverage=confidence[sl];h,w=coverage.shape;u=np.linspace(0,1,w)
    donor_u=a.center+a.amplitude*np.cos(2*np.pi*u)
    donor_x=donor_u*(w-1);lo=np.floor(donor_x).astype(int);hi=np.minimum(lo+1,w-1);fraction=donor_x-lo
    donor=ar[:,lo]*(1-fraction[None,:,None])+ar[:,hi]*fraction[None,:,None]
    # Source strips are artistic continuation. Protect reliable observed pixels
    # exactly, and remove old boundary residue in low-confidence blend regions.
    t=np.clip((a.preserve_from-coverage)/(a.preserve_from-a.replace_through),0,1)
    weight=t*t*(3-2*t);result[sl]=ar*(1-weight[:,:,None])+donor*weight[:,:,None];weights[sl]=weight
    records[name]={'preserved_texels':int((weight==0).sum()),'edited_texels':int((weight>0).sum()),
        'fully_replaced_texels':int((weight>=1).sum()),'sampled_confidence_mean':float(coverage[:,lo].mean()),
        'source_strip_u':[a.center-a.amplitude,a.center+a.amplitude]}
srgb=np.where(result<=.0031308,12.92*result,1.055*np.power(np.maximum(result,0),1/2.4)-.055)
new=old.copy();new[:,:,:3]=np.uint8(np.rint(np.clip(srgb,0,1)*255));new[weights==0]=old[weights==0]
assert np.array_equal(new[weights==0],old[weights==0]);Image.fromarray(new).save(out/'albedo.png');np.save(out/'weights.npy',weights)
canvas=Image.new('RGB',(1024,550),'#171b21');d=ImageDraw.Draw(canvas)
for i,(label,ar) in enumerate([('Accepted pigment',old),('Inferred continuation from front wood',new)]):
    canvas.paste(Image.fromarray(ar).convert('RGB').resize((512,512)),(512*i,38));d.text((512*i+10,12),label,fill='white')
canvas.save(out/'atlas-comparison.png')
report={'source':a.source,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'coverage':a.coverage,'coverage_sha256':hashlib.sha256((ROOT/a.coverage).read_bytes()).hexdigest(),
 'output_sha256':hashlib.sha256((out/'albedo.png').read_bytes()).hexdigest(),'parameters':vars(a),'regions':records,
 'protected_texels_identical':True,'method':'Smooth periodic sampling of a front strip at the same meridian coordinate. Replace low-confidence pigment, including fine boundary residue, while preserving high-confidence texels exactly.',
 'limits':'Unseen grain is an interpretation. Possible repeated markings and wrapped shading must be judged in real fixed and rotated BSDF renders.'}
(out/'continuation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
