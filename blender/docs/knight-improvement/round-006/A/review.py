"""Review the two sculptures in the same registered cameras and shared studio."""
from pathlib import Path
import json
import sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont

sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];A=ROOT/'assets/knight'
sys.path.insert(0,str(ROOT/'scripts/knight'))
from audit_mission import silhouette,iou
from overlay_qa import font


def load(p):return Image.open(p).convert('RGBA')


def put(sheet,p,box,pos,size,label):
    im=load(p) if isinstance(p,Path) else p
    im=im.crop(box) if box else im.copy()
    w,h=size
    ratio=min((w-4)/im.width,(h-24)/im.height)
    im=im.resize((int(ratio*im.width),int(ratio*im.height)),Image.Resampling.LANCZOS)
    x,y=pos
    sheet.paste(im,(x+(w-im.width)//2,y+23),im)
    ImageDraw.Draw(sheet).text((x+4,y),label,font=font(16),fill='#eeeeea')


def main():
    ref=load(A/'ref.png')
    old=load(A/'render.png');new=load(OUT/'wood.png')
    ac=json.loads((A/'original-alignment.json').read_text());k=ac['scale']*300/1254
    sprite=load(A/'original.png').transform(ref.size,Image.Transform.AFFINE,
               (k,0,ac['x']*3,0,k,ac['y']*3),Image.Resampling.BILINEAR)
    # Matched wood uses all 26 parent lights and original light-link sets.
    modes=[('parent clay',OUT/'parent-fixed-clay.png',OUT/'parent-side-clay.png'),
           ('candidate clay',OUT/'candidate-fixed-clay.png',OUT/'candidate-side-clay.png'),
           ('parent walnut',A/'render.png',A/'guide-render.png'),
           ('candidate walnut / parent lights',OUT/'matched-parent-fixed.png',OUT/'matched-parent-side.png')]
    sheet=Image.new('RGB',(1312,1020),'#26272a')
    for i,(name,f,s) in enumerate(modes):
        put(sheet,f,(179,266,749,595),(328*i,0),(328,234),name+' / 54°')
        put(sheet,f,(451,443,559,513),(328*i,242),(328,207),'Eye / 54°')
        put(sheet,s,(270,113,926,508),(328*i,467),(328,248),name+' / side')
        put(sheet,s,(562,282,701,374),(328*i,720),(328,254),'Eye / side')
    sheet.save(OUT/'matched-features.png')
    sheet=Image.new('RGB',(1360,609),'#242628')
    for i,(name,file,box) in enumerate([
         ('Parent / rear',OUT/'parent-rear-clay.png',(180,21,463,412)),
         ('Candidate / rear',OUT/'candidate-rear-clay.png',(180,21,463,412)),
         ('Parent / rear quarter',OUT/'parent-rear-quarter-clay.png',(157,26,497,435)),
         ('Candidate / rear quarter',OUT/'candidate-rear-quarter-clay.png',(157,26,497,435)),
         ('Parent / opposite quarter',OUT/'parent-far-rear-quarter-clay.png',(157,26,497,435)),
         ('Candidate / opposite quarter',OUT/'candidate-far-rear-quarter-clay.png',(157,26,497,435)),
         ('Parent / front',OUT/'parent-front-clay.png',(170,26,480,418)),
         ('Candidate / front',OUT/'candidate-front-clay.png',(170,26,480,418))]):
        put(sheet,file,box,((i%4)*340,(i//4)*303),(338,301),name)
    sheet.save(OUT/'clay-ridges.png')
    sheet=Image.new('RGB',(1400,861),'#232527')
    for i,(name,im) in enumerate([('Black original',sprite),('Black candidate 2',ref),('Parent',old),('Candidate A',new)]):
        put(sheet,im,(165,258,785,1070),(350*i,0),(350,360),name)
        put(sheet,im,(192,267,579,515),(350*i,363),(350,239),'Mane and eye')
        put(sheet,im,(448,441,560,513),(350*i,608),(350,166),'Eye')
        board=im.resize((100,100),Image.Resampling.LANCZOS)
        sheet.paste(board,(350*i+127,764),board)
    sheet.save(OUT/'reference-comparison.png')
    sheet=Image.new('RGB',(1320,634),'#252729')
    for i,(name,f,box) in enumerate([
        ('Walnut / 54°',OUT/'wood.png',(170,252,785,1060)),('Walnut / registered side',OUT/'wood-side.png',(267,74,958,1144)),
        ('Walnut / opposite',OUT/'wood-opposite.png',(47,22,457,458)),('Walnut / rear',OUT/'wood-rear.png',(47,22,457,458)),
        ('Clay / near',OUT/'clay-turn/00.png',(36,18,450,455)),('Clay / front',OUT/'clay-turn/04.png',(36,18,450,455)),
        ('Clay / opposite',OUT/'clay-turn/08.png',(36,18,450,455)),('Clay / rear quarter',OUT/'clay-turn/14.png',(36,18,450,455))]):
        put(sheet,f,box,((i%4)*330,(i//4)*317),(328,315),name)
    sheet.save(OUT/'diagnostics.png')
    turns=[]
    for p in sorted((OUT/'clay-turn').glob('*.png')):
        im=load(p);bg=Image.new('RGB',im.size,'#383a3d');bg.paste(im,(0,0),im);turns.append(bg)
    turns[0].save(OUT/'clay-turn.webp',save_all=True,append_images=turns[1:],duration=280,loop=0,quality=93)
    masks=[silhouette(im,True) for im in [sprite,ref]]
    samples=[silhouette(im) for im in [old,new]]
    scores={label:{k:iou(c,refmask) for k,c in zip(['parent','candidate'],samples)}
           for label,refmask in zip(['original','black_2'],masks)}
    scores['parent_overlap']={'fixed':iou(*samples),'side':iou(silhouette(load(A/'guide-render.png')),silhouette(load(OUT/'wood-side.png')))}
    (OUT/'outline-metrics.json').write_text(json.dumps(scores,indent=2)+'\n')
    print(json.dumps(scores))


if __name__=='__main__':main()
