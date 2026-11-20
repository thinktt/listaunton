"""Compare light-to-dark transitions that both source pictures resolve on the original pixel grid."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont

root=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);codes=sys.argv[3:]
b=root/'build/knight-mission';j=b/f'round-{n:03}-judge';assets=root/'assets/knight'
src=Image.open(assets/'original.png').convert('RGBA')
hi=Image.open(assets/'ref.png').convert('RGBA')
a=json.loads((assets/'original-alignment.json').read_bytes());scale=a['scale']*src.width/hi.width
ox,oy=a['x']*3,a['y']*3
extent=(-ox/scale,-oy/scale,(src.width-ox)/scale,(src.height-oy)/scale)
def opaque(img):
    canvas=Image.new('RGBA',img.size,'black');canvas.alpha_composite(img);return canvas.convert('RGB')
def native(img):
    return opaque(img.convert('RGBA').resize(src.size,Image.Resampling.LANCZOS,box=extent))
pics={'Original black':opaque(src),'Black 2':native(hi),'Parent':native(Image.open(assets/'render.png'))}
for c in codes:pics[c]=native(Image.open(b/f'improvement-{n:03}-{c}/wood.png'))
poly=[(466,467),(479,460),(501,459),(520,463),(539,470),(561,486),(558,494),
      (537,498),(524,502),(495,505),(477,500),(470,491)]
# Use centers of actual Lichess pixels, with the supplied signed registration.
mask_img=Image.new('L',src.size);pen=ImageDraw.Draw(mask_img)
pen.polygon([(round(x*scale+ox-.5),round(y*scale+oy-.5)) for x,y in poly],fill=255)
inside=np.asarray(mask_img)>0;yy,xx=np.nonzero(inside)
lights={k:np.array(p,dtype=float)@[.2126,.7152,.0722] for k,p in pics.items()}
saved=[];result={}
for dy,dx in [(0,1),(1,0)]:
    within=inside[yy+dy,xx+dx]
    x,y=xx[within],yy[within]
    ds=lights['Original black'][y+dy,x+dx]-lights['Original black'][y,x]
    dh=lights['Black 2'][y+dy,x+dx]-lights['Black 2'][y,x]
    ok=(abs(ds)>=3)&(abs(dh)>=6)&(np.sign(ds)==np.sign(dh))
    for i in np.flatnonzero(ok):saved.append((int(x[i]),int(y[i]),dx,dy,float(ds[i]),float(dh[i])))
assert len(saved)>10
x,y,dx,dy=[np.array([v[k] for v in saved],int) for k in range(4)]
target=np.array([v[4] for v in saved]);weight=np.minimum(abs(target),15)
font=ImageFont.load_default(size=13);w,h=202,121
sheet=Image.new('RGB',(w*len(pics),2*h+67),'#232825');d=ImageDraw.Draw(sheet)
box=(int(xx.min()-2),int(yy.min()-3),int(xx.max()+3),int(yy.max()+3))
for i,(key,pic) in enumerate(pics.items()):
    lum=lights[key];delta=lum[y+dy,x+dx]-lum[y,x]
    same=np.sign(delta)==np.sign(target)
    result[key]={'agreeing_edges':int(same.sum()),'available_edges':int(len(same)),'source_agreement_percent':round(float(100*same.mean()),2),
                 'weighted_agreement_percent':round(float(100*weight[same].sum()/weight.sum()),2),
                 'reversed_with_contrast_over_3':int(((~same)&(abs(delta)>=3)).sum())}
    tile=pic.crop(box).resize((w-2,h),Image.Resampling.NEAREST);left=i*w
    d.text((left+5,4),key,font=font,fill='#edf0e5')
    sheet.paste(tile,(left,24));sheet.paste(tile,(left,h+30))
    for px,py,vx,vy,agree in zip(x,y,dx,dy,same):
        xp=left+(px+.5+vx/2-box[0])*(w-2)/(box[2]-box[0])
        yp=h+30+(py+.5+vy/2-box[1])*h/(box[3]-box[1])
        d.line((xp-vx*1.8,yp-vy*1.8,xp+vx*1.8,yp+vy*1.8),fill='#87c9ac' if agree else '#f28773',width=2)
d.text((5,2*h+41),'Shared source edges at native resolution. Green agrees with their contrast direction. Coral reverses it.',font=font,fill='#dce3d7')
sheet.save(j/'eye-shared-edges.png')
(j/'eye-shared-edges.json').write_text(json.dumps({'method':'In the same eye polygon on the unscaled 300-pixel sprite, select directly neighboring pixels with at least 3 levels of luma contrast in the original and 6 in the registered enlargement, with the same sign. Evaluate candidate contrast direction on those exact pixel pairs. The fixed thresholds exclude ambiguous source-level details. This describes only the source-supported edges, not profile beauty or anatomy.',
 'native_polygon_pixels':int(inside.sum()),'source_pairs':saved,'results':result},indent=2)+'\n')
print(result)
