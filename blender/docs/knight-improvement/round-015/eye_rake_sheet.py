"""Put three positions of the same softbox beside one another on each flank."""
from pathlib import Path
import hashlib,json,sys
from PIL import Image,ImageDraw,ImageFont,ImageOps
j=Path(sys.argv[1]);codes=sys.argv[2:];font=ImageFont.load_default(size=13)
w,h=228,154
for flank in ('near','far'):
    sheet=Image.new('RGB',(3*w,len(codes)*(h+24)+22),'#242924');d=ImageDraw.Draw(sheet)
    for i,k in enumerate(codes):
        folder=j/f'rake-{k}';record=json.loads((folder/'source.json').read_bytes())
        for c,name in enumerate(('from-poll','across','from-nose')):
            f=folder/f'{flank}-{name}.png'
            assert hashlib.sha256(f.read_bytes()).hexdigest()==record['views'][f.name]
            im=Image.open(f).convert('RGBA')
            if flank=='far':im=ImageOps.mirror(im)
            base=Image.new('RGBA',im.size,'#1f2322');base.alpha_composite(im)
            left=c*w;top=i*(h+24);d.text((left+4,top+4),k+' / light '+name.replace('-',' '),font=font,fill='#ebece2')
            sheet.paste(base.convert('RGB').resize((w-2,h),Image.Resampling.LANCZOS),(left,top+23))
    note='Far side mirrored for comparison.' if flank=='far' else 'Camera held at the near profile.'
    d.text((5,len(codes)*(h+24)+3),note+' Only the softbox moves.',font=font,fill='#d8dcd5')
    sheet.save(j/f'raking-eye-{flank}.png')
