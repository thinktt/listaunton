"""Compose diagnostic contact sheets, leaving all source PNGs unchanged."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
root=Path(__file__).resolve().parents[2];a=root/'assets/knight';W=1254
placement=json.loads((a/'original-alignment.json').read_text());s=placement['scale'];x=placement['x'];y=placement['y']
reg=json.loads((a/'white-registration.json').read_text())
original=Image.open(a/'original.png').convert('RGBA').transform((W,W),Image.Transform.AFFINE,(s*300/W,0,x*3,0,s*300/W,y*3),Image.Resampling.BILINEAR)
white=Image.open(a/'white-original.png').convert('RGBA').transpose(Image.Transpose.FLIP_LEFT_RIGHT).transform((W,W),Image.Transform.AFFINE,(s*300/W/reg['scale'],0,(x-reg['x'])*3/reg['scale'],0,s*300/W/reg['scale'],(y-reg['y'])*3/reg['scale']),Image.Resampling.BILINEAR)
images=[original,Image.open(a/'ref.png').convert('RGBA'),Image.open(a/'render.png').convert('RGBA'),white]
labels=['Original black (300px source)','Selected black candidate 2','Reconstructed neutral clay','Original white, mirrored/aligned']
canvas=Image.new('RGB',(2000,620),'#111317');draw=ImageDraw.Draw(canvas)
for i,(image,label) in enumerate(zip(images,labels)):
 image=image.resize((660,660),Image.Resampling.LANCZOS).crop((70,100,570,640));canvas.paste(image,(i*500,45),image);draw.text((i*500+18,16),label,fill='#eeeeee')
canvas.save(a/'comparison.png')
views=Image.new('RGB',(1920,690),'#111317');draw=ImageDraw.Draw(views)
for i,label in enumerate(['side','front','opposite']):
 image=Image.open(a/f'view-{label}.png').convert('RGBA');views.paste(image,(i*640,40),image);draw.text((i*640+20,15),label.capitalize()+' volume inspection',fill='white')
views.save(a/'volume-inspection.png')
