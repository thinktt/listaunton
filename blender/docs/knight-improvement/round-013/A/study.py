from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from audit_mission import registered,black
def build():
 f=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15);ref=registered()
 im=Image.new('RGB',(298*4,234*3),'#222724');pen=ImageDraw.Draw(im)
 def put(img,title,row,col,box=None):
    if box:img=img.crop(box)
    img=black(img.convert('RGBA'));img.thumbnail((296,203),Image.Resampling.LANCZOS)
    x=298*col;y=234*row;pen.text((x+5,y+4),title,font=f,fill='#eff0e4');im.paste(img,(x+(298-img.width)//2,y+27))
 for col,(k,title) in enumerate([('original','Original 100 px'),('selected','Black 2')]):
    put(ref[k].crop((429,435,600,525)).resize((316,180),Image.Resampling.LANCZOS),title,0,col)
 for iu,n in enumerate(['parent','knight']):
    label=['12B','13A'][iu]
    put(Image.open(D/f'detail-{n}-wood-fixed.png').crop((13,17,184,107)).resize((316,180),Image.Resampling.LANCZOS),label+' 54°',0,iu+2)
    for col,mat in enumerate(['clay','wood']):
      put(Image.open(D/f'detail-{n}-{mat}-side.png'),label+' side '+mat,iu+1,col)
      pic=Image.open(D/f'detail-{n}-{mat}-fixed.png').crop((13,17,184,107)).resize((316,180),Image.Resampling.LANCZOS)
      put(pic,label+' 54° '+mat,iu+1,col+2)
 im.save(D/'eye-study.png')
if __name__=='__main__':build()
