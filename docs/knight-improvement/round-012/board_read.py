"""Compare sprites at 1x and 2x on common squares, honoring the saved registration."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw
root=Path(sys.argv[1]).resolve()
number=int(sys.argv[2])
build=root/'build/knight-mission'
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import registered
refs=registered()
def read(path):
    with Image.open(path) as im:
        return im.convert('RGBA')
images={'Lichess':refs['original'],'Black 2':refs['selected'],'Parent':read(root/'assets/knight/render.png')}
for name in sys.argv[3:]:
    images[name]=read(build/f'improvement-{number:03}-{name}'/'wood.png')
# Lichess 3D sprites extend above their square. Apply one crop to every
# registered image so their scales, centers and baseline remain directly comparable.
crop=(113,205,868,1090)
out=Image.new('RGB',(len(images)*166,324),'#191a18')
d=ImageDraw.Draw(out)
for i,(name,img) in enumerate(images.items()):
    d.text((i*166+8,5),name,fill='white')
    tile=img.crop(crop)
    for y,box,bg in [(27,(78,91),'#55574f'),(125,(152,178),'#6f7067')]:
        tile2=tile.resize(box,Image.Resampling.LANCZOS)
        x=i*166+(166-box[0])//2
        d.rectangle((i*166,y,i*166+165,y+box[1]),fill=bg)
        out.paste(tile2,(x,y),tile2)
dest=build/f'round-{number:03}-judge'
dest.mkdir(exist_ok=True)
out.save(dest/'board-read.png')
