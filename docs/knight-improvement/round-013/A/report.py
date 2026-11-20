from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(R/'scripts/knight'))
from audit_mission import black,registered,silhouette,iou
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
def read(p):return json.loads(Path(p).read_bytes())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgba(p):return Image.open(p).convert('RGBA')
def sheet(name,rows,cell):
    w,h=cell;bar=29
    canvas=Image.new('RGB',(w*len(rows[0]),(h+bar)*len(rows)),'#1e2220');draw=ImageDraw.Draw(canvas)
    for iy,row in enumerate(rows):
        for ix,(label,pic) in enumerate(row):
            x=ix*w;y=iy*(h+bar);draw.text((x+5,y+4),label,font=font,fill='#eeeae1')
            pic=pic.convert('RGBA');pic.thumbnail((w,h),Image.Resampling.LANCZOS)
            canvas.paste(pic,(x+(w-pic.width)//2,y+bar+(h-pic.height)//2),pic.getchannel('A'))
    canvas.save(D/name)
def go():
    params=read(D/'parameters.json');m=params['reopened_renders'];model=digest(D/'knight.blend')
    assert model==params['model_sha256'] and digest(D/'pigment.png')==params['packed_atlas_sha256']
    assert m['samples']==144 and digest(D/'wood.png')==m['fixed_sha256'] and digest(D/'wood-side.png')==m['side_sha256']
    refs=registered();full={'Original':refs['original'],'Black 2':refs['selected'],'12B':rgba(D/'parent-wood.png'),'13A':rgba(D/'wood.png')}
    sheet('comparison.png',[[(n,i.crop((146,242,813,1092))) for n,i in full.items()]],(246,325))
    sheet('board.png',[[(n,i.resize((100,100),Image.Resampling.LANCZOS)) for n,i in full.items()]],(100,100))
    eye=(451,447,585,520)
    sheet('registered-eye.png',[[(n,i.crop(eye).resize((282,153),Image.Resampling.LANCZOS)) for n,i in full.items()]],(282,153))
    masks={}
    for n,im in full.items():
        rgba_data=np.asarray(im);mask=rgba_data[:,:,3]>127
        if n in ['Original','Black 2']:mask=mask&(rgba_data[:,:,:3].max(2)>12)
        masks[n]=mask
    size={'fixed_changed_alpha_pixels':int((masks['12B']!=masks['13A']).sum()),
      'raw_foreground_iou':{s:{n:iou(masks[s],masks[n]) for n in ['12B','13A']} for s in ['Original','Black 2']},
      'side_changed_alpha_pixels':int(((np.asarray(rgba(D/'parent-wood-side.png'))[:,:,3]>127)!=(np.asarray(rgba(D/'wood-side.png'))[:,:,3]>127)).sum())}
    point=full['13A'].getpixel((545,493));size['nasal_corner_rgb']=list(point[:3])
    (D/'image-validation.json').write_text(json.dumps(size,indent=2)+'\n')
    steps=[('Near',0),('Front quarter',2),('Front',4),('Far',8),('Rear',12),('Rear quarter',14)]
    sheet('clay-turn.png',[[ (s,rgba(D/'clay-turn'/f'{i:02d}.png')) for s,i in steps]],(176,176))
    rows=[]
    for n,title in [('parent','12B'),('knight','13A')]:
        rows.append([(f'{title}  {degree}°',rgba(D/f'head-{n}-{degree}.png')) for degree in [-30,0,30]])
    sheet('whole-head-clay.png',rows,(330,225))
    if (D/'matched-studio.json').exists() and read(D/'matched-studio.json')['model']==model:
        rows=[]
        for label,fixed,side in [('12B, inherited studio','parent-wood.png','parent-wood-side.png'),('13A, inherited studio','matched-parent-fixed.png','matched-parent-side.png'),('13A, final studio','wood.png','wood-side.png')]:
            rows.append([(label+' at 54°',rgba(D/fixed).crop(eye).resize((325,177),Image.Resampling.LANCZOS)),(label+' at 7°',rgba(D/side).crop((570,235,823,420)).resize((325,237),Image.Resampling.LANCZOS))])
        sheet('matched-studio.png',rows,(325,218))
    pa=D/'portraits-A';pp=D/'portraits-parent'
    if (pa/'source.json').exists() and read(pa/'source.json')['model']==model:
        rows=[]
        for title,path in [('12B',pp),('13A',pa)]:
            for mat in ['clay','walnut']:
                rows.append([(title+' '+mat+' near',rgba(path/(mat+'-near.png'))),(title+' '+mat+' mirrored far',ImageOps.mirror(rgba(path/(mat+'-far.png'))))])
        sheet('flank-portraits.png',rows,(307,216))
    if (D/'moving.json').exists() and read(D/'moving.json')['model']==model:
        rows=[]
        for title,modelname in [('12B','parent'),('13A','knight')]:
            for mat in ['wood','clay']:
                rows.append([(f'{title} {mat} {degree}°',rgba(D/'moving'/f'{modelname}-{mat}-{i}.png')) for i,degree in enumerate([-56,-30,0,30,56])])
        sheet('moving-light.png',rows,(196,140))
        frames=[rgba(D/'moving'/f'knight-wood-{i}.png').convert('RGB') for i in [0,1,2,3,4,3,2,1]]
        frames[0].save(D/'moving-highlight.webp',save_all=True,append_images=frames[1:],duration=280,loop=0,quality=86)
if __name__=='__main__':go()
