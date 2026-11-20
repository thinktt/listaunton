"""Build equal-registration presentation and compute alpha-mask and board statistics."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from evidence import open_rgb
D=Path(__file__).resolve().parent
def main():
    pairs=[('54-degree fixed','parent-wood.png','wood.png'),('7-degree side','parent-side.png','wood-side.png')]
    sheet=Image.new('RGB',(2*285,2*310),'#232723');p=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=14)
    facts={}
    for row,(name,bef,aft) in enumerate(pairs):
        a,b=(np.asarray(Image.open(D/q).convert('RGBA')) for q in (bef,aft));ma=a[:,:,3]>=128;mb=b[:,:,3]>=128
        da=np.abs(a[:,:,3].astype(int)-b[:,:,3].astype(int));diff=np.max(abs(a[:,:,:3].astype(int)-b[:,:,:3].astype(int)),axis=2)
        facts[name]={'canvas':list(a.shape[:2]),'silhouette_iou':float((ma&mb).sum()/(ma|mb).sum()),'threshold_128_changed_pixels':int((ma!=mb).sum()),'max_alpha_diff':int(da.max()),'median_abs_rgb_change_on_piece':float(np.median(diff[ma&mb]))}
        for i,(label,file) in enumerate([('13A',bef),('14A',aft)]):
            img=open_rgb(D/file);box=img.getbbox()
            tile=img.crop(box);tile.thumbnail((265,270),Image.Resampling.LANCZOS)
            sheet.paste(tile,(285*i+(285-tile.width)//2,310*row+31+(268-tile.height)//2))
            p.text((285*i+6,310*row+8),label+' / '+name,font=font,fill='white')
    sheet.save(D/'pair.png');(D/'silhouette.json').write_text(json.dumps(facts,indent=2)+'\n')
if __name__=='__main__':main()
