"""Compact silhouettes, profiles, fixed material controls and true cross sections."""
from pathlib import Path
import json,sys,numpy as np
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(D))
from study import black,pics,table
def channels(file):return np.asarray(Image.open(file).convert('RGBA'))
def main():
 a,b=[channels(D/x) for x in ('parent-wood.png','wood.png')];sa,sb=[channels(D/x) for x in ('parent-side.png','wood-side.png')]
 def sil(z,q):
  p=z[:,:,3]>=128;v=q[:,:,3]>=128
  return {'iou':round(float((p&v).sum()/(p|v).sum()),8),'different_threshold_pixels':int((p!=v).sum())}
 masks={}
 ref=pics()[1];rgb=np.asarray(ref);shape=np.max(rgb,axis=2)>6
 trace=json.loads((D.parent/'round-011-judge/mane-hollow.json').read_bytes())['Black 2']['samples'];yy,xx=np.array([p[:2] for p in trace]).T
 mask=np.zeros(a.shape[:2],bool)
 for y in range(480,620):
  left=np.flatnonzero(shape[y])[0];right=np.interp(y,yy,xx);mask[y,round(left+.22*(right-left)):round(left+.75*(right-left))]=True
 masks['lower blade at 54 degrees']=mask;mask=np.zeros_like(mask);mask[450:511,460:561]=True;masks['eye at 54 degrees']=mask
 luma=np.array([.2126,.7152,.0722]);ca=a[:,:,:3]@luma;cb=b[:,:,:3]@luma
 report={'fixed_silhouette':sil(a,b),'side_silhouette':sil(sa,sb),'appearance_checks':{k:{'pixels':int(m.sum()),'parent_median':round(float(np.median(ca[m])),2),'16A_median':round(float(np.median(cb[m])),2),'median_abs_change':round(float(np.median(abs(ca-cb)[m])),2),'p95_abs_change':round(float(np.percentile(abs(ca-cb)[m],95)),2)} for k,m in masks.items()}}
 (D/'image-proof.json').write_text(json.dumps(report,indent=2)+'\n')
 # Geometry, material and illumination at the same camera.
 if (D/'common-studio-parent.png').exists():
  table('matched-light.png',[[('15A under its release studio',D/'parent-wood-fixed.png'),('16A under the 15A studio',D/'common-studio-parent.png'),('16A under its fitted cards',D/'common-studio-new.png')]],(290,169))
 if (D/'parent-clay-front.png').exists():
  table('full-turns.png',[[(label+' / '+name+' / '+k,D/f'{model}-{k}-{name}.png') for name in ['near','front-quarter','rear-quarter','rear','opposite']] for k in ['clay','wood'] for model,label in [('parent','15A'),('knight','16A')]],(203,153))
 pairs=[]
 for title,files in [('54 degrees',['parent-wood.png','wood.png']),('7 degrees',['parent-side.png','wood-side.png'])]:
  row=[]
  for t,f in zip(['15A','16A'],files):
   im=black(Image.open(D/f));row.append((t+' / '+title,im.crop(im.getbbox())))
  pairs.append(row)
 table('full-piece.png',pairs,(245,241))
 ref=pics()[1];src=R/'assets/knight';orig=black(Image.open(src/'original.png'));dim=orig.width;co=json.loads((src/'original-alignment.json').read_bytes());fac=co['scale']*dim/ref.width
 ext=(-co['x']*3/fac,-co['y']*3/fac,(dim-co['x']*3)/fac,(dim-co['y']*3)/fac)
 strip=[('Original',orig.resize((100,100),Image.Resampling.LANCZOS))]+[(k,im.resize((100,100),Image.Resampling.LANCZOS,box=ext)) for k,im in [('Black 2',ref),('15A',black(Image.open(D/'parent-wood.png'))),('16A',black(Image.open(D/'wood.png')))]]
 table('board.png',[strip],(105,100))
 q=json.loads((D/'native-proof.json').read_bytes());w,h=825,250;im=Image.new('RGB',(w,h),'#252925');dr=ImageDraw.Draw(im);font=ImageFont.load_default(size=13)
 for k,ix in enumerate([0,2,4]):
  x0=k*275+9;shift=15;dr.text((x0,8),f"Station {q['sections'][ix]['station']:.1f}",font=font,fill='white')
  for label,color in [('parent_sections','#879eaf'),('sections','#e9b25e')]:
   rec=q[label][ix];y,n=np.array(rec['y']),np.array(rec['r']);points=[(x0+15+yy*900,32-rr*790) for yy,rr in zip(y,n)];dr.line(points,fill=color,width=2)
  dr.text((x0,213),'15A in blue-grey   16A in amber',font=font,fill='white')
 im.save(D/'sections.png')
if __name__=='__main__':main()
