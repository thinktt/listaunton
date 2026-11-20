"""Match real clay views and annotate the guide sections used for the breast."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
shade=(35,38,38)
canvas=Image.new('RGB',(976,714),shade)
d=ImageDraw.Draw(canvas)
for col,(file,label) in enumerate([('parent','Accepted parent'),('B','Round 8B')]):
    for row,(view,caption) in enumerate([('near','Near side'),('far','Far side')]):
        image=Image.open(OUT/f'{file}-clay-{view}.png').convert('RGBA')
        crop=(97,151,537,465) if view=='near' else (92,151,532,465)
        image=image.crop(crop).resize((463,331),Image.Resampling.LANCZOS)
        x=col*488+12;y=row*352+25
        canvas.paste(image,(x,y),image)
        d.text((x,y-24),f'{label} · {caption}',font=font,fill='#eeeee7')
canvas.save(OUT/'roundness.png')
