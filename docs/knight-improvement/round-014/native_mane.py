"""Compare the mane on the actual Lichess grid and at a 100px playing size."""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np

root=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);codes=sys.argv[3:]
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import black,registered,silhouette
assets=root/'assets/knight';build=root/'build/knight-mission';out=build/f'round-{n:03}-judge'
refs=registered();source=Image.open(assets/'original.png').convert('RGBA')
align=json.loads((assets/'original-alignment.json').read_bytes())
scale=align['scale']*source.width/refs['selected'].width;ox,oy=align['x']*3,align['y']*3
extent=(-ox/scale,-oy/scale,(source.width-ox)/scale,(source.height-oy)/scale)
items={'Lichess PNG':source}
for name,pic in [('Black 2',refs['selected']),('Parent',Image.open(assets/'render.png'))]+[(k,Image.open(build/f'improvement-{n:03}-{k}/wood.png')) for k in codes]:
    items[name]=pic.convert('RGBA').resize(source.size,Image.Resampling.LANCZOS,box=extent)
trace=json.loads((build/'round-011-judge/mane-hollow.json').read_bytes())['Black 2']['samples']
ty,tx=np.transpose([a[:2] for a in trace])
shape=silhouette(refs['selected'],True)
mask=np.zeros(shape.shape,np.uint8)
for y in range(462,623):
    edge=np.flatnonzero(shape[y])[0];inside=np.interp(y,ty,tx);span=inside-edge
    mask[y,round(edge+.15*span):round(edge+1.12*span)]=255
native_mask=Image.fromarray(mask).resize(source.size,Image.Resampling.LANCZOS,box=extent)
cols=['Lichess PNG','Black 2','Parent',*codes]
font=ImageFont.load_default(size=13);w=158
sheet=Image.new('RGB',(len(cols)*w,346),'#242822')
draw=ImageDraw.Draw(sheet)
crops={};data={}
aabb=(172,449,313,631)
native_box=tuple(round(z*scale+(ox,oy)[i%2]) for i,z in enumerate(aabb))
for i,name in enumerate(cols):
    x=i*w
    draw.text((x+6,4),name,font=font,fill='#edece2')
    base=black(items[name]);board=base.resize((100,100),Image.Resampling.LANCZOS)
    sheet.paste(board,(x+(w-100)//2,24))
    crops[name]={}
    for key,size,place,h in [('native',300,148,110),('playing',100,279,52)]:
        image=base.resize((size,size),Image.Resampling.LANCZOS)
        coords=tuple(round(v*size/300) for v in native_box)
        cut=image.crop(coords)
        zoom=round(h/cut.height)
        tile=cut.resize((cut.width*zoom,cut.height*zoom),Image.Resampling.NEAREST)
        draw.text((x+5,place-20),f'{size} px / mane',font=font,fill='#d2d9cd')
        sheet.paste(tile,(x+(w-tile.width)//2,place))
        m=np.asarray(native_mask.resize((size,size),Image.Resampling.LANCZOS))>240
        crops[name][key]=np.asarray(image,dtype=float)[m]
for name,sizes in crops.items():
    data[name]={}
    for tag,v in sizes.items():
        metrics={}
        for ref in ('Lichess PNG','Black 2'):
            target=crops[ref][tag]
            lum=v@[.2126,.7152,.0722];source_lum=target@[.2126,.7152,.0722]
            metrics[ref]={'rgb_mae':round(float(abs(v-target).mean()),2),
                          'mean_rgb_bias':np.round((v-target).mean(axis=0),2).tolist(),
                          'luminance_correlation':round(float(np.corrcoef(lum,source_lum)[0,1]),3)}
        data[name][tag]={'pixels':len(v),'against':metrics}
sheet.save(out/'mane-native.png')
(out/'mane-native.json').write_text(json.dumps({'method':'Compare the original PNG and registered model after a single Lanczos reduction onto the actual 300px sprite raster. The 100px grids simulate a playing square. Sample the broad mane from 15% of its width to just beyond the dark inside edge. Percentages exclude the outer contour. All crops use nearest-neighbor enlargement for display.','results':data},indent=2)+'\n')
for k in cols:print(k,data[k]['native']['against'])
