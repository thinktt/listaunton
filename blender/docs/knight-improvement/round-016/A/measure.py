from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageFilter
sys.dont_write_bytecode=True
from study import pics,black,D
def measure():
 tag=sys.argv[-1];orig,ref=pics();parent=black(Image.open(D/'parent-wood.png'))
 if tag=='trial' or tag.startswith('scan-'):
  curr=parent.copy();curr.paste(black(Image.open(D/('trial-wood-fixed.png' if tag=='trial' else tag+'.png'))),(240,270))
 else:curr=black(Image.open(D/'wood.png'))
 x=np.arange(278,481);axis=[276,288,300,320,340,360,380,400,420,440,452,462,470,477,484];ys=[356,351,346,341,338,338,338,339,340,342,345,350,354,358,365];guide=np.rint(np.interp(x,axis,ys)).astype(int)
 X=np.arange(298,472)[:,None];Y=np.rint(np.interp(X[:,0],[298,320,340,360,380,400,420,440,452,462,471],[347,341,338,338,338,339,340,342,345,350,355])).astype(int)[:,None]+np.arange(-23,-4)
 out={};gray=np.array([.2126,.7152,.0722])
 for k,im in [('Original',orig),('Black 2',ref),('15A',parent),('16A',curr)]:
  smooth=np.asarray(im.filter(ImageFilter.GaussianBlur(1.35)),float);lum=smooth@gray;step=np.arange(-10,11);peak=guide+step[np.argmax(lum[guide[:,None]+step,x[:,None]],axis=1)]
  band=smooth[peak[:,None]+np.arange(-3,4),x[:,None]];ix=np.argsort(band@gray,axis=1)[:,-3:];rgb=np.take_along_axis(band,ix[:,:,None],1).mean(1)
  vals=np.asarray(im.filter(ImageFilter.GaussianBlur(3)),float)[Y,X]@gray;w=np.maximum(vals-np.percentile(vals,90),0)
  out[k]={'upper_glint_centroid':[(w*X).sum()/w.sum(),(w*Y).sum()/w.sum()],'sectors':{}}
  for label,l,h in [('rear',298,340),('middle',341,409),('front',410,450),('return',451,476)]:
   take=(x>=l)&(x<=h);out[k]['sectors'][label]={'peak_y_offset':float(np.median(peak[take]-guide[take])),'luminance':round(np.median(rgb[take]@gray),1),'red_minus_blue':round(np.median(rgb[take,0]-rgb[take,2]),1),'underface':round(np.median(lum[peak[take]+15,x[take]]),1)}
 out=json.loads(json.dumps(out));(D/(tag+'.json' if tag.startswith('scan-') else 'appearance.json')).write_text(json.dumps(out,indent=2)+'\n');print(out['16A'])
if __name__=='__main__':measure()
