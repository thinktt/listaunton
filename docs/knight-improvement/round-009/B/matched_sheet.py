from pathlib import Path
from PIL import Image,ImageDraw
from review import im,put,BG
D=Path(__file__).resolve().parent
for mode in ['walnut','clay']:
    canvas=Image.new('RGB',(1056,544),BG)
    for j,prefix in enumerate(['parent','B']):
        for i,view in enumerate(['near','opposite','rear','front']):
            put(canvas,im(f'matched-{prefix}-{view}-{mode}.png'),(155,50,1095,1210),i*264,j*272,264,272,prefix+' · '+view+' · '+mode)
    canvas.save(D/f'matched-{mode}-turns.png')
