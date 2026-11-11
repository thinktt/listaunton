"""Finial-only comparisons with unchanged image registration and source pixels."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
HERE=Path(__file__).resolve().parent
ROOT=next((p for p in HERE.parents if (p/'assets/queen').is_dir()),HERE.parent/'queen-profile-019')
A=ROOT/'assets/queen';old=ROOT/'history/queen-mission-021'
sys.path.insert(0,str(ROOT/'scripts/queen'))
from overlay_qa import largest_component,fill_holes
reg=json.loads((A/'original-reference-alignment.json').read_text());s,x,y=reg['scale'],reg['offset_x'],reg['offset_y']
original=Image.open(ROOT/'references/lichess-staunton-3d/Black-Queen.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(1/s,0,-x/s,0,1/s,-y/s),Image.Resampling.BILINEAR)
ref=Image.open(A/'reference.png').convert('RGBA');previous=Image.open(old/'queen-brown.png').convert('RGBA')
trials=[(v,ROOT/'build/queen-mission'/v) for v in sys.argv[1:]]
font_path=next(p for p in ['C:/Windows/Fonts/segoeui.ttf','/mnt/c/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'] if Path(p).exists())
font=ImageFont.truetype(font_path,21)
def rgb(im):return Image.alpha_composite(Image.new('RGBA',im.size,(0,0,0,255)),im.convert('RGBA')).convert('RGB')
def sheet(items,path,box,width):
    h=round(width*(box[3]-box[1])/(box[2]-box[0]));out=Image.new('RGB',(len(items)*(width+12)+12,h+58),(22,25,30));d=ImageDraw.Draw(out)
    for i,(label,im) in enumerate(items):
        xx=12+i*(width+12);d.text((xx,12),label,font=font,fill='white');out.paste(rgb(im).crop(box).resize((width,h),Image.Resampling.LANCZOS),(xx,48))
    out.save(path)
wood=[('Original',original),('Selected high-res',ref),('Accepted 21',previous)]+[(v,Image.open(p/'wood.png')) for v,p in trials]
sheet(wood,HERE/'finial-comparison.png',(410,135,558,292),400)
sheet(wood,HERE/'crown-comparison.png',(310,50,665,355),400)
side=[('Accepted 21',Image.open(old/'queen-finished-profile.png'))]+[(v,Image.open(p/'side-clay.png')) for v,p in trials if (p/'side-clay.png').exists()]
sheet(side,HERE/'side-crown.png',(200,172,400,370),460)
def mask(im,reference=False):
    a=np.asarray(im.convert('RGBA'));m=a[:,:,3]>127
    if reference:m&=a[:,:,:3].max(2)>12
    return fill_holes(largest_component(m))
original_mask=mask(original,True);selected_mask=mask(ref,True)
previous_alpha=np.asarray(previous)[:,:,3];previous_mask=mask(previous)
report={}
for variant,im in [('accepted-21',previous)]+[(v,Image.open(p/'wood.png')) for v,p in trials]:
    record={}
    silhouette=previous_mask if np.array_equal(np.asarray(im.convert('RGBA'))[:,:,3],previous_alpha) else mask(im)
    for label,source_mask in [('original',original_mask),('highres',selected_mask)]:
        record[label+'_iou']=float((silhouette&source_mask).sum()/(silhouette|source_mask).sum())
    for label,source in [('original',original),('highres',ref)]:
        for region,box in [('finial',(424,147,546,282)),('contact',(420,246,550,291)),('bowl',(385,115,580,320))]:
            left,top,right,bottom=box
            a=np.asarray(rgb(source).filter(ImageFilter.GaussianBlur(2)),dtype=float)[top:bottom,left:right]
            b=np.asarray(rgb(im).filter(ImageFilter.GaussianBlur(2)),dtype=float)[top:bottom,left:right]
            record[label+'_'+region+'_rgb_mse']=float(np.mean((a-b)**2))
    report[variant]=record
    if variant!='accepted-21' and (ROOT/'build/queen-mission'/variant/'controls.npz').exists():
        data=np.load(ROOT/'build/queen-mission'/variant/'controls.npz')
        for key in ['before','after']:
            arr=data[key];tip=float(arr[90:101,:,2].max());egg=float(arr[108:,:,2].max())
            record[key+'_egg_tip_height_difference']=egg-tip
(HERE/'metrics.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
