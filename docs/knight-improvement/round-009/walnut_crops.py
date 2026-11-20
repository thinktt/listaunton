"""Compare the apparent wood figure in registered, fully opaque wood patches."""
from pathlib import Path
import argparse,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
p=argparse.ArgumentParser()
p.add_argument('root',type=Path);p.add_argument('number',type=int);p.add_argument('codes',nargs='*')
a=p.parse_args();root=a.root.resolve()
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import registered,black
ref=registered();build=root/'build/knight-mission';dest=build/f'round-{a.number:03}-judge'
imgs={'Black 2':ref['selected'],'Parent':Image.open(root/'assets/knight/render.png')}
for code in a.codes:imgs[code]=Image.open(build/f'improvement-{a.number:03}-{code}'/'wood.png')
regions={'Upper mane':(245,355,315,390),'Cheek':(455,500,525,535),
         'Upper chest':(317,570,387,605),'Base':(392,934,462,969)}
info={};w,h=184,116
panel=Image.new('RGB',(len(imgs)*w,len(regions)*h),'#242626');d=ImageDraw.Draw(panel)
for col,(key,img) in enumerate(imgs.items()):
    info[key]={}
    for row,(part,box) in enumerate(regions.items()):
        rgba=img.convert('RGBA').crop(box)
        assert rgba.getchannel('A').getextrema()[0]>240,(key,part)
        im=black(rgba)
        l=im.convert('L');arr=np.asarray(l).astype(float)
        base=np.asarray(l.filter(ImageFilter.GaussianBlur(4))).astype(float)
        micro=np.log1p(arr)-np.log1p(base)
        qs=np.percentile(micro,[10,90])
        info[key][part]={'median_rgb':np.median(np.array(im),axis=(0,1)).tolist(),
                         'local_log_luminance_p90_minus_p10':round(float(qs[1]-qs[0]),4)}
        d.text((col*w+4,row*h+4),f'{key} / {part}', fill='#f1eee7')
        panel.paste(im.resize((175,88),Image.Resampling.BICUBIC),(col*w+4,row*h+22))
dest.mkdir(exist_ok=True,parents=True)
panel.save(dest/'walnut-crops.png')
(dest/'walnut-crops.json').write_text(json.dumps({'method':'Corresponding fixed image patches at identical scale. The local contrast describes visible high-frequency shading and grain together, using the 10th and 90th percentiles of log(1+gray) after subtracting its radius-4 blurred equivalent.','regions':regions,'images':info},indent=2)+'\n')
print(info)
