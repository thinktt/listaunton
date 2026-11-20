"""Compare the eye on the original Lichess PNG pixel grid at 300 and 100 pixels."""
from pathlib import Path
import json,sys
from PIL import Image,ImageDraw,ImageFont
import numpy as np
root=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);labels=sys.argv[3:]
asset=root/'assets/knight';build=root/'build/knight-mission';out=build/f'round-{n:03}-judge'
src=Image.open(asset/'original.png').convert('RGBA')
hi=Image.open(asset/'ref.png').convert('RGBA')
alignment=json.loads((asset/'original-alignment.json').read_bytes())
scale=alignment['scale']*src.width/hi.width
ox=alignment['x']*3;oy=alignment['y']*3
extent=(-ox/scale,-oy/scale,(src.width-ox)/scale,(src.height-oy)/scale)
def match(photo):
    # High-res render to original grid in one Lanczos reduction.
    return photo.convert('RGBA').resize(src.size,Image.Resampling.LANCZOS,box=extent)
items={'Lichess PNG':src,'Black 2':match(hi),'Parent':match(Image.open(asset/'render.png'))}
for label in labels:items[label]=match(Image.open(build/f'improvement-{n:03}-{label}/wood.png'))
box=(round(443*scale+ox),round(443*scale+oy),round(569*scale+ox),round(516*scale+oy))
w=164
sheet=Image.new('RGB',(len(items)*w,376),'#272b28');d=ImageDraw.Draw(sheet);f=ImageFont.load_default(size=13)
def opaque(im):
    bg=Image.new('RGBA',im.size,'#717268');bg.alpha_composite(im);return bg.convert('RGB')
rec={}
for col,(name,native) in enumerate(items.items()):
    x=col*w
    canvas=opaque(native);board=canvas.resize((100,100),Image.Resampling.LANCZOS)
    d.text((x+5,4),name,font=f,fill='white')
    sheet.paste(board,(x+5,25))
    d.text((x+5,134),'Native sprite grid / eye',font=f,fill='#d7d8d2')
    cut=canvas.crop(box)
    sheet.paste(cut.resize((cut.width*5,cut.height*5),Image.Resampling.NEAREST),(x+5,153))
    d.text((x+5,251),'100 px sprite / eye',font=f,fill='#d7d8d2')
    b=tuple(round(k/3) for k in box)
    tiny=board.crop(b)
    sheet.paste(tiny.resize((tiny.width*13,tiny.height*13),Image.Resampling.NEAREST),(x+5,275))
    rec[name]={}
    for key,img in [('300',cut),('100',tiny)]:
        lum=np.array(img,float)@[.2126,.7152,.0722]
        rec[name][key]=lum
report={}
for name,sizes in rec.items():
    report[name]={}
    for label,patch in sizes.items():
        ref=rec['Lichess PNG'][label]
        report[name][label]={'correlation_with_original':round(float(np.corrcoef(patch.ravel(),ref.ravel())[0,1]),4),'luma_mae_to_original':round(float(np.abs(patch-ref).mean()),3)}
sheet.save(out/'eye-native-grid.png')
(out/'eye-native-grid.json').write_text(json.dumps({'source_box':box,'source_size':src.size,'method':'Downsample once to original registered 300-pixel PNG grid, then to 100 pixels. Crop the same window through the eye. The small images shown enlarged use nearest-neighbor sampling.','stats':report},indent=2)+'\n')
print(report)
