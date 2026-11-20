"""Native-pixel finish details at a common twofold scale, with no image fitting."""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('renders',nargs='+');p.add_argument('--out',required=True)
a=p.parse_args();items=[('Selected white 3',ROOT/'assets/bishop/reference.png')]+[(Path(v).parent.name,ROOT/v) for v in a.renders]
regions=[('Head varnish',(475,280,580,430)),('Base varnish',(505,925,635,1030)),('Socket',(435,765,585,830))]
canvas=Image.new('RGB',(320*len(items),820),'#151a20');d=ImageDraw.Draw(canvas)
for i,(name,path) in enumerate(items):
    im=Image.open(path).convert('RGB');d.text((i*320+8,10),name,fill='white');y=40
    for label,box in regions:
        d.text((i*320+8,y),label,fill='white');y+=22
        tile=im.crop(box);tile=tile.resize((tile.width*2,tile.height*2),Image.Resampling.NEAREST)
        canvas.paste(tile,(i*320+8,y));y+=tile.height+24
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);canvas.save(out)
