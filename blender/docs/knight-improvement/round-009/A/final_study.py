"""Inspect the real eye and cheek in clay and in original/final walnut studios."""
import sys,json
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
from review import OUT,ROOT,put,load
A=ROOT/'assets/knight'
def main():
    sheet=Image.new('RGB',(1500,795),'#252729')
    fixed=[('Parent clay',OUT/'parent-fixed-clay.png'),('9A clay',OUT/'candidate-fixed-clay.png'),
           ('Parent walnut',OUT/'parent-wood.png'),('9A in parent studio',OUT/'matched-parent-fixed.png'),
           ('9A gallery studio',OUT/'wood.png')]
    side=[OUT/'parent-side-clay.png',OUT/'candidate-side-clay.png',OUT/'parent-wood-side.png',OUT/'matched-parent-side.png',OUT/'wood-side.png']
    for i,((lab,f),s) in enumerate(zip(fixed,side)):
        put(sheet,f,(417,437,571,541),(i*300,0),(298,216),lab+' at 54 degrees')
        put(sheet,s,(559,266,714,387),(i*300,232),(298,258),lab+' in side view')
    ref=load(A/'ref.png');q=json.loads((A/'original-alignment.json').read_text());k=q['scale']*300/1254
    orig=load(A/'original.png').transform(ref.size,Image.Transform.AFFINE,(k,0,q['x']*3,0,k,q['y']*3),Image.Resampling.BILINEAR)
    for i,(label,f) in enumerate([('Original',orig),('Black 2',ref),('Parent',load(OUT/'parent-wood.png')),
                                  ('9A in parent studio',load(OUT/'matched-parent-fixed.png')),('9A gallery',load(OUT/'wood.png'))]):
        put(sheet,f,(350,394,620,563),(i*300,495),(298,184),label+' carving')
        icon=f.resize((100,100),Image.Resampling.LANCZOS);sheet.paste(icon,(i*300+98,683),icon)
    sheet.save(OUT/'final-features.png')
if __name__=='__main__':main()
