"""Compare the carved eyes at identical native scale in walnut and neutral clay."""
import hashlib,json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageFont
out=Path(sys.argv[1])
labels=sys.argv[2:]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
w,h=324,220
sheet=Image.new('RGB',(w*len(labels),4*(h+27)),'#242725')
draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=14)
for col,label in enumerate(labels):
    directory=out/f'portraits-{label}'
    info=json.loads((directory/'source.json').read_text())
    for row,(finish,side) in enumerate([('walnut','near'),('walnut','far'),('clay','near'),('clay','far')]):
        source=directory/f'{finish}-{side}.png'
        assert sha(source)==info['views'][source.name]
        im=Image.open(source).convert('RGBA')
        if side=='far': im=ImageOps.mirror(im)
        im.thumbnail((w-6,h),Image.Resampling.LANCZOS)
        x=col*w;y=row*(h+27)
        draw.text((x+7,y+4),f'{label} / {finish} / {side} eye',font=font,fill='#eee9df')
        sheet.paste(im,(x+(w-im.width)//2,y+26),im)
sheet.save(out/'eye-portraits.png')
