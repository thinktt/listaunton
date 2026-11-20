"""Separate carved highlights from the underlying walnut inside the registered eye."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
root=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);labels=sys.argv[3:]
build=root/'build/knight-mission';study=build/f'round-{n:03}-judge'
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import registered,black
target=black(registered()['selected'])
box=(455,445,565,514);w,h=244,155
sheet=Image.new('RGB',(4*w,(h+26)*len(labels)),'#222626');draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=13)
record={}
for row,label in enumerate(labels):
    actual=root/'assets/knight/render.png' if label=='parent' else build/f'improvement-{n:03}-{label}/wood.png'
    passes=study/f'passes-{label}'
    windows={'Black 2':target,'Rendered walnut':Image.open(actual),'Pigment alone':Image.open(passes/'pigment.png'),'Neutral polish':Image.open(passes/'polish.png')}
    yy,xx=np.indices((1254,1254))
    mask=np.zeros(xx.shape,bool)
    aperture=json.loads((study/f'fixed-eye-{label}.json').read_bytes())
    for x,first,last in aperture['columns']:
        mask[first:last+1,x]=True
    interior=np.asarray(Image.fromarray(mask).convert('L').filter(ImageFilter.MinFilter(5)))>0
    record[label]={}
    for col,(name,pic) in enumerate(windows.items()):
        site=black(pic.convert('RGBA'))
        x=col*w;y=row*(h+26)
        draw.text((x+6,y+2),f'{label} / {name}',font=font,fill='#eceae0')
        sheet.paste(site.crop(box).resize((w-3,h),Image.Resampling.LANCZOS),(x,y+24))
        arr=np.asarray(site,dtype=float)
        smoothed=np.asarray(site.filter(ImageFilter.GaussianBlur(2)),dtype=float)
        intensity=arr@[.2126,.7152,.0722];detail=intensity-smoothed@[.2126,.7152,.0722]
        record[label][name]={}
        for region,m in [('mid eye',interior&(xx>=478)&(xx<=514)),('nose corner',interior&(xx>=519)&(xx<=552))]:
            if not m.any():continue
            record[label][name][region]={'pixels':int(m.sum()),'median_rgb':np.round(np.median(arr[m],axis=0),1).tolist(),
               'luminance_p90_minus_p10':round(float(np.percentile(intensity[m],90)-np.percentile(intensity[m],10)),2),
               '2px_detail_rms':round(float(np.sqrt(np.mean(detail[m]**2))),2)}
sheet.save(study/'eye-finish.png')
(study/'eye-finish.json').write_text(json.dumps({'regions':record,'method':'Sample interior pixels of each mesh’s projected eye after a two-pixel erosion. Pigment is shaded as emission. Neutral polish replaces the material base colour only. Source and final render statistics include illumination.'},indent=2)+'\n')
for k,v in record.items():print(k,v['Pigment alone'])
