"""Combine harmonic broad pigment with clean sampled grain in transition regions."""
import argparse,json,hashlib,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--broad-trial',required=True);p.add_argument('--donor-trial',required=True);p.add_argument('--out',required=True)
a=p.parse_args();out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
def read(path):
    ar=np.array(Image.open(path).convert('RGBA'));rgb=ar[:,:,:3].astype(np.float32)/255
    lin=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4);return ar,np.log(np.maximum(lin,.0001))
original,log=read(ROOT/a.source);broad_ar,harmonic=read(ROOT/a.broad_trial/'albedo.png');_,donor=read(ROOT/a.donor_trial/'albedo.png')
weights=np.load(ROOT/a.donor_trial/'weights.npy');result=harmonic.copy()
for v0,v1 in [(.01,.70),(.73,.88)]:
    y0,y1=int((1-v1)*2048),int((1-v0)*2048)+1;x0,x1=int(.01*2048),int(.99*2048)+1;sl=np.s_[y0:y1,x0:x1]
    old_fine=log[sl]-blur(log[sl],8,2)
    # The harmonic trial carried 80% of the old fine signal in hidden texels.
    broad_weight=np.load(ROOT/a.broad_trial/'hidden-weight.npy')[sl]
    old_contribution=old_fine*(1-.2*broad_weight[:,:,None])
    clean_fine=np.clip(donor[sl]-blur(donor[sl],20,2),-.22,.22)
    w=weights[sl][:,:,None]
    result[sl]=harmonic[sl]+w*(clean_fine-old_contribution)
lin=np.exp(result);rgb=np.where(lin<=.0031308,12.92*lin,1.055*np.power(lin,1/2.4)-.055)
new=original.copy();new[:,:,:3]=np.uint8(np.rint(np.clip(rgb,0,1)*255));new[weights==0]=original[weights==0]
Image.fromarray(new).save(out/'albedo.png')
canvas=Image.new('RGB',(1024,550),'#171b21');d=ImageDraw.Draw(canvas)
for i,(label,ar) in enumerate([('Accepted pigment',original),('Continuous broad color plus sampled fine grain',new)]):
    canvas.paste(Image.fromarray(ar).convert('RGB').resize((512,512)),(i*512,38));d.text((i*512+10,12),label,fill='white')
canvas.save(out/'atlas-comparison.png')
report={'parameters':vars(a),'source_sha256':hashlib.sha256((ROOT/a.source).read_bytes()).hexdigest(),
 'output_sha256':hashlib.sha256((out/'albedo.png').read_bytes()).hexdigest(),'protected_texels_identical':bool(np.array_equal(new[weights==0],original[weights==0])),
 'method':'Remove the old transition-region high-frequency residue from the harmonic trial. Substitute bounded sampled fine grain, without propagating donor broad shadow bands. Interpretive isolated material trial.'}
(out/'continuation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
