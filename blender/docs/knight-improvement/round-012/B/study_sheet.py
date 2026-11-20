from pathlib import Path
import sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from reference_images import black,registered
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15)
refs=registered();crops=[black(im.crop((175,374,436,716))) for im in refs.values()]
keys=list(map(int,sys.argv[1:])) if len(sys.argv)>1 else [-1,0,1,2,3]
W,H=209,268
sheet=Image.new('RGB',(W*(2+len(keys)),H*4+55),'#252726');dr=ImageDraw.Draw(sheet)
for i,name in enumerate(['Original','Black 2']+['Parent' if k<0 else f'Study {k}' for k in keys]):
    x=W*i;dr.text((x+4,3),name,fill='white',font=font)
    if i<2:
        sheet.paste(crops[i].resize((W,H)),(x,28));continue
    for j,mode in enumerate(['walnut','clay','side','far']):
        path=D/f'study-{keys[i-2]}-{mode}.png'
        if path.exists():sheet.paste(black(Image.open(path)).resize((W,H)),(x,28+j*H))
sheet.save(D/'development.png')
