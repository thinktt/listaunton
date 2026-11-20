"""Produce fixed-registration evidence for current profile studies."""
from pathlib import Path
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts/queen'))
from overlay_qa import largest_component, fill_holes
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',21)
assets=ROOT/'assets/queen';reg=json.loads((assets/'original-reference-alignment.json').read_text())
t,dx,dy=reg['scale'],reg['offset_x'],reg['offset_y']
original=Image.open(ROOT/'references/lichess-staunton-3d/Black-Queen.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(1/t,0,-dx/t,0,1/t,-dy/t),Image.Resampling.BILINEAR)
highres=Image.open(assets/'reference.png').convert('RGBA')
baseline=Image.open(assets/'queen-brown.png').convert('RGBA')
def black(im):return Image.alpha_composite(Image.new('RGBA',im.size,(0,0,0,255)),im.convert('RGBA')).convert('RGB')
def mask(im,ref=False):
    a=np.asarray(im.convert('RGBA'));m=a[:,:,3]>127
    if ref:m&=a[:,:,:3].max(2)>12
    return fill_holes(largest_component(m))
def iou(a,b):return float((a&b).sum()/(a|b).sum())
def sheet(items,path,box,width=420):
    h=round((box[3]-box[1])*width/(box[2]-box[0]));out=Image.new('RGB',(len(items)*(width+12)+12,h+54),(24,27,33));d=ImageDraw.Draw(out)
    for i,(label,img) in enumerate(items):
        x=12+i*(width+12);d.text((x,9),label,font=font,fill='white');out.paste(black(img).crop(box).resize((width,h),Image.Resampling.LANCZOS),(x,45))
    out.save(path)
variants=sys.argv[1:];trials=[(v,ROOT/'build/queen-mission'/v) for v in variants]
fixed=[('Original',original),('Accepted 18',baseline)]+[(v,Image.open(p/'wood.png')) for v,p in trials]
sheet(fixed,ROOT/'fixed-grid.png',(180,30,790,1110),330)
sheet(fixed,ROOT/'base-grid.png',(190,550,780,1095),420)
side=[('Accepted 18',Image.open(assets/'queen-finished-profile.png'))]+[(v,Image.open(p/'side-clay.png')) for v,p in trials]
sheet(side,ROOT/'side-grid.png',(125,160,475,820),290)
report={};O=mask(original,True);H=mask(highres,True)
for name,im in [('accepted-18',baseline)]+[(v,Image.open(p/'wood.png')) for v,p in trials]:
    M=mask(im);b=black(im).filter(ImageFilter.GaussianBlur(3));row={'original_iou':iou(O,M),'highres_iou':iou(H,M)}
    for ref,R,label in [(original,O,'original'),(highres,H,'highres')]:
        a=black(ref).filter(ImageFilter.GaussianBlur(3));err=(np.asarray(a).astype(float)-np.asarray(b).astype(float))**2
        for region,box in [('base',(190,550,780,1095)),('whole',(180,30,790,1110))]:
            x0,y0,x1,y1=box;valid=(R&M)[y0:y1,x0:x1];row[f'{label}_{region}_rgb_mse']=float(err[y0:y1,x0:x1][valid].mean())
    report[name]=row
(ROOT/'study-metrics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
