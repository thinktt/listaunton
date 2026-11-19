"""Produce equal-camera side panels for the geometry style revision."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/bishop-mission/iteration-030'
font=ImageFont.load_default()
for path in ['C:/Windows/Fonts/arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
    if Path(path).is_file():font=ImageFont.truetype(path,22);break
im=Image.new('RGB',(880,930),'#1a1f24');d=ImageDraw.Draw(im)
for i,(name,label) in enumerate([('before','Previous'),('after','Revised')]):
    q=Image.open(DOC/name/'side.png').convert('RGBA').crop((260,20,740,980))
    q=q.resize((440,880),Image.Resampling.LANCZOS)
    im.paste(q,(440*i,45),q);d.text((440*i+24,13),label,font=font,fill='white')
im.save(DOC/'geometry-side-comparison.png')
print('Saved geometry-side-comparison.png')
