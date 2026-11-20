"""Show both sides of the mane and its back at the same physical scale."""
from pathlib import Path
import hashlib,json,sys
from PIL import Image,ImageDraw,ImageFont,ImageOps
out=Path(sys.argv[1]);names=sys.argv[2:];w,h=220,254;font=ImageFont.load_default(size=14)
for material in ['walnut','clay']:
    sheet=Image.new('RGB',(w*3,len(names)*(h+27)),'#212624');d=ImageDraw.Draw(sheet)
    for row,name in enumerate(names):
        folder=out/f'back-{name}';meta=json.loads((folder/'source.json').read_bytes())
        for col,angle in enumerate(['near-quarter','back','far-quarter']):
            img=folder/f'{material}-{angle}.png';assert hashlib.sha256(img.read_bytes()).hexdigest()==meta['views'][img.name]
            im=Image.open(img).convert('RGBA')
            if angle=='far-quarter':im=ImageOps.mirror(im)
            im.thumbnail((w-4,h),Image.Resampling.LANCZOS);x=col*w;y=row*(h+27)
            sheet.paste(im,(x+(w-im.width)//2,y+25),im)
            desc={'near-quarter':'near quarter','back':'back','far-quarter':'far quarter, mirrored'}[angle]
            d.text((x+4,y+3),f'{name} / {desc}',font=font,fill='#e4e6de')
    sheet.save(out/f'back-{material}.png')
