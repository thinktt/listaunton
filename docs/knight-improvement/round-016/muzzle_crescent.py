"""Trace the narrow muzzle cut from the cheek to the notch at the nose."""
import json, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

root=Path(sys.argv[1]).resolve()
round_number=int(sys.argv[2])
build=root/'build/knight-mission'
judge=build/f'round-{round_number:03}-judge'
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import black, registered

refs=registered()
pictures={'Original black':refs['original'],'Black 2':refs['selected'],'Parent':Image.open(root/'assets/knight/render.png')}
for code in sys.argv[3:]:pictures[code]=Image.open(build/f'improvement-{round_number:03}-{code}/wood.png')
for key,file in [('Parent pigment','pigment.png'),('Parent polish','polish.png')]:
    native=judge/'passes-parent'/file
    if native.is_file():pictures[key]=Image.open(native)
anchors=[(546,484),(555,490),(565,495),(580,500),(596,503),(611,506),(630,508),(646,508),(660,507),(673,503),(684,498),(689,496),(695,498),(704,502),(715,509),(723,516)]
ax,ay=np.array(anchors).T
xs=np.arange(547,724)
guide=np.interp(xs,ax,ay).round().astype(int)
box=(533,460,744,538)
font=ImageFont.load_default(size=14)
w,h=264,98
sheet=Image.new('RGB',(len(pictures)*w,2*h+62),'#252826');d=ImageDraw.Draw(sheet);report={}
for col,(name,raw) in enumerate(pictures.items()):
    rgb=black(raw.convert('RGBA'))
    lum=np.asarray(rgb.filter(ImageFilter.GaussianBlur(2)),float)@[.2126,.7152,.0722]
    # Follow a continuous dark return. Penalize departures from the reference
    # path and fast jumps to pores or a neighboring specular reflection.
    offsets=np.arange(-7,8)
    band=lum[guide[:,None]+offsets,xs[:,None]]
    dep=band+.28*np.square(offsets)[None,:]
    hops=1.4*np.square(offsets[:,None]-offsets[None,:])
    indices=[]
    cost=dep[0]
    for row in dep[1:]:
        path=cost[:,None]+hops
        previous=path.argmin(axis=0)
        indices.append(previous)
        cost=row+path[previous,np.arange(len(offsets))]
    out=[cost.argmin()]
    for previous in reversed(indices):out.append(previous[out[-1]])
    y=guide+offsets[out[::-1]]
    # Brightness above and below the cut distinguishes a recessed line from a soft gradient.
    floor=lum[y,xs]
    above=lum[y-5,xs]
    below=lum[y+5,xs]
    record={}
    for label,lo,hi in [('cheekward',552,597),('long middle',599,663),('notch rise',669,689),('notch return',692,716)]:
        m=(xs>=lo)&(xs<=hi)
        record[label]={'vertical_offset_px':round(float(np.median((y-guide)[m])),2),
                       'wood_above_minus_line':round(float(np.median((above-floor)[m])),2),
                       'lower_lip_minus_line':round(float(np.median((below-floor)[m])),2),
                       'fraction_both_flanks_brighter':round(float(((above[m]>floor[m])&(below[m]>floor[m])).mean()),3)}
    forward=(xs>=672)&(xs<=717)
    lip_offsets=np.arange(2,18)
    lip=lum[guide[forward,None]+lip_offsets,xs[forward,None]]
    positive=np.maximum(lip-np.percentile(lip,80),0)
    lip_x=xs[forward,None]
    lip_y=guide[forward,None]+lip_offsets
    brightness={'centroid_of_upper_fifth_xy':[round(float((positive*coord).sum()/positive.sum()),2) if positive.sum() else None for coord in (lip_x,lip_y)],
                'peak_xy':[int(lip_x[np.unravel_index(lip.argmax(),lip.shape)[0],0]),int(lip_y[np.unravel_index(lip.argmax(),lip.shape)])],
                'peak_luma':round(float(lip.max()),2),'noseward_share':round(float(positive[xs[forward]>=696].sum()/positive.sum()),3) if positive.sum() else None}
    report[name]={'sections':record,'lower_reflection':brightness,'trace':np.column_stack((xs,y)).tolist()}
    tile=rgb.crop(box).resize((w-3,h),Image.Resampling.LANCZOS);l=col*w
    d.text((l+4,4),name,font=font,fill='#eeeade');sheet.paste(tile,(l,23));sheet.paste(tile,(l,h+30))
    coords=[(l+(x+.5-box[0])*(w-3)/(box[2]-box[0]),h+30+(yy+.5-box[1])*h/(box[3]-box[1])) for x,yy in zip(xs,y)]
    d.line(coords,fill='#81baa7',width=1)
d.text((5,2*h+36),'Muzzle cut and forward notch in the fixed reference view. Green follows the local dark line.',font=font,fill='#dddccf')
sheet.save(judge/'muzzle-crescent.png')
(judge/'muzzle-crescent.json').write_text(json.dumps({'method':'Hand-registered source anchors, 2px Gaussian blur and a continuous local luminance trough within seven vertical pixels. The signed differences use samples five pixels above and below. A light boundary can come from surface shape, finish or shadow.','anchor_points':[list(p) for p in anchors],'images':report},indent=2)+'\n')
print({k:v['sections'] for k,v in report.items()})
