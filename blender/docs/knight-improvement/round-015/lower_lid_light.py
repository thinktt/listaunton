"""Measure the length and placement of the reflection beneath the photographed eye."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
r=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);labels=sys.argv[3:]
sys.path.insert(0,str(r/'scripts/knight'))
from audit_mission import black,registered
b=r/'build/knight-mission';dest=b/f'round-{n:03}-judge';dest.mkdir(parents=True,exist_ok=True)
photos=registered()
samples={'Original black':photos['original'],'Black 2':photos['selected'],'Parent':Image.open(r/'assets/knight/render.png')}
for name in labels:samples[name]=Image.open(b/f'improvement-{n:03}-{name}/wood.png')
anchors=np.array([(457,481),(466,485),(477,491),(487,496),(497,499),(509,500),(519,501),(529,500),(540,499),(549,497)])
x=np.arange(459,548)
center=np.rint(np.interp(x,anchors[:,0],anchors[:,1])).astype(int)
offset=np.arange(-11,14)
font=ImageFont.load_default(size=13)
sheet=Image.new('RGB',(max(716,166*len(samples)),412),'#232723');d=ImageDraw.Draw(sheet)
colors=['#bcc6ba','#fec87e','#a2bbc8','#c698df','#64d4ac']
report={};graphs=[]
for idx,(label,img) in enumerate(samples.items()):
    photo=black(img.convert('RGBA'));l=idx*166
    tile=photo.crop((451,444,554,514)).resize((164,112),Image.Resampling.LANCZOS)
    d.text((l+2,4),label,font=font,fill='#eae9df');sheet.paste(tile,(l,25))
    light=np.asarray(photo.filter(ImageFilter.GaussianBlur(1.8)),float)@[.2126,.7152,.0722]
    band=light[center[None,:]+offset[:,None],x[None,:]]
    peak_idx=np.argmax(band[(offset>=-5)&(offset<=6)],axis=0)
    peak=band[peak_idx+np.flatnonzero(offset==-5)[0],np.arange(len(x))]
    scatter=np.median(band[(offset>=9)&(offset<=13)],axis=0)
    prominence=np.maximum(0.,peak-scatter)
    smooth=np.convolve(np.pad(prominence,(2,2),mode='edge'),np.ones(5)/5,'valid')
    w=smooth/max(smooth.sum(),1e-8);cum=np.cumsum(w)
    xlo,x50,xhi=[int(x[min(np.searchsorted(cum,q),len(x)-1)]) for q in (.1,.5,.9)]
    p=peak_idx-5
    pathx=x[w>.003]
    if len(pathx)>0:
        px=(pathx-451)*164/103+l
        py=(center[w>.003]+p[w>.003]-444)*112/70+145
        sheet.paste(tile,(l,145));d.line(list(zip(px,py)),fill=colors[idx],width=1)
    row={'x_at_light_quantiles_10_50_90':[xlo,x50,xhi],'middle_80pc_length':xhi-xlo,'peak_contrast':round(float(smooth.max()),2),'peak_contrast_x':int(x[np.argmax(smooth)]),'percent_of_light_noseward_of_x511':round(float(w[x>=511].sum()*100),1),'positive_luminance_profile':np.round(smooth,2).tolist(),'peak_y':(center+p).tolist()}
    report[label]=row;graphs.append(smooth)
left=40;right=sheet.width-26;bottom=374;top=281;limit=max(15,float(np.ceil(max(a.max() for a in graphs)/10)*10))
for v in [0,limit/2,limit]:
    yy=bottom-(bottom-top)*v/limit;d.line((left,yy,right,yy),fill='#454b44');d.text((3,yy-5),str(round(v)),font=font,fill='#cccfc6')
for xx in [460,480,500,520,540]:
    horiz=left+(right-left)*(xx-x[0])/(x[-1]-x[0]);d.line((horiz,top,horiz,bottom),fill='#454b44');d.text((horiz-12,bottom+3),str(xx),font=font,fill='#dedfd4')
for a,color,label,idx in zip(graphs,colors,samples,range(len(samples))):
    d.line([(left+i*(right-left)/(len(x)-1),bottom-v*(bottom-top)/limit) for i,v in enumerate(a)],fill=color,width=2)
    px=idx*140+6;d.line((px,267,px+16,267),fill=color,width=3);d.text((px+20,260),label,font=font,fill='#e8e8df')
d.text((6,395),'Reflection above the local cheek value, along the source lower lid (fixed-camera x in pixels).',font=font,fill='#e8e8df')
sheet.save(dest/'lower-lid-light.png')
(dest/'lower-lid-light.json').write_text(json.dumps({'method':'Fixed registration; median cheek value 9–13 px below the photographed arc subtracted from the brightest sample in a narrow -5 to +6 px corridor about that arc. The profile uses a 1.8 px blur and five-column smoothing. Reported length spans 10% to 90% cumulative positive contrast. Wood and light both influence these measurements.','anchors':anchors.tolist(),'x':x.tolist(),'results':report},indent=2)+'\n')
print({k:{key:value for key,value in row.items() if key not in ('positive_luminance_profile','peak_y')} for k,row in report.items()})
