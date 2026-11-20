"""Equal-size crops in the untouched studio and one common, bilateral clay light."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,sys
D=Path(__file__).resolve().parent;R=D.parents[2];p=R/'assets/knight'
def black(im):
 im=im.convert('RGBA');return Image.alpha_composite(Image.new('RGBA',im.size,(0,0,0,255)),im).convert('RGB')
def reg():
 hi=black(Image.open(p/'ref.png'));lo=Image.open(p/'original.png').convert('RGBA');a=json.loads((p/'original-alignment.json').read_bytes());fac=a['scale']*300/hi.width
 return black(lo.transform(hi.size,Image.Transform.AFFINE,(fac,0,a['x']*3,0,fac,a['y']*3),Image.Resampling.BILINEAR)),hi
def main():
 tag=sys.argv[-1];lo,hi=reg()
 grid=Image.new('RGB',(265*4,171*3),'#222825');pen=ImageDraw.Draw(grid);f=ImageFont.load_default(size=14)
 def tile(im,i,j,name):
  im=black(im);w,h=im.size;scale=min(263/w,142/h);im=im.resize((round(w*scale),round(h*scale)),Image.Resampling.LANCZOS);x=i*265;y=j*171;grid.paste(im,(x+(265-im.width)//2,y+25+(142-im.height)//2));pen.text((x+5,y+4),name,fill='white',font=f)
 for i,(img,n) in enumerate([(lo,'Original'),(hi,'Black 2')]):tile(img.crop((457,449,561,508)),i,0,n)
 for k,n in enumerate(['parent',tag]):
  owl=Image.open(D/f'{n}-walnut-fixed.png');tile(owl.crop((28,34,132,93)),k+2,0,'14B' if n=='parent' else '15A')
  for i,mat in enumerate(['clay','walnut']):
   label='14B' if n=='parent' else '15A'
   tile(Image.open(D/f'{n}-{mat}-fixed.png').crop((22,24,147,98)),i,k+1,label+' 54° / '+mat)
   side=Image.open(D/f'{n}-{mat}-side.png');tile(side.crop((25,40,176,132)),i+2,k+1,label+' 7° / '+mat)
 grid.save(D/'eye-study.png')
if __name__=='__main__':main()
