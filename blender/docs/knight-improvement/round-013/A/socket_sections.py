"""Take transverse sections across actual visible lid and cheek surfaces on both flanks."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
j=Path(sys.argv[1]);labels=sys.argv[2:]
fig=Image.new('RGB',(828,545),'#232826');draw=ImageDraw.Draw(fig);font=ImageFont.load_default(size=14)
palette={'parent':'#c7c9c0','A':'#e6b17b','B':'#88cbb6'}
draw.text((14,6),'Transverse relief through the eye and cheek in native model units',font=font,fill='#edf1e4')
stats={};sections={};stations=[-.15,-.05,.075,.165]
for k,name in enumerate(labels):
    data=np.load(j/f'eyes-{name}.npz')
    u=data['u'][0];v=data['v'][::-1,0];rel={}
    for flank in ['near','far']:
        depth=data[flank][::-1];exposed=data[flank+'_insert'][::-1]
        info={'upper':[],'lower':[]}
        for col in np.flatnonzero((u>=-.16)&(u<=.165)):
            sl=exposed[:,col]
            if sl.sum()<3:continue
            d=depth[:,col]
            if not np.isfinite(d).all():continue
            for side,anchor in [('lower',min(v[sl])),('upper',max(v[sl]))]:
                if anchor-.035<v.min() or anchor+.035>v.max():continue
                window=(v>=anchor-.012)&(v<=anchor+.012)
                baseline=np.interp(v[window],[anchor-.035,anchor+.035],np.interp([anchor-.035,anchor+.035],v,d))
                info[side].append(max(0.,float((baseline-d[window]).max())))
        rel[flank]={key:{'number_of_sections':len(values),'median_recess':round(float(np.median(values)),5),'p90_recess':round(float(np.percentile(values,90)),5)} if values else {'number_of_sections':0} for key,values in info.items()}
    stats[name]=rel
    sections[name]={}
    for station in stations:
        col=int(abs(u-station).argmin());d=data['near'][::-1,col];mask=data['near_insert'][::-1,col]
        # Remove the cheek slope. Keep a common dimensional scale across all carvings.
        anchors=[-.125,.14]
        ends=np.interp(anchors,v,d);baseline=ends[0]+(v-anchors[0])*(ends[1]-ends[0])/(anchors[1]-anchors[0])
        sections[name][station]=(d-baseline,mask)
    x=16+k*115;draw.line((x,42,x+19,42),fill=palette[name],width=3);draw.text((x+25,33),name,font=font,fill='#e8e9df')
for i,station in enumerate(stations):
    x0=45+(i%2)*406;y0=84+(i//2)*206;w=330;h=132
    ylo=min(float(np.nanmin(sections[name][station][0])) for name in labels)
    yhi=max(float(np.nanmax(sections[name][station][0])) for name in labels)
    ylo=min(-.06,ylo);yhi=max(.06,yhi)
    def xy(pos,depth):return (x0+(pos+.16)*w/.32,y0+h-(depth-ylo)*h/(yhi-ylo))
    draw.text((x0,y0-18),f'Along the brow: {station:+.3f}',font=font,fill='#eeeee5')
    for px in [-.12,-.06,0,.06,.12]:
        xx,_=xy(px,0);draw.line((xx,y0,xx,y0+h),fill='#444b46');draw.text((xx-14,y0+h+3),str(px),font=font,fill='#d1d7c9')
    _,yline=xy(0,0);draw.line((x0,yline,x0+w,yline),fill='#798476')
    draw.text((x0-35,y0),f'{yhi:.2f}',font=font,fill='#dbdfd1');draw.text((x0-38,y0+h-17),f'{ylo:.2f}',font=font,fill='#dbdfd1')
    for name in labels:
        d,mask=sections[name][station]
        draw.line([xy(q,float(z)) for q,z in zip(v,d) if np.isfinite(z)],fill=palette[name],width=2)
        if mask.any():
            pts=[xy(v[e],d[e]) for e in [np.flatnonzero(mask)[0],np.flatnonzero(mask)[-1]]]
            for xx,yy in pts:draw.ellipse((xx-2,yy-2,xx+2,yy+2),fill=palette[name])
draw.text((11,493),'Left to right in each section: lower cheek, exposed eye, upper lid. Dots mark the visible insert margins.',font=font,fill='#e7e9dd')
draw.text((11,518),'Vertical scale gives lateral depth relative to the neighboring cheek slope. Depth and curvature are artistic choices.',font=font,fill='#e7e9dd')
fig.save(j/'socket-sections.png')
(j/'socket-sections.json').write_text(json.dumps({'method':'On each column of the opposed native eye rays, find upper and lower visible insert boundaries; compare the deepest nearby surface within 0.012 model units with a chord joining the samples 0.035 on either side of the boundary. Limits along eye axis are -0.16 to +0.165 units. Positive numbers indicate recess. The source photograph supplies no true physical recess depth.','results':stats},indent=2)+'\n')
print(stats)
