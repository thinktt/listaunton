from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent;A=D.parents[2]/'assets/knight'
def load(p):return Image.open(p).convert('RGBA')
def patch(im,box):
    rgba=im.crop(box).convert('RGBA')
    p=Image.alpha_composite(Image.new('RGBA',rgba.size,(0,0,0,255)),rgba).convert('RGB')
    lum=p.convert('L');a=np.asarray(lum).astype(float);blur=np.asarray(lum.filter(ImageFilter.GaussianBlur(4))).astype(float)
    q=np.percentile(np.log1p(a)-np.log1p(blur),[10,90]);return {'median_rgb':np.median(np.array(p),axis=(0,1)).tolist(),'local_contrast':float(q[1]-q[0])}
def main():
    old=load(D/'parent-wood.png');ref=load(A/'ref.png')
    if (D/'wood.png').exists():new=load(D/'wood.png');mode='final'
    else:
        new=old.copy();new.paste(load(D/'preview-fixed.png'),(342,395));mode='preview'
    specs={'Black 2':ref,'Parent':old,'8A':new};report={}
    panel=Image.new('RGB',(1110,661),'#27282b');draw=ImageDraw.Draw(panel)
    for i,(name,im) in enumerate(specs.items()):
        report[name]={k:patch(im,b) for k,b in {'cheek':(455,500,525,535),'upper_mane':(245,355,315,390),'chest':(317,570,387,605),'pedestal':(392,934,462,969)}.items()}
        for j,(title,b,size) in enumerate([('eye',(441,445,555,517),(361,199)),('head',(336,397,612,567),(361,222)),('cheek sample',(455,500,525,535),(315,145))]):
            x=i*370;y=[0,224,471][j];draw.text((x+5,y+2),name+' / '+title,fill='#eeeeed')
            pic=im.crop(b).resize(size,Image.Resampling.BICUBIC);panel.paste(pic,(x+3,y+18),pic)
    panel.save(D/(mode+'-cheek.png'));(D/(mode+'-cheek.json')).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
