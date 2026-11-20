"""Compare frontmost ear boundaries on the registered source photos and carvings."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
D=Path(__file__).resolve().parent;sys.dont_write_bytecode=True
sys.path.insert(0,str(D))
from fit import shapes
from review import load
def main():
    src=shapes()
    labels=[('Released parent',D/'ear-parent.json',src[2]),('Uniform 7A',D/'uniform-study/ear.json',load(D/'uniform-study/wood.png')),
            ('Final 7A',D/'ear-final.json',load(D/'wood.png'))]
    rect=(215,339,592,487);w,h=377,148
    sheet=Image.new('RGB',(3*w,3*(h+24)),'#27292b');summary={}
    for row,(key,p,im) in enumerate(labels):
        pts=np.array(json.loads(p.read_text())['visible_ear_columns'])
        poly=np.vstack([pts[:,[0,1]],pts[::-1][:,[0,2]],pts[:1,[0,1]]])
        summary[key]={'first_column_xy':pts[0].tolist(),'last_column_xy':pts[-1].tolist()}
        for col,(lab,source) in enumerate([('original',src[0]),('black 2',src[1]),('model',im)]):
            x=col*w;y=row*(h+24)
            view=source.crop(rect);sheet.paste(view,(x,y+24),view)
            draw=ImageDraw.Draw(sheet);draw.text((x+4,y+5),key+' on '+lab,fill='#eeeeea')
            draw.line([tuple(v) for v in poly+np.array([x-rect[0],y+24-rect[1]])],fill='#91d7ed',width=1)
            if col<2:
                box=(235,372,351,428)
                a=np.asarray(im.convert('RGB').filter(ImageFilter.GaussianBlur(2)).crop(box)).astype(float)
                b=np.asarray(source.convert('RGB').filter(ImageFilter.GaussianBlur(2)).crop(box)).astype(float)
                summary[key][lab+'_tip_patch_mean_rgb_error']=float(np.abs(a-b).mean())
    sheet.save(D/'ear-footprint.png')
    (D/'ear-comparison.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
if __name__=='__main__':main()
