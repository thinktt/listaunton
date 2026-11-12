from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes
P=Path(__file__).resolve().parent;S=P.parents[2]
configs=[{'variant':'baseline'}]+json.loads((P/'socket-shelf-studies.json').read_text())
reg=json.loads((S/'assets/queen/original-reference-alignment.json').read_text());s=reg['scale']
original=Image.open(S/'references/lichess-staunton-3d/Black-Queen.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(1/s,0,-reg['offset_x']/s,0,1/s,-reg['offset_y']/s),Image.Resampling.BILINEAR)
def clean(m):
    ids,count=label(m,np.ones((3,3)));areas=np.bincount(ids.ravel());areas[0]=0;return binary_fill_holes(ids==areas.argmax())
def mask(im):
    a=np.asarray(im.convert('RGBA'));return clean((a[:,:,3]>127)&(a[:,:,:3].max(2)>12))
def bg(im):
    out=Image.new('RGBA',im.size,(18,24,31,255));out.alpha_composite(im.convert('RGBA'));return out.convert('RGB')
refs={'original':mask(original),'selected':mask(Image.open(S/'assets/queen/reference.png'))}
sheet=Image.new('RGB',(1200,990),(15,20,26));d=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
scores=[]
for j,cfg in enumerate(configs):
    tag=cfg['variant'];fixed=Image.open(P/'renders'/tag/'fixed-neutral.png').convert('RGBA');side=Image.open(P/'renders'/tag/'side-neutral.png')
    d.text((j*400+10,12),tag,font=font,fill='white')
    sheet.paste(bg(side).crop((145,570,455,810)).resize((400,310)),(j*400,50))
    sheet.paste(bg(fixed).crop((315,610,650,890)).resize((400,334)),(j*400,390))
    m=clean(np.asarray(fixed)[:,:,3]>127);sc={name:100*float((m&r).sum())/float((m|r).sum()) for name,r in refs.items()}
    scores.append({'variant':tag,'silhouette_iou_percent':sc})
    d.text((j*400+10,740),f"Original {sc['original']:.4f}% | selected {sc['selected']:.4f}%",fill='white')
    sheet.paste(bg(original).crop((345,660,625,880)).resize((280,220)),(j*400+60,770))
sheet.save(P/'neutral-shelf-comparison.png')
(P/'neutral-shelf-scores.json').write_text(json.dumps(scores,indent=2)+'\n');print(json.dumps(scores,indent=2))
