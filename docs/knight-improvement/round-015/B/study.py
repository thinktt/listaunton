from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont,ImageOps
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from reference_images import registered,black
from eye_study import metrics
BOX=(448,444,594,527)
F=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15)
RES=Image.Resampling.LANCZOS
def crop_rgb(name):
    im=black(Image.open(name).convert('RGBA'))
    return im.crop(BOX) if im.width>600 else im
def lower(im):
    anchors=np.array(json.loads((D/'lower-trace.json').read_text())['anchors'])
    x=np.arange(459,548);yc=np.rint(np.interp(x,anchors[:,0],anchors[:,1])).astype(int)
    dy=np.arange(-11,14)
    light=np.asarray(im.filter(ImageFilter.GaussianBlur(1.8)),float)@[.2126,.7152,.0722]
    band=light[yc-BOX[1]+dy[:,None],x[None,:]-BOX[0]]
    peak=band[(dy>=-5)&(dy<=6)].max(axis=0);background=np.median(band[(dy>=9)&(dy<=13)],axis=0)
    p=np.convolve(np.pad(np.maximum(0,peak-background),(2,2),mode='edge'),np.ones(5)/5,'valid')
    c=np.cumsum(p)/max(p.sum(),1e-8)
    lo,mid,hi=[int(x[min(np.searchsorted(c,q),len(x)-1)]) for q in [.1,.5,.9]]
    return {'x10':lo,'x50':mid,'x90':hi,'width80':hi-lo,'peak':int(x[p.argmax()]),'peak_prominence':round(float(p.max()),2),'sum':round(float(p.sum()),2),'profile':np.round(p,1).tolist()}
def run(keys):
    refs=registered()
    objs=[('Original',black(refs['original']).crop(BOX),None),('Black 2',black(refs['selected']).crop(BOX),None)]
    for key in keys:
        label='Parent' if key in ['-1','parent'] else '15B' if key=='knight' else key
        file=D/('wood.png' if key=='knight' else 'parent-wood.png' if key=='parent' else f'trial-{key}-fixed.png')
        if file.exists(): objs.append((label,crop_rgb(file),key))
    c=Image.new('RGB',(224*len(objs),597),'#252927');dr=ImageDraw.Draw(c);output={}
    for i,(name,im,key) in enumerate(objs):
        x=224*i;dr.text((x+6,4),name,font=F,fill='white');c.paste(im.resize((224,128),RES),(x,29))
        stats=lower(im);eye=metrics(im,objs[1][1]);stats['inner_eye']=eye['inner_eye'];stats['eye_trace']=eye['trace_x508_516']
        polygon=json.loads((D/'inner-source.json').read_text())['polygon']
        mr=Image.new('L',im.size);ImageDraw.Draw(mr).polygon([(x-BOX[0],y-BOX[1]) for x,y in polygon],fill=255)
        m=np.asarray(mr)>0;yy,xx=np.indices(m.shape);xx+=BOX[0];yy+=BOX[1]
        light=np.asarray(im.filter(ImageFilter.GaussianBlur(1.25)),float)@[.2126,.7152,.0722]
        high=m*np.maximum(light-np.percentile(light[m],65),0);q=np.unravel_index(high.argmax(),m.shape)
        stats['inner_light']={'brightest':[int(xx[q]),int(yy[q])],'nose_percent':round(float(100*high[xx>=517].sum()/high.sum()),2)}
        text=f"80% {stats['x10']}–{stats['x90']} · peak {stats['peak']}"
        dr.text((x+4,162),text,font=F,fill='#e5e1d8')
        print(name,text,stats['peak_prominence'],eye['inner_eye'],stats['inner_light'],flush=True)
        output[name]=stats
        if key is None:continue
        for row,mode in enumerate(['side','clay']):
            if key in ['knight','parent']:file=D/('portraits-B' if key=='knight' else 'portraits-parent')/('walnut-near.png' if mode=='side' else 'clay-near.png')
            else:file=D/f'trial-{key}-{mode}.png'
            if file.exists():
                o=Image.open(file).convert('RGB');w,h=o.size
                o=o.crop((int(.20*w),int(.08*h),int(.86*w),int(.85*h)))
                c.paste(ImageOps.fit(o,(224,190),method=RES),(x,195+row*198))
    stem='comparison' if 'knight' in keys else 'study'
    c.save(D/(stem+'.png'));(D/(stem+'.json')).write_text(json.dumps(output,indent=2)+'\n')
if __name__=='__main__':run(sys.argv[1:])
