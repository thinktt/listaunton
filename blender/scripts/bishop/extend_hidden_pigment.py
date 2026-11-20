"""Extend compatible turned-wood color around unseen UVs, preserving protected texels."""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--visibility',required=True);p.add_argument('--out',required=True);p.add_argument('--blend-width',type=int,default=64)
p.add_argument('--tone-mode',choices=['profile','global'],default='profile')
p.add_argument('--visibility-threshold',type=float,default=.002)
p.add_argument('--preserve-dilation',type=int,default=8)
a=p.parse_args();source=ROOT/a.source;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
original=np.array(Image.open(source).convert('RGBA'));rgb=original[:,:,:3].astype(np.float32)/255
linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
log=np.log(np.maximum(linear,.0001));visible=np.load(ROOT/a.visibility)
assert visible.shape==original.shape[:2]==(2048,2048)
result=log.copy();weight_image=np.zeros(visible.shape,dtype=np.float32);protected_image=np.zeros(visible.shape,dtype=bool);records={}

def grow(mask):
    up=np.r_[mask[:1],mask[:-1]];down=np.r_[mask[1:],mask[-1:]]
    return mask|np.roll(mask,1,axis=1)|np.roll(mask,-1,axis=1)|up|down

for name,(v0,v1) in {'body':(.01,.70),'button':(.73,.88)}.items():
    y1,y2=int((1-v1)*2048),int((1-v0)*2048)+1;x1,x2=int(.01*2048),int(.99*2048)+1
    sl=np.s_[y1:y2,x1:x2];old=log[sl];mask=visible[sl]>a.visibility_threshold
    protected=mask.copy()
    for _ in range(a.preserve_dilation):protected=grow(protected)
    # Obtain regional wood pigment from well-seen central surface, not a dark
    # procedural edge. Unknown azimuths remain artistic interpretation.
    front=visible[sl]>.95
    front[:,:front.shape[1]//4]=False;front[:,3*front.shape[1]//4:]=False
    rows=np.full((old.shape[0],3),np.nan,dtype=np.float32)
    for y in range(len(rows)):
        if front[y].sum()>8:rows[y]=np.median(old[y,front[y]],axis=0)
    good=np.isfinite(rows[:,0]);assert good.any()
    for c in range(3):rows[:,c]=np.interp(np.arange(len(rows)),np.flatnonzero(good),rows[good,c])
    rows=blur(rows[:,None,:],radius=8,passes=2)[:,0,:]
    if a.tone_mode=='global':rows[:]=np.quantile(old[front],.7,axis=0)
    fine=old-blur(old,radius=8,passes=2)
    target=rows[:,None,:]+.8*fine
    # Smoothly enter the unknown region, with zero edits on protected texels.
    field=protected.copy();distance=np.zeros(mask.shape,dtype=np.float32)
    for _ in range(a.blend_width):
        distance+=(~field)/a.blend_width;field=grow(field)
    weight=distance*distance*(3-2*distance);weight[protected]=0
    result[sl]=old+(target-old)*weight[:,:,None]
    weight_image[sl]=weight;protected_image[sl]=protected
    records[name]={'protected_texels':int(protected.sum()),'edited_texels':int((weight>0).sum()),'median_log_rgb':np.median(rows,axis=0).tolist()}
value=np.exp(result);srgb=np.where(value<=.0031308,12.92*value,1.055*np.power(value,1/2.4)-.055)
new=original.copy();new[:,:,:3]=np.uint8(np.rint(np.clip(srgb,0,1)*255))
# Quantization must not alter even a single protected source pixel.
new[weight_image==0]=original[weight_image==0]
assert np.array_equal(new[protected_image],original[protected_image])
Image.fromarray(new).save(out/'albedo.png');np.save(out/'hidden-weight.npy',weight_image)
canvas=Image.new('RGB',(1024,550),'#171b21');d=ImageDraw.Draw(canvas)
for i,(title,array) in enumerate([('Previous atlas',original),('Hidden wood continuation',new)]):
    canvas.paste(Image.fromarray(array).convert('RGB').resize((512,512)),(i*512,38));d.text((i*512+10,10),title,fill='white')
canvas.save(out/'atlas-comparison.png')
record={'source':a.source,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'visibility':a.visibility,'output_sha256':hashlib.sha256((out/'albedo.png').read_bytes()).hexdigest(),'blend_width_texels':a.blend_width,'protected_texels_unchanged':True,'regions':records,'method':'Robust per-meridian visible pigment color, existing fine procedural grain, smooth continuation only into conservatively hidden texels. No source reference pixels are modified.','caveat':'Unseen grain is inferred. Rendered fixed-view comparison is still required because indirect illumination can change.'}
record.update({'tone_mode':a.tone_mode,'visibility_threshold':a.visibility_threshold,'preserve_dilation':a.preserve_dilation})
if a.tone_mode=='global':record['method']='Use a single robust amber pigment color per component (70th percentile of well-seen pigment) with the existing fine grain. This avoids propagating reference-view shadow bands around the rear. Blend outside the declared protection mask; verify any grazing-view effect in the actual render.'
(out/'parameters.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
