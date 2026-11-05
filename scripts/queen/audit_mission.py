"""Fixed-coordinate image evidence; never refits or modifies source images."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from overlay_qa import largest_component,fill_holes
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('variant');p.add_argument('--previous-image',default='assets/queen/queen-brown.png');args=p.parse_args()
out=root/'build/queen-mission'/args.variant
reference=Image.open(root/'assets/queen/reference.png').convert('RGBA')
previous_path=root/args.previous_image
previous=Image.open(previous_path).convert('RGBA')
trial=Image.open(out/'wood.png').convert('RGBA')
def black(im):return Image.alpha_composite(Image.new('RGBA',im.size,(0,0,0,255)),im).convert('RGB')
fontpath=next((p for p in ['C:/Windows/Fonts/segoeui.ttf','/mnt/c/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'] if Path(p).exists()),None)
font=ImageFont.truetype(fontpath,20) if fontpath else ImageFont.load_default(size=20)
labels=['High-res reference','Previous accepted model','Trial '+args.variant]
images=[black(reference),black(previous),black(trial)]
for name,box,w in [('full',(180,30,790,1110),420),('crown',(300,45,675,365),500),('collars',(290,310,680,580),500),('socket',(310,530,660,880),450),('base',(190,800,780,1095),550)]:
 h=round((box[3]-box[1])*w/(box[2]-box[0]));sheet=Image.new('RGB',(3*w+40,h+55),(22,24,28));d=ImageDraw.Draw(sheet)
 for i,im in enumerate(images):
  x=10+i*(w+10);d.text((x+3,8),labels[i],font=font,fill='#eeeae5');sheet.paste(im.crop(box).resize((w,h),Image.Resampling.LANCZOS),(x,45))
 sheet.save(out/(name+'-comparison.png'))
def refmask(im):
 a=np.array(im);return fill_holes(largest_component((a[:,:,3]>127)&(a[:,:,:3].max(2)>12)))
def mmask(im):return fill_holes(largest_component(np.array(im)[:,:,3]>127))
def iou(a,b):return float((a&b).sum()/(a|b).sum())
reg=json.loads((root/'assets/queen/original-reference-alignment.json').read_text());s=reg['scale'];dx=reg['offset_x'];dy=reg['offset_y']
original=Image.open(root/'references/lichess-staunton-3d/Black-Queen.png').convert('RGBA').transform(reference.size,Image.Transform.AFFINE,(1/s,0,-dx/s,0,1/s,-dy/s),Image.Resampling.BILINEAR)
Image.blend(black(reference),black(trial),.5).save(out/'overlay-highres.png')
Image.blend(black(original),black(trial),.5).save(out/'overlay-original.png')
sheet=Image.new('RGB',(1300,799),(22,24,28));d=ImageDraw.Draw(sheet)
for i,(label,im) in enumerate([('Lichess original',original),('High-res reference',reference),('Trial '+args.variant,trial)]):
 x=10+i*430;d.text((x+3,8),label,font=font,fill='#eeeae5');sheet.paste(black(im).crop((180,30,790,1110)).resize((420,744),Image.Resampling.LANCZOS),(x,45))
sheet.save(out/'original-comparison.png')
A=refmask(reference);O=refmask(original);B=mmask(trial);P=mmask(previous)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stats={'highres_iou':iou(A,B),'original_iou':iou(O,B),'previous_highres_iou':iou(A,P),'previous_original_iou':iou(O,P),'regional_iou':{},'trial_blend_sha256':digest(out/'queen.blend'),'trial_render_sha256':digest(out/'wood.png'),'reference_sha256':digest(root/'assets/queen/reference.png'),'previous_image':args.previous_image,'previous_image_sha256':digest(previous_path)}
for name,lo,hi in [('crown',45,360),('body-collars',360,570),('stem-socket',570,850),('base-foot',850,1095)]:stats['regional_iou'][name]={'previous':iou(A[lo:hi],P[lo:hi]),'trial':iou(A[lo:hi],B[lo:hi])}
(out/'metrics.json').write_text(json.dumps(stats,indent=2))
print(json.dumps(stats,indent=2))
