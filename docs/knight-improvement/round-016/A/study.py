"""Compare the registered piece in the original studio and in real side geometry."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
D=Path(__file__).resolve().parent;R=D.parents[2];A=R/'assets/knight';sys.dont_write_bytecode=True
def black(im):
 im=im.convert('RGBA');return Image.alpha_composite(Image.new('RGBA',im.size,(0,0,0,255)),im).convert('RGB')
def pics():
 h=black(Image.open(A/'ref.png'));o=Image.open(A/'original.png').convert('RGBA');a=json.loads((A/'original-alignment.json').read_bytes());fac=a['scale']*300/h.width
 o=o.transform(h.size,Image.Transform.AFFINE,(fac,0,a['x']*3,0,fac,a['y']*3),Image.Resampling.BILINEAR);return black(o),h
def table(name,rows,size):
 w,h=size;out=Image.new('RGB',(w*len(rows[0]),(h+26)*len(rows)),'#252925');dr=ImageDraw.Draw(out);font=ImageFont.load_default(size=13)
 for j,row in enumerate(rows):
  for i,(title,im) in enumerate(row):
   if isinstance(im,Path):im=Image.open(im)
   im=black(im);sc=min((w-2)/im.width,h/im.height);im=im.resize((round(im.width*sc),round(im.height*sc)),Image.Resampling.LANCZOS);x=i*w;y=j*(h+26)
   out.paste(im,(x+(w-im.width)//2,y+24+(h-im.height)//2));dr.text((x+5,y+4),title,font=font,fill='white')
 out.save(D/name)
def main():
 o,h=pics();tag=sys.argv[-1];rows=[[(n,x.crop((249,281,517,415))) for n,x in [('Original sprite',o),('Black 2',h)]]]
 for k in ['wood','clay']:
  rows.append([(lab+' / '+k,black(Image.open(D/f'{file}-{k}-fixed.png')).crop((9,11,277,145))) for lab,file in [('15A','parent'),('16A',tag)]])
 table('crest-study.png',rows,(328,170))
 table('profile-study.png',[[(n+' / '+k,D/f'{file}-{k}-side.png') for n,file in [('15A','parent'),('16A',tag)]] for k in ['wood','clay']],(440,195))
if __name__=='__main__':main()
