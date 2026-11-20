from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes

P=Path(__file__).resolve().parent;S=P.parents[2];O=P/'phase-audit'
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
def bg(im):
    canvas=Image.new('RGBA',im.size,(18,24,31,255));canvas.alpha_composite(im.convert('RGBA'));return canvas.convert('RGB')
before=P/'phase-before/baseline';after=P/'renders/baseline'
sheet=Image.new('RGB',(1040,780),(14,19,26));d=ImageDraw.Draw(sheet)
for j,(title,path) in enumerate([('Before shape phase - checkpoint 22',before),('Accepted - checkpoint 33',after)]):
    x=j*520;d.text((x+16,15),title,font=font,fill='white')
    im=bg(Image.open(path/'side-neutral.png')).crop((135,175,465,815)).resize((330,640))
    sheet.paste(im,(x+20,60))
    for k,(crop,y,label_text) in enumerate([((190,365,410,485),100,'Collars'),((140,610,460,810),420,'Base and socket')]):
        detail=bg(Image.open(path/'side-neutral.png')).crop(crop);detail.thumbnail((160,180))
        sheet.paste(detail,(x+355,y+25));d.text((x+350,y),label_text,fill='white')
d.text((20,730),'Same camera, material, neutral lights, physical scale and ground line. No image stretching.',font=font,fill='white')
sheet.save(O/'phase-side-before-after.png')

reg=json.loads((S/'assets/queen/original-reference-alignment.json').read_text());s=reg['scale']
original=Image.open(S/'references/lichess-staunton-3d/Black-Queen.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(1/s,0,-reg['offset_x']/s,0,1/s,-reg['offset_y']/s),Image.Resampling.BILINEAR)
def clean(m):
    lab,count=label(m,np.ones((3,3)));areas=np.bincount(lab.ravel());areas[0]=0;return binary_fill_holes(lab==areas.argmax())
def refmask(im):
    a=np.asarray(im.convert('RGBA'));return clean((a[:,:,3]>127)&(a[:,:,:3].max(2)>12))
refs={'original_black':refmask(original),'selected_highres':refmask(Image.open(S/'assets/queen/reference.png'))}
scores={};full=Image.new('RGB',(1440,760),(14,19,26));dd=ImageDraw.Draw(full)
images=[original,Image.open(before/'fixed-neutral.png'),Image.open(after/'fixed-neutral.png')]
for j,(title,im) in enumerate(zip(['Original black','Before shape phase','Accepted checkpoint 33'],images)):
    dd.text((j*480+15,15),title,font=font,fill='white')
    full.paste(bg(im).crop((195,40,775,1120)).resize((370,689)),(j*480+45,55))
    if j:
        mask=clean(np.asarray(im.convert('RGBA'))[:,:,3]>127)
        scores[title]={name:100*float((mask&r).sum())/float((mask|r).sum()) for name,r in refs.items()}
full.save(O/'phase-fixed-comparison.png')
(O/'phase-neutral-iou.json').write_text(json.dumps(scores,indent=2)+'\n')
print(json.dumps(scores,indent=2))
