"""Fixed-size diagnostic crops and unchanged registered socket measurements."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('renders',nargs='+');p.add_argument('--out',required=True)
a=p.parse_args();out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
paths=[('Reference',ROOT/'assets/bishop/reference.png')]+[(Path(n).stem,ROOT/n) for n in a.renders]
crop=(350,735,640,870);columns=min(3,len(paths))
canvas=Image.new('RGB',(290*columns,440*((len(paths)+columns-1)//columns)),'#161a1f');draw=ImageDraw.Draw(canvas)
ref=np.array(Image.open(paths[0][1]).convert('RGBA'),dtype=float);records={}
for i,(name,path) in enumerate(paths):
    img=Image.open(path).convert('RGBA');assert img.size==(1254,1254)
    x=i%columns*290;y=i//columns*440
    canvas.paste(img.crop(crop).convert('RGB'),(x,y+30))
    canvas.paste(img.crop((410,775,600,825)).convert('RGB').resize((285,75)),(x,y+185))
    canvas.paste(img.crop((480,795,560,825)).convert('RGB').resize((280,105)),(x,y+285))
    draw.text((x+5,y+8),name,fill='white')
    values=np.array(img,dtype=float);r=ref[735:870,350:640];v=values[735:870,350:640]
    mask=(r[:,:,3]>127)&(v[:,:,3]>(127 if i==0 else 254))&(r[:,:,:3].max(2)>12)
    assert mask.sum()>100
    error=float(abs(v[mask,:3]-r[mask,:3]).mean())
    records[name]={'path':str(path.relative_to(ROOT)).replace('\\','/'),'crop_rgb_mae':error,'pixels':int(mask.sum())}
    draw.text((x+5,y+405),f'RGB MAE {error:.2f}',fill='white')
canvas.save(out/'comparison.png')
(out/'diagnostic-metrics.json').write_text(json.dumps({'note':'Fixed crops, no realignment or grading. These are image diagnostics, not fidelity scores.','renders':records},indent=2)+'\n')
print(json.dumps(records))
