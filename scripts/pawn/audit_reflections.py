"""Measure and show the fine grain inside the pawn's actual reflections."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).parent))
from derive_wood import ROOT,blur

REGIONS=[('head-left',461,451,15,14),('head-upper',509,435,20,20),
         ('head-right',515,490,18,24),('flare-left',402,880,28,12),
         ('flare-line',559,906,15,5),('socket-lip',523,758,12,6),
         ('foot-line',548,961,18,6),('stem-edge',407,627,12,7)]


def run(out,trials):
    paths={'selected':ROOT/'assets/pawn/reference.png',
           'accepted-baseline':ROOT/'assets/pawn/render.png'}
    for trial in trials:paths[trial]=ROOT/'build/pawn-mission'/trial/'fixed.png'
    results={};reference={};images={}
    for key,path in paths.items():
        images[key]=Image.open(path).convert('RGB')
        rgb=np.asarray(images[key],np.float32)
        luma=rgb@np.array([.24,.53,.23],np.float32)
        hp=luma-blur(luma,r=2,passes=2)
        row={}
        for label,x,y,rx,ry in REGIONS:
            b=np.s_[y-ry:y+ry,x-rx:x+rx];h=hp[b].ravel()
            if key=='selected':reference[label]=h.copy()
            row[label]={'median':float(np.median(luma[b])),
                        'p99':float(np.quantile(luma[b],.99)),
                        'ripple_rms':float(np.mean(h*h)**.5),
                        'ripple_correlation':float(np.corrcoef(h,reference[label])[0,1])}
        results[key]=row
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(results,indent=2)+'\n',encoding='utf8')
    patches=[('Flare left',(365,857,447,903)),('Flare line',(518,880,599,932)),
             ('Foot line',(500,935,594,985))]
    canvas=Image.new('RGB',(320*len(paths),230*len(patches)+38),(22,24,27))
    draw=ImageDraw.Draw(canvas)
    fontpath=Path('C:/Windows/Fonts/segoeui.ttf')
    font=ImageFont.truetype(str(fontpath),16) if fontpath.is_file() else ImageFont.load_default(size=16)
    for col,(key,im) in enumerate(images.items()):
        draw.text((col*320+8,8),key,font=font,fill='#edebe6')
        for row,(label,box) in enumerate(patches):
            x,y=col*320+8,38+230*row
            draw.text((x,y),label,font=font,fill='#edebe6')
            crop=im.crop(box);crop.thumbnail((300,190))
            size=(300,round(crop.height*300/crop.width))
            canvas.paste(crop.resize(size,Image.Resampling.NEAREST),(x,y+28))
    canvas.save(out.with_suffix('.png'))
    for key,row in results.items():
        print(key,[(k,round(row[k]['ripple_rms'],2),round(row[k]['ripple_correlation'],4)) for k in ('head-upper','flare-left','flare-line','foot-line')])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('trials',nargs='+');a=p.parse_args()
    run(a.output,a.trials)
