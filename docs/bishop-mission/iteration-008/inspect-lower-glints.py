from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[2]
canvas=Image.new('RGB',(1000,680),'#171b21');draw=ImageDraw.Draw(canvas)
for i,(label,path) in enumerate([('Reference','assets/bishop/reference.png'),('Accepted 007','history/bishop-mission-007/render.png')]):
    im=Image.open(root/path).convert('RGB');ar=np.array(im)
    crop=im.crop((350,760,750,1080)).resize((400,320))
    canvas.paste(crop,(i*500,40));draw.text((i*500+10,10),label,fill='white')
    for x in range(350,751,50):
        xx=i*500+x-350;draw.line((xx,40,xx,360),fill='#58646e');draw.text((xx+2,365),str(x),fill='white')
    for y in range(760,1081,40):
        yy=40+y-760;draw.line((i*500,yy,i*500+400,yy),fill='#58646e');draw.text((i*500+405,yy),str(y),fill='white')
    reg=ar[920:1030,500:670].astype(float);v=reg[:,:,2]
    mask=v>np.percentile(v,98);yy,xx=np.nonzero(mask)
    print(label,'bright-blue base centroid',float(xx.mean()+500),float(yy.mean()+920),'mean RGB',reg[mask].mean(0))
canvas.crop((0,0,1000,400)).save(root/'build/bishop-mission/lower-glint-grid.png')
