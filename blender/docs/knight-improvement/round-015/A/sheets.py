"""Source registration, true whole-head profiles, and a moving-light test."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,numpy as np
from study import black,reg
D=Path(__file__).resolve().parent;R=D.parents[2];AS=R/'assets/knight'
def sheet(name,rows,cell):
    w,h=cell;im=Image.new('RGB',(len(rows[0])*w,len(rows)*(h+25)),'#222724');p=ImageDraw.Draw(im);f=ImageFont.load_default(size=13)
    for j,row in enumerate(rows):
        for i,(tag,src) in enumerate(row):
            a=black(Image.open(src)) if isinstance(src,Path) else black(src);a.thumbnail((w-2,h),Image.Resampling.LANCZOS)
            left=i*w;top=j*(h+25);im.paste(a,(left+(w-a.width)//2,top+24));p.text((left+4,top+4),tag,font=f,fill='white')
    im.save(D/name)
def main():
    lo,hi=reg();orig=black(Image.open(AS/'original.png'));dim=orig.width
    align=json.loads((AS/'original-alignment.json').read_bytes());f=align['scale']*dim/hi.width
    ex=(-align['x']*3/f,-align['y']*3/f,(dim-align['x']*3)/f,(dim-align['y']*3)/f)
    figs=[('Original sprite',orig.resize((100,100),Image.Resampling.LANCZOS))]+[(k,a.resize((100,100),Image.Resampling.LANCZOS,box=ex)) for k,a in [('Black 2',hi),('14B',black(Image.open(D/'parent-wood.png'))),('15A',black(Image.open(D/'wood.png')))]]
    sheet('board.png',[figs],(118,100));pairs=[];checks={}
    for label,p,q in [('54 degrees','parent-wood.png','wood.png'),('7 degrees','parent-side.png','wood-side.png')]:
        a,b=[np.asarray(Image.open(D/file).convert('RGBA'))[:,:,3] for file in (p,q)];ma=a>=128;mb=b>=128
        checks[label]={'silhouette_iou':float((ma&mb).sum()/(ma|mb).sum()),'pixels_with_changed_alpha':int((a!=b).sum())}
        row=[]
        for tag,file in [('14B',p),('15A',q)]:
            pic=black(Image.open(D/file));row.append((tag+' / '+label,pic.crop(pic.getbbox())))
        pairs.append(row)
    sheet('fixed-and-side.png',pairs,(246,252));(D/'silhouette.json').write_text(json.dumps(checks,indent=2)+'\n')
    if (D/'knight-head-walnut-180.png').exists():
        sheet('true-profiles.png',[[(label+' / '+k+' / '+str(angle),D/f'{name}-head-{k}-{angle}.png') for angle in [-30,0,30,180]] for k in ['clay','walnut'] for name,label in [('parent','14B'),('knight','15A')]],(212,212))
    if (D/'moving.json').exists():
        sheet('moving-light.png',[[(label+' / '+k+' / '+str(a)+'°',D/'moving'/f'{name}-{k}-{i}.png') for i,a in enumerate([-56,-30,0,30,56])] for k in ['wood','clay'] for name,label in [('parent','14B'),('knight','15A')]],(176,126))
    if (D/'portraits/source.json').exists():
        sheet('paired-eyes.png',[[(k+' / '+side,D/'portraits'/f'{k}-{side}.png') for side in ['near','far']] for k in ['walnut','clay']],(287,200))
    folder=R/'build/knight-mission/round-015-judge/turn-eye-parent'
    sheet('earward-corner.png',[[(tag+' / '+k,base/f'{k}-0.png') for k in ['walnut','clay']] for tag,base in [('14B',folder),('15A',D/'turn-study')]],(346,244))
if __name__=='__main__':main()
