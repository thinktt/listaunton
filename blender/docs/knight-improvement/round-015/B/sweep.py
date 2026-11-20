"""Trace the photographed upper eyelid into its two corners on a shared pixel grid."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

out=Path(__file__).resolve().parent
sys.path.insert(0,str(out))
from reference_images import registered,black
refs=registered()
pics={'Original black':refs['original'],'Black 2':refs['selected'],'Parent':Image.open(out/'parent-wood.png')}
for k in sys.argv[1:]:
    im=Image.open(out/('wood.png' if k=='knight' else f'trial-{k}-fixed.png')).convert('RGBA')
    if im.width<600:
        full=Image.new('RGBA',pics['Parent'].size);full.paste(im,(448,444));im=full
    pics['15B' if k=='knight' else k]=im
def dark_path(im):
    lum = np.asarray(im.filter(ImageFilter.GaussianBlur(1.25)),float)@[.2126,.7152,.0722]
    # A loose search band follows the upper brow's photographed outline under the poll.
    # The curve within it must be supported by the actual dark ridge.
    anchors = [(470,467),(475,468),(485,464),(495,463),(505,464),(515,467),(525,469),(535,473),(545,479),(551,482),(558,487)]
    ax,ay = np.transpose(anchors)
    cols = np.arange(471,558)
    seed = np.rint(np.interp(cols,ax,ay)).astype(int)
    states = np.arange(-4,5)
    locations = seed[:,None]+states
    values = lum[locations,cols[:,None]]
    shadow = (lum[locations-4,cols[:,None]]+lum[locations+4,cols[:,None]])/2-values
    cost = np.zeros_like(values)
    previous = np.zeros_like(values,dtype=int)
    for i in range(len(cols)):
        # Include darkness as well as local contrast to reject dark wood pores.
        local = .48*values[i]-.20*shadow[i]+.85*abs(states)
        if i==0:
            cost[i]=local
            continue
        jump = abs(locations[i,:,None]-locations[i-1,None,:])
        transitions = np.where(jump<=1,cost[i-1,None,:]+1.4*jump,np.inf)
        previous[i] = np.argmin(transitions,axis=1)
        cost[i] = local+transitions[np.arange(len(states)), previous[i]]
    indices = [int(cost[-1].argmin())]
    for i in range(len(cols)-1,0,-1):
        indices.append(int(previous[i,indices[-1]]))
    y = locations[np.arange(len(cols)),indices[::-1]]
    contrast = (lum[y-4,cols]+lum[y+4,cols])/2-lum[y,cols]
    return cols,y,contrast,lum

def quad_lights(lum):
    windows={'earward upper glint':(487,462,506,473),'inner glint':(495,471,515,481),
             'noseward crescent':(518,479,542,491)}
    result={}
    for name,(x0,y0,x1,y1) in windows.items():
        roi=lum[y0:y1,x0:x1]
        y,x=np.unravel_index(roi.argmax(),roi.shape)
        result[name]=[int(x)+x0,int(y)+y0,round(float(roi[y,x]),2)]
    return result

w,h=238,136
font=ImageFont.load_default(size=13)
sheet=Image.new('RGB',(w*len(pics),2*h+57),'#252823')
draw=ImageDraw.Draw(sheet)
record={}
box=(459,454,562,509)
source=black(refs['selected'].convert('RGBA'))
_,ref_y,_,_=dark_path(source)
for i,(label,pic) in enumerate(pics.items()):
    im=black(pic.convert('RGBA'))
    x,y,contrast,lum=dark_path(im)
    sides={}
    for name,lo,hi in [('earward corner',472,486),('middle brow',487,522),('noseward corner',523,555)]:
        take=(x>=lo)&(x<=hi)
        yr=ref_y[take]
        col=x[take]
        fixed_contrast=(lum[yr-4,col]+lum[yr+4,col])/2-lum[yr,col]
        sides[name]={'mean_signed_displacement_y':round(float(np.mean(y[take]-ref_y[take])),2),
                     'median_contrast_on_exact_source_line':round(float(np.median(fixed_contrast)),2),
                     'median_dark_contrast':round(float(np.median(contrast[take])),2),
                     'tenth_percentile_dark_contrast':round(float(np.percentile(contrast[take],10)),2)}
    record[label]={'edge_sections':sides,'coarse_glint_peaks_xy_luma':quad_lights(lum),'trace':np.stack((x,y),axis=1).tolist()}
    crop=im.crop(box).resize((w-3,h),Image.Resampling.LANCZOS)
    left=i*w;draw.text((left+5,4),label,font=font,fill='#f3f0e7')
    sheet.paste(crop,(left,24));sheet.paste(crop,(left,h+30))
    pts=[(left+(xx+.5-box[0])*(w-3)/(box[2]-box[0]),h+30+(yy+.5-box[1])*h/(box[3]-box[1])) for xx,yy in zip(x,y)]
    draw.line(pts,fill='#7ac1aa',width=1)
draw.text((5,2*h+35),'Green follows the upper lid. Some crossings in the coarse sprite are ambiguous.',font=font,fill='#e3e9df')
sheet.save(out/'upper-eye-sweep.png')
(out/'upper-eye-sweep.json').write_text(json.dumps({'method':'One softly constrained, continuous dark line follows the upper lid on each registered image. Contrast is the average of samples four pixels above and below, minus the line itself. The three local peak windows are descriptive and cannot identify independent anatomical structures in the small original.', 'results':record},indent=2)+'\n')
for k,v in record.items():
    print(k,v['edge_sections'],v['coarse_glint_peaks_xy_luma'])
