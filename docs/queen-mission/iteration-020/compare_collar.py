"""Fixed-camera collar evidence, with the original as the primary comparison."""
import sys,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
HERE=Path(__file__).resolve().parent
ROOT=next((p for p in HERE.parents if (p/'assets/queen').is_dir()),HERE.parent/'queen-profile-019');A=ROOT/'assets/queen'
sys.path.insert(0,str(ROOT/'scripts/queen'))
from overlay_qa import largest_component,fill_holes
reg=json.loads((A/'original-reference-alignment.json').read_text());s,x,y=reg['scale'],reg['offset_x'],reg['offset_y']
original=Image.open(ROOT/'references/lichess-staunton-3d/Black-Queen.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(1/s,0,-x/s,0,1/s,-y/s),Image.Resampling.BILINEAR)
selected=Image.open(A/'reference.png').convert('RGBA');baseline=Image.open(ROOT/'history/queen-mission-019/queen-brown.png').convert('RGBA')
font_path=next(p for p in ['C:/Windows/Fonts/segoeui.ttf','/mnt/c/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'] if Path(p).exists())
font=ImageFont.truetype(font_path,20)
def black(im):return Image.alpha_composite(Image.new('RGBA',im.size,(0,0,0,255)),im.convert('RGBA')).convert('RGB')
def mask(im,ref=False):
    a=np.asarray(im.convert('RGBA'));m=a[:,:,3]>127
    if ref:m&=a[:,:,:3].max(2)>12
    return fill_holes(largest_component(m))
def iou(a,b):return float((a&b).sum()/(a|b).sum())
def sheet(items,path,box,width):
    h=round(width*(box[3]-box[1])/(box[2]-box[0]));out=Image.new('RGB',((width+12)*len(items)+12,h+55),(22,25,31));d=ImageDraw.Draw(out)
    for i,(label,im) in enumerate(items):
        xx=12+i*(width+12);d.text((xx,10),label,font=font,fill='white');out.paste(black(im).crop(box).resize((width,h),Image.Resampling.LANCZOS),(xx,44))
    out.save(path)
trials=[(v,ROOT/'build/queen-mission'/v) for v in sys.argv[1:]]
items=[('Original Lichess',original),('Selected high-res',selected),('Accepted 19',baseline)]+[(v,Image.open(p/'wood.png').convert('RGBA')) for v,p in trials]
sheet(items,HERE/'collar-fixed.png',(300,340,670,565),400)
side=[('Accepted 19',Image.open(ROOT/'history/queen-mission-019/queen-finished-profile.png'))]+[(v,Image.open(p/'side-clay.png')) for v,p in trials]
sheet(side,HERE/'collar-side.png',(195,325,405,495),480)
sheet(side,HERE/'profile-full.png',(125,170,475,815),300)
O=mask(original,True);H=mask(selected,True);report={}
for v,im in [('accepted-19',baseline)]+[(v,Image.open(p/'wood.png').convert('RGBA')) for v,p in trials]:
    M=mask(im);row={'original_iou':iou(O,M),'highres_iou':iou(H,M)}
    for label,ref,R in [('original',original,O),('highres',selected,H)]:
        a=np.asarray(black(ref).filter(ImageFilter.GaussianBlur(3)),dtype=float);b=np.asarray(black(im).filter(ImageFilter.GaussianBlur(3)),dtype=float)
        valid=(R&M)[360:565,300:670];row[label+'_collar_rgb_mse']=float(((a-b)**2)[360:565,300:670][valid].mean())
    report[v]=row
(HERE/'metrics.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
