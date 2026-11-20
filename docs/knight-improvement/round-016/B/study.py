"""Measure the crest color, forward cap return and breadth of the near bevel."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from reference_images import registered,black
BOX=(240,278,508,414);gray=np.array([.2126,.7152,.0722]);scale=Image.Resampling.LANCZOS
px=[276,288,300,320,340,360,380,400,420,440,452,462,470,477,484];py=[356,351,346,341,338,338,338,339,340,342,345,350,354,358,365]
def metrics(im):
    smooth=np.asarray(im.filter(ImageFilter.GaussianBlur(1.6)),float);lum=smooth@gray
    fine=np.asarray(im.filter(ImageFilter.GaussianBlur(.7)),float)@gray
    coarse=np.asarray(im.filter(ImageFilter.GaussianBlur(3.5)),float)@gray
    xs=np.arange(278,481);guide=np.rint(np.interp(xs,px,py)).astype(int)-BOX[1];xi=xs-BOX[0]
    peak=guide+np.array([np.argmax(lum[y-10:y+11,x])-10 for x,y in zip(xi,guide)])
    rgb=smooth[peak[:,None]+np.arange(-3,4),xi[:,None]]
    rgb=np.take_along_axis(rgb,np.argsort(rgb@gray,axis=1)[:,-3:,None],axis=1).mean(1)
    parts={}
    for name,lo,hi in [('rear',298,340),('middle',341,409),('forward',410,450),('return',451,476)]:
        use=(xs>=lo)&(xs<=hi);x=xi[use];yp=peak[use];lumax=rgb[use]@gray
        cols=[]
        for col,y in zip(x,yp):
            z=lum[:,col];c=(z[y]+np.percentile(z[y+8:y+21],35))/2;L=H=y
            while L>y-18 and z[L-1]>c:L-=1
            while H<y+19 and z[H+1]>c:H+=1
            cols.append(H-L+1)
        y=guide[use,None]+np.arange(-25,-12);x=x[:,None]
        parts[name]={'edge_luma':round(float(np.median(lumax)),2),'warmth':round(float(np.median(rgb[use,0]-rgb[use,2])),2),
            'underface':round(float(np.median(lum[yp+15,xi[use]])),2),'width':float(np.median(cols)),
            'cap_pore_contrast':round(float(np.sqrt(np.mean(((fine[y,x]-coarse[y,x])/np.maximum(15,coarse[y,x]))**2))),4)}
    xx=np.arange(298,472);yy=np.rint(np.interp(xx,[298,320,340,360,380,400,420,440,452,462,471],[347,341,338,338,338,339,340,342,345,350,355])).astype(int)
    X=np.broadcast_to(xx[:,None],(len(xx),19));Y=yy[:,None]+np.arange(-23,-4);area=(np.asarray(im.filter(ImageFilter.GaussianBlur(3)),float)@gray)[Y-BOX[1],X-BOX[0]]
    w=np.maximum(area-np.percentile(area,90),0);center=[round(float((a*w).sum()/w.sum()),2) for a in [X,Y]]
    return {'parts':parts,'cap_center':center,'cap_median':round(float(np.median(area)),2),'cap_p90':round(float(np.percentile(area,90)),2)}
def run(keys):
    refs=registered();items={k:black(refs[f]).crop(BOX) for k,f in [('Original','original'),('Black 2','selected')]}
    for k in ['parent',*keys]:
        file=D/('parent-wood.png' if k=='parent' else 'wood.png' if k=='knight' else f'trial-{k}.png')
        if file.exists():
            img=black(Image.open(file).convert('RGBA'));items[k]=img.crop(BOX) if img.width>600 else img
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16);w,h=324,220;nc=min(4,len(items));nr=(len(items)+nc-1)//nc
    sheet=Image.new('RGB',(w*nc,h*nr),'#202521');dr=ImageDraw.Draw(sheet);out={}
    for i,(k,img) in enumerate(items.items()):
        x=(i%nc)*w;y=(i//nc)*h;q=metrics(img);out[k]=q;dr.text((x+5,y+1),k,font=font,fill='#fcfaf4');sheet.paste(img.resize((w-3,163),scale),(x,y+25))
        line=f"Cap x {q['cap_center'][0]:.0f}   ·   Edge R−B {q['parts']['middle']['warmth']:.0f}   ·   Face {q['parts']['middle']['underface']:.0f}"
        dr.text((x+4,y+190),line,font=font,fill='#c8d4c4')
        print(k,q['cap_center'],[(p['edge_luma'],p['warmth'],p['underface'],p['width']) for p in q['parts'].values()])
    stem='crest-comparison' if 'knight' in keys else 'study'
    sheet.save(D/(stem+'.png'));(D/(stem+'.json')).write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':run(sys.argv[1:])
