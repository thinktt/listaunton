"""Fixed-registration mission evidence. Masks follow MISSION-BISHOP.md."""
from pathlib import Path
import argparse, collections, hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--render',required=True);p.add_argument('--out',required=True);p.add_argument('--previous');a=p.parse_args()
out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
ref=Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA');W=ref.width
ren=Image.open(ROOT/a.render).convert('RGBA');assert ren.size==ref.size
def source(name,alignment):
    q=json.loads((ROOT/'assets/bishop'/alignment).read_text());s=q['scale']*300/W
    return Image.open(ROOT/'assets/bishop'/name).convert('RGBA').transform((W,W),Image.Transform.AFFINE,(s,0,q['x']*3,0,s,q['y']*3),Image.Resampling.BILINEAR)
original=source('original.png','original-alignment.json');black=source('black-original.png','black-alignment.json')
def mask(im):
    ar=np.array(im);m=(ar[:,:,3]>127)&(ar[:,:,:3].max(2)>12)
    # Run-length connected components, 4-connectivity, then fill enclosed holes.
    parent=[];sizes=[];rows=[];last=[]
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for yy,row in enumerate(m):
        e=np.diff(np.r_[False,row,False].astype(np.int8));runs=list(zip(np.where(e==1)[0],np.where(e==-1)[0]));current=[]
        j=0
        for start,end in runs:
            idx=len(parent);parent.append(idx);sizes.append(int(end-start));current.append((start,end,idx));rows.append((yy,start,end,idx))
            while j<len(last) and last[j][1]<=start:j+=1
            k=j
            while k<len(last) and last[k][0]<end:
                x,y=find(idx),find(last[k][2])
                if x!=y:parent[y]=x;sizes[x]+=sizes[y]
                k+=1
        last=current
    largest=max(range(len(parent)),key=lambda i:sizes[i] if find(i)==i else 0)
    clean=np.zeros_like(m)
    for yy,start,end,idx in rows:
        if find(idx)==largest:clean[yy,start:end]=True
    flood=Image.fromarray((clean*255).astype('uint8')).copy();ImageDraw.floodfill(flood,(0,0),128)
    return np.array(flood)!=128
bm=np.array(ren)[:,:,3]>127
report={'mask':'reference max RGB >12 and alpha >127; largest 4-connected component; holes filled. Model alpha >127. No alignment search or warping.','render':a.render,'render_sha256':hashlib.sha256((ROOT/a.render).read_bytes()).hexdigest(),'images':{}}
for label,im in [('selected',ref),('original_white',original),('original_black',black)]:
    m=mask(im);report['images'][label]={'silhouette_iou':float((m&bm).sum()/(m|bm).sum())}
    canvas=np.array(im)[:,:,:3].copy()//2
    edge=m&~(np.roll(m,1,0)&np.roll(m,-1,0)&np.roll(m,1,1)&np.roll(m,-1,1));be=bm&~(np.roll(bm,1,0)&np.roll(bm,-1,0)&np.roll(bm,1,1)&np.roll(bm,-1,1))
    canvas[edge]=(50,225,255);canvas[be]=(255,75,185);Image.fromarray(canvas).save(out/(label+'-contours.png'))
def tile(im,box=None,size=500):
    if box:im=im.crop(box)
    im=im.copy();im.thumbnail((size,size),Image.Resampling.LANCZOS)
    bg=Image.new('RGB',(size,size),'#090b0d');bg.paste(im,((size-im.width)//2,(size-im.height)//2),im if im.mode=='RGBA' else None);return bg
def sheet(name,box=None):
    ims=[('Original white',original),('Selected white 3',ref),('Current render',ren)]
    if a.previous:ims.insert(2,('Previous',Image.open(ROOT/a.previous).convert('RGBA')))
    canvas=Image.new('RGB',(len(ims)*500,535),'#171b21');d=ImageDraw.Draw(canvas)
    for i,(label,im) in enumerate(ims):canvas.paste(tile(im,box),(500*i,35));d.text((500*i+15,10),label,fill='white')
    canvas.save(out/name)
sheet('comparison.png');sheet('head.png',(285,135,690,610));sheet('stem-socket.png',(300,535,690,865));sheet('base.png',(165,670,805,1140))
Image.blend(ref,ren,.5).save(out/'overlay-selected.png');Image.blend(original,ren,.5).save(out/'overlay-original.png')
(out/'metrics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
