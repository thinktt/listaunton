"""Read the color, distribution of light, and walnut figure on the poll bevel."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont

root=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);codes=sys.argv[3:]
build=root/'build/knight-mission';out=build/f'round-{n:03}-judge'
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import black,registered
ref=registered()
images={'Original black':ref['original'],'Black 2':ref['selected'],'Parent':Image.open(root/'assets/knight/render.png')}
for k in codes:images[k]=Image.open(build/f'improvement-{n:03}-{k}/wood.png')
for tag,f in [('Pigment','pigment'),('Neutral polish','polish')]:
    folder=out/'passes-parent'
    if (folder/(f+'.png')).exists():images[tag]=Image.open(folder/(f+'.png'))
gray=np.array([.2126,.7152,.0722])
# The silhouette is aligned before judging. The broad search window follows the
# full photographed crest from the rear sweep to the point under the forehead.
cx=np.array([276,288,300,320,340,360,380,400,420,440,452,462,470,477,484])
cy=np.array([356,351,346,341,338,338,338,339,340,342,345,350,354,358,365])
xs=np.arange(278,481)
guide=np.rint(np.interp(xs,cx,cy)).astype(int)
parts=[('rear',298,340),('middle',341,409),('front shoulder',410,450),('return',451,476)]
report={};w,h=290,145;font=ImageFont.load_default(size=13)
canvas=Image.new('RGB',(w*len(images),h*2+57),'#222624');draw=ImageDraw.Draw(canvas)
for col,(name,pic) in enumerate(images.items()):
    im=black(pic.convert('RGBA'))
    smooth=np.asarray(im.filter(ImageFilter.GaussianBlur(1.6)),float);lum=smooth@gray
    peak=guide+np.array([np.argmax(lum[y-10:y+11,x])-10 for x,y in zip(xs,guide)])
    # Per column, look at the three brightest pixels in the narrow bevel cross section.
    band=np.arange(-3,4)
    rgb=smooth[peak[:,None]+band,xs[:,None]]
    rank=np.argsort(rgb@gray,axis=1)[:,-3:]
    rgb=np.take_along_axis(rgb,rank[:,:,None],axis=1).mean(axis=1)
    top=np.asarray(im.filter(ImageFilter.GaussianBlur(.7)),float)@gray
    local=np.asarray(im.filter(ImageFilter.GaussianBlur(3.5)),float)@gray
    record={}
    for label,x0,x1 in parts:
        m=(xs>=x0)&(xs<=x1)
        shade=lum[peak[m]+15,xs[m]]
        level=rgb[m]@gray
        rec={'median_peak_luma':round(float(np.median(level)),2),'median_peak_rgb':np.median(rgb[m],axis=0).round(1).tolist(),
          'median_underface_luma_15px_below':round(float(np.median(shade)),2),
          'median_bevel_y_offset_px':round(float(np.median(peak[m]-guide[m])),2),
          'warmth_R_minus_B':round(float(np.median(rgb[m,0]-rgb[m,2])),2)}
        # Within each broad planar face, not the thin central specular strand.
        for face,yr in [('cap',np.arange(-25,-12)),('underface',np.arange(9,25))]:
            y=guide[m,None]+yr[None,:];x=xs[m,None]
            residual=top[y,x]-local[y,x]
            rec[face+'_pore_contrast']=round(float(np.sqrt(np.mean((residual/np.maximum(15,local[y,x]))**2))),4)
        record[label]=rec
    # Retain an untraced crop above the identical annotated one.
    box=(246,285,500,408);left=col*w
    tile=im.crop(box).resize((w-3,h),Image.Resampling.LANCZOS)
    draw.text((left+5,4),name,font=font,fill='#ebece2')
    canvas.paste(tile,(left,24));canvas.paste(tile,(left,h+30))
    pts=[(left+(x+.5-box[0])*(w-3)/(box[2]-box[0]),h+30+(y+.5-box[1])*h/(box[3]-box[1])) for x,y in zip(xs,peak)]
    draw.line(pts,fill='#77bbac',width=1)
    report[name]=record
draw.text((4,2*h+37),'The green trace follows the reflective edge of the mane above the swept ear.',font=font,fill='#dedfd5')
canvas.save(out/'crest-color.png')
(out/'crest-color.json').write_text(json.dumps({'method':'At each registered x sample, trace the brightest smoothed pixel within 10px of the source bevel, then average the three brightest pixels within 3px. Measure warm color and relative grain contrast on either side of the bevel. Fine-grain values from the enlarged original are resolution-limited.','results':report},indent=2)+'\n')
for k,v in report.items():
    print(k,[(s,o['median_peak_luma'],o['warmth_R_minus_B'],o['cap_pore_contrast'],o['underface_pore_contrast']) for s,o in v.items()])
