"""Primary features from the reopened gallery pair, registered sources and studio control."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
from review import put,load,OUT,ROOT
A=ROOT/'assets/knight'
def main():
    ref=load(A/'ref.png')
    q=json.loads((A/'original-alignment.json').read_text());k=q['scale']*300/1254
    sprite=load(A/'original.png').transform(ref.size,Image.Transform.AFFINE,
            (k,0,q['x']*3,0,k,q['y']*3),Image.Resampling.BILINEAR)
    fixed=[('Original',sprite),('Black 2',ref),('Parent',A/'render.png'),('A',OUT/'wood.png'),
           ('A in parent studio',OUT/'matched-parent-fixed.png')]
    canvas=Image.new('RGB',(1450,776),'#252729')
    for i,(label,p) in enumerate(fixed):
        put(canvas,p,(195,275,542,440),(i*290,0),(288,173),label+' upper head')
        put(canvas,p,(443,443,561,516),(i*290,181),(288,181),label+' eye')
        im=p if isinstance(p,Image.Image) else load(p)
        icon=im.resize((100,100),Image.Resampling.LANCZOS)
        canvas.paste(icon,(i*290+89,362),icon)
    side=[('Parent clay',OUT/'parent-side-clay.png'),('A clay',OUT/'candidate-side-clay.png'),
          ('Parent walnut',A/'guide-render.png'),('A walnut',OUT/'wood-side.png'),
          ('A walnut in parent studio',OUT/'matched-parent-side.png')]
    for i,(label,p) in enumerate(side):
        put(canvas,p,(455,127,686,256),(i*290,476),(288,142),label+' crown')
        put(canvas,p,(574,279,707,375),(i*290,617),(288,158),label+' eye')
    canvas.save(OUT/'final-features.png')
if __name__=='__main__':main()
