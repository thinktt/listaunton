from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
r=Path(r'C:\Users\toby\Documents\Codex\2026-10-01\go-x20')
im=Image.open(r/'outputs/queen-hires/reference.png').convert('RGB')
d=ImageDraw.Draw(im)
for y in range(60,381,20):
 d.line([(300,y),(675,y)],fill=(50,190,200),width=1);d.text((677,y-5),str(y),fill='white')
for x in range(320,661,40):
 d.line([(x,40),(x,380)],fill=(50,190,200),width=1);d.text((x,380),str(x),fill='white')
im.crop((295,35,720,405)).resize((850,740)).save(r/'work/queen-hires/crown-grid.png')
