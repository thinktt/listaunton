"""Compare a 54-degree reflection in registered renders with the source and parent."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;A=D.parents[2]/'assets/knight'
BOX=(258,295,485,383)
def crop(p):
    img=Image.open(p).convert('RGBA')
    if img.width==1254:return img.crop(BOX)
    return img
def metrics(img):
    pix=np.asarray(img)[:,:,:3].astype(float)
    pad=np.pad(pix,((2,2),(2,2),(0,0)),mode='edge')
    lum=sum(pad[y:y+pix.shape[0],x:x+pix.shape[1]].mean(2) for x in range(5) for y in range(5))/25
    xs=np.arange(316,462,4)
    trace=np.interp(xs,[300,320,340,360,380,400,420,440,460,470],
                        [345,341,338,338,338,339,340,342,351,357]).round().astype(int)
    offsets=np.arange(-28,29)
    h=lum[trace[None,:]-BOX[1]+offsets[:,None],xs[None,:]-BOX[0]]
    off=[];sizes=[];peaks=[];sh=[]
    for col in h.T:
        y=int(np.argmax(col[13:44])+13)
        pk=col[y]
        threshold=(pk+np.mean(np.r_[col[1:9],col[46:54]]))*.5
        low=next((j for j in range(y,-1,-1) if col[j]<threshold),-1)
        high=next((j for j in range(y,len(col)) if col[j]<threshold),len(col))
        off.append(abs(offsets[y]));sizes.append(high-low-1);peaks.append(pk);sh.append(np.mean(col[36:46]))
    return {k:float(np.median(m)) for k,m in [('absolute_trace_error',off),('width_pixels',sizes),('peak_0_to_255',peaks),('shadow_below',sh)]}
def main():
    paths=[('Black 2',A/'ref.png'),('Parent',A/'render.png')]
    paths.extend((tag,D/f'card-{tag}.png') for tag in ('off','minus32','minus16','zero','plus16','plus32')
                 if (D/f'card-{tag}.png').exists())
    if (D/'wood.png').exists():paths.append(('Final',D/'wood.png'))
    m={};w,h=365,169
    sheet=Image.new('RGB',(w*3,h*((len(paths)+2)//3)),'#303235')
    for j,(label,p) in enumerate(paths):
        im=crop(p);m[label]=metrics(im)
        x=j%3*w;y=j//3*h
        ImageDraw.Draw(sheet).text((x+4,y+3),label,fill='white')
        im=im.resize((352,137),Image.Resampling.LANCZOS)
        sheet.paste(im,(x+5,y+22),im)
    sheet.save(D/'card-study.png');(D/'card-study.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m))
if __name__=='__main__':main()
