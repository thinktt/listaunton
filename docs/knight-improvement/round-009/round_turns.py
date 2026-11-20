"""Compare the backs and opposite flanks under the same neutral light."""
from pathlib import Path
import sys
from PIL import Image, ImageDraw
root=Path(sys.argv[1])
out=Image.new('RGB',(780,570),'#272a29')
draw=ImageDraw.Draw(out)
for col,k in enumerate(['parent','A','B']):
    for row,v in enumerate(['rear-quarter','far-side']):
        with Image.open(root/f'clay-{k}'/(v+'.png')) as im:
            im=im.convert('RGBA')
            alpha=im.getchannel('A').getbbox()
            if alpha is None:raise ValueError(v)
            tile=im.crop(alpha);tile.thumbnail((250,255),Image.Resampling.LANCZOS)
            x=260*col+(260-tile.width)//2
            y=285*row+23
            out.paste(tile,(x,y),tile)
        draw.text((260*col+5,285*row+5),f'{k} - {v}',fill='white')
out.save(root/'carving-turns.png')
