"""Rook evidence at fixed registration, with the set mission mask convention."""
from pathlib import Path
import argparse, hashlib, json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/queen'))
from overlay_qa import largest_component, fill_holes, contour

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def black(im):return Image.alpha_composite(Image.new('RGBA',im.size,(0,0,0,255)),im).convert('RGB')
def mask(im,reference=False):
    a=np.asarray(im);m=a[:,:,3]>127
    if reference:m=m&(a[:,:,:3].max(2)>12)
    return fill_holes(largest_component(m))
def iou(a,b):return float((a&b).sum()/(a|b).sum())
def audit(render,previous,out,model=None):
    out.mkdir(parents=True,exist_ok=True)
    reference=Image.open(ROOT/'assets/rook/ref.png').convert('RGBA')
    trial=Image.open(render).convert('RGBA');prior=Image.open(previous).convert('RGBA')
    assert trial.size==reference.size==prior.size
    reg=json.loads((ROOT/'assets/rook/original-alignment.json').read_text());s,x,y=(reg[k] for k in ('scale','x','y'));W=reference.width
    original=Image.open(ROOT/'assets/rook/original.png').convert('RGBA').transform(reference.size,Image.Transform.AFFINE,(s*300/W,0,x*3,0,s*300/W,y*3),Image.Resampling.BILINEAR)
    fontpath=next((p for p in ['C:/Windows/Fonts/segoeui.ttf','/mnt/c/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'] if Path(p).exists()),None)
    font=ImageFont.truetype(fontpath,19) if fontpath else ImageFont.load_default(size=19)
    for name,box,w in [('full',(190,230,780,1100),420),('turret',(290,260,680,625),500),('shaft',(315,575,665,845),500),('shoulder',(260,745,720,925),450),('base',(195,800,805,1110),500)]:
        h=round((box[3]-box[1])*w/(box[2]-box[0]));sheet=Image.new('RGB',(3*w+40,h+48),(22,24,28));d=ImageDraw.Draw(sheet)
        for k,(title,im) in enumerate([('High-res reference',reference),('Previous accepted / baseline',prior),('Rook trial',trial)]):
            d.text((10+k*(w+10),8),title,font=font,fill='#eeeae5');sheet.paste(black(im).crop(box).resize((w,h),Image.Resampling.LANCZOS),(10+k*(w+10),40))
        sheet.save(out/(name+'-comparison.png'))
    A=mask(reference,True);O=mask(original,True);B=mask(trial);P=mask(prior)
    report={'mask_convention':'max RGB >12 and alpha >127, largest component and holes filled; model alpha >127', 'highres_iou':iou(A,B),'original_iou':iou(O,B),'previous_highres_iou':iou(A,P),'previous_original_iou':iou(O,P),'regional_iou':{},'render_sha256':sha(render),'reference_sha256':sha(ROOT/'assets/rook/ref.png'),'original_sha256':sha(ROOT/'assets/rook/original.png'),'previous_sha256':sha(previous)}
    if model:report['model_sha256']=sha(model)
    for name,lo,hi in [('turret',260,625),('shaft',625,810),('shoulder',810,925),('base-foot',925,1100)]:report['regional_iou'][name]={'previous':iou(A[lo:hi],P[lo:hi]),'trial':iou(A[lo:hi],B[lo:hi])}
    for name,im,m in [('highres',reference,A),('original',original,O)]:
        Image.blend(black(im),black(trial),.5).save(out/('overlay-'+name+'.png'))
        ar=np.asarray(black(im)).copy();ar=(ar*.6).astype(np.uint8);ar[contour(m)]=(50,225,244);ar[contour(B)]=(255,76,215);Image.fromarray(ar).save(out/('contour-'+name+'.png'))
    (out/'metrics.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('variant');p.add_argument('--render');p.add_argument('--previous',default='assets/rook/render.png');args=p.parse_args()
    out=ROOT/'build/rook-mission'/args.variant
    audit(ROOT/args.render if args.render else out/'wood.png',ROOT/args.previous,out,out/'rook.blend' if (out/'rook.blend').exists() else None)
