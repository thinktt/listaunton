from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;S=P.parents[2];T=P/'wood-trial'
reg=json.loads((S/'assets/queen/original-reference-alignment.json').read_text());s=reg['scale']
def original(color):return Image.open(S/f'references/lichess-staunton-3d/{color}-Queen.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(1/s,0,-reg['offset_x']/s,0,1/s,-reg['offset_y']/s),Image.Resampling.BILINEAR)
def bg(im):
    out=Image.new('RGBA',im.size,(16,21,28,255));out.alpha_composite(im.convert('RGBA'));return out.convert('RGB')
images=[original('Black'),original('White'),Image.open(S/'assets/queen/reference.png'),Image.open(P/'current-snapshot/queen-brown.png'),Image.open(T/'fixed-wood.png')]
names=['Original black','Original white','Selected high-res','Checkpoint 33','Flatter shelf trial']
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
sheet=Image.new('RGB',(5*400,430),(16,21,28));d=ImageDraw.Draw(sheet)
for j,(name,im) in enumerate(zip(names,images)):
    d.text((j*400+10,10),name,fill='white',font=font);sheet.paste(bg(im).crop((315,610,650,890)).resize((400,334)),(j*400,50))
sheet.save(P/'socket-wood-comparison.png')
side=Image.new('RGB',(820,680),(16,21,28));d=ImageDraw.Draw(side)
for j,(name,folder) in enumerate([('Checkpoint 33',P/'current-snapshot'),('Flatter shelf trial',T)]):
    d.text((j*410+10,10),name,fill='white',font=font)
    for row,filename in enumerate(['queen-wood-profile.png','queen-finished-profile.png'] if j==0 else ['side-wood.png','side-neutral.png']):
        im=bg(Image.open(folder/filename)).crop((145,570,455,810)).resize((400,310));side.paste(im,(j*410,40+row*320))
side.save(P/'socket-wood-side.png')
