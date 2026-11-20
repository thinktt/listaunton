"""Publish true fixed and side render crops, native board scale, and the clay turn."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parents[2]
sys.path.insert(0,str(D))
from reference_images import registered,black,silhouette,iou
from crest_measure import go
BG='#292b2b'
def put(canvas,img,rect,x,y,w,h,title):
    rgba=img.convert('RGBA')
    ratio=rgba.width/1254
    crop=rgba.crop(tuple(round(n*ratio) for n in rect))
    crop.thumbnail((w,h-21),Image.Resampling.LANCZOS)
    canvas.paste(crop,(x+(w-crop.width)//2,y+19),crop)
    ImageDraw.Draw(canvas).text((x+6,y+3),title,fill='#e6e3dc')
def im(name):return Image.open(D/name).convert('RGBA')
def main():
    refs=registered()
    pics=[refs['original'],refs['selected'],im('parent-wood.png'),im('wood.png')]
    flat=Image.new('RGB',(1100,521),BG)
    for i,pre in enumerate(['parent-','']):
        for j,(view,box) in enumerate([('fixed',(195,276,786,570)),('side',(220,81,945,433))]):
            put(flat,im(f'{pre}clay-{view}.png'),box,j*550,i*260,550,258,('Parent' if i==0 else '10B')+' · '+view+' clay')
    flat.save(D/'flat-comparison.png')
    studio=Image.new('RGB',(1056,534),BG)
    for i,(p,label) in enumerate(zip(pics,['Original','Black 2','Parent','10B'])):
        put(studio,p,(155,261,790,1086),264*i,0,264,309,label+' · fixed')
        mini=p.resize((90,90),Image.Resampling.LANCZOS)
        studio.paste(mini,(264*i+87,316),mini)
    for i,(p,label) in enumerate(zip([im('parent-side.png'),im('wood-side.png')],['Parent side','10B side'])):
        put(studio,p,(210,103,950,434),i*528,404,528,128,label+' · crest')
    studio.save(D/'board-and-side.png')
    orbit=Image.new('RGB',(1100,536),BG)
    for i,(tag,idx) in enumerate([('near',0),('front',4),('opposite',8),('rear-quarter',10),('rear',12)]):
        for row,(name,title) in enumerate([(f'wood-{tag}.png',tag),(f'clay-{idx:02d}.png','Clay · '+tag)]):
            put(orbit,im(name),(180,73,1090,1205),i*220,row*268,220,268,title)
    orbit.save(D/'contact.png')
    frames=[]
    for i in range(16):
        p=im(f'clay-{i:02d}.png').crop((105,19,544,626))
        frame=Image.new('RGB',p.size,BG);frame.paste(p,(0,0),p)
        frame.thumbnail((330,400),Image.Resampling.LANCZOS);frames.append(frame)
    frames[0].save(D/'clay-turn.webp',save_all=True,append_images=frames[1:],duration=330,loop=0,quality=88)
    data={}
    masks=[silhouette(p,i<2) for i,p in enumerate(pics)]
    for k,m in zip(['Original','Black 2','Parent','10B'],masks):
        data[k]={'whole_IoU_original':iou(m,masks[0]),'whole_IoU_black2':iou(m,masks[1])}
    (D/'silhouette.json').write_text(json.dumps(data,indent=2)+'\n')
    go()
if __name__=='__main__':main()
