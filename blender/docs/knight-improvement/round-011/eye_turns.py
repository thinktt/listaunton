"""Place equal-scale views of each carved eye on the same sheet."""
from pathlib import Path
import hashlib,json,sys
from PIL import Image,ImageDraw,ImageFont
out=Path(sys.argv[1]);names=sys.argv[2:]
w,h=228,160;header=27
font=ImageFont.load_default(size=14)
for finish in ('clay','walnut'):
    sheet=Image.new('RGB',(w*3,len(names)*(h+header)),'#242625')
    draw=ImageDraw.Draw(sheet)
    for row,label in enumerate(names):
        folder=out/f'turn-eye-{label}'
        source=json.loads((folder/'source.json').read_bytes())
        for i,angle in enumerate(['-30','0','30']):
            path=folder/f'{finish}-{angle}.png'
            assert source['views'][path.name]==hashlib.sha256(path.read_bytes()).hexdigest()
            img=Image.open(path).convert('RGBA');img.thumbnail((w-3,h),Image.Resampling.LANCZOS)
            left=i*w;top=row*(h+header)
            draw.text((left+6,top+5),f'{label} / {finish} / {angle} deg',font=font,fill='#e9e8e1')
            sheet.paste(img,(left+2,top+header),img)
    sheet.save(out/f'eye-turns-{finish}.png')
