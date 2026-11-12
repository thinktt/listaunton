"""Measure image highlights as observations, not recovered geometric edges."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter

P=Path(__file__).resolve().parent;S=P.parents[2]
reg=json.loads((S/'assets/queen/original-reference-alignment.json').read_text());s=reg['scale']
def original(color):
    return Image.open(S/f'references/lichess-staunton-3d/{color}-Queen.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(1/s,0,-reg['offset_x']/s,0,1/s,-reg['offset_y']/s),Image.Resampling.BILINEAR)
sources={'original_black':original('Black'),'original_white':original('White'),
         'selected_highres':Image.open(S/'assets/queen/reference.png'),
         'current_033':Image.open(P/'current-snapshot/queen-brown.png')}
rings=json.loads((P/'projected-socket-rings.json').read_text())
inner=np.array(next(a['points'] for a in rings if a['ring']==38))
outer=np.array(next(a['points'] for a in rings if a['ring']==33))
xs=np.arange(385,586,5);measurements={}
sheet=Image.new('RGB',(4*420,385),(15,20,26));pen=ImageDraw.Draw(sheet)
for j,(name,im) in enumerate(sources.items()):
    rgb=np.asarray(im.convert('RGB'),dtype=float)/255
    lum=gaussian_filter(rgb@np.array([.2126,.7152,.0722]),1.2)
    samples=[]
    for x in xs:
        lo=int(np.interp(x,inner[:,0],inner[:,1])-11);hi=int(np.interp(x,outer[:,0],outer[:,1])+3)
        column=lum[lo:hi+1,x-1:x+2].mean(1)
        k=int(np.argmax(column));y=lo+k
        samples.append({'x':int(x),'y':y,'luminance':float(column[k]),'boundary_peak':k in (0,len(column)-1)})
    measurements[name]=samples
    crop=im.convert('RGB').crop((345,660,625,880)).resize((420,330));d=ImageDraw.Draw(crop)
    for a in samples:
        x=(a['x']-345)*1.5;y=(a['y']-660)*1.5
        d.ellipse((x-2,y-2,x+2,y+2),fill='#65e7ff' if not a['boundary_peak'] else '#ff8474')
    sheet.paste(crop,(j*420,45));pen.text((j*420+8,12),name,fill='white')
comparison={}
for name,values in measurements.items():
    if name=='current_033':continue
    a=np.array([v['y'] for v in values]);b=np.array([v['y'] for v in measurements['current_033']])
    comparison[name]={'median_model_minus_reference_y':float(np.median(b-a)),
                      'mean_abs_vertical_difference':float(np.abs(b-a).mean()),
                      'center_x_460_to_510_median_difference':float(np.median((b-a)[(xs>=460)&(xs<=510)]))}
sheet.save(P/'crescent-peaks.png')
(P/'crescent-peaks.json').write_text(json.dumps({'method':'Maximum smoothed luminance within a fixed projected shelf band. Highlight locations are shading observations, not known geometry.',
    'samples':measurements,'comparison':comparison},indent=2)+'\n')
print(json.dumps(comparison,indent=2))
