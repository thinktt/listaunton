"""Compare actual queen renders with both sources and build shared-scale plates."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'assets/queen-projections';W=1254
manifest=json.loads((A/'variants.json').read_text(encoding='utf-8'))
reg=json.loads((ROOT/'assets/queen/original-reference-alignment.json').read_text(encoding='utf-8'));t=reg['scale'];dx=reg['offset_x'];dy=reg['offset_y']
original=Image.open(A/'original.png').convert('RGBA').transform((W,W),Image.Transform.AFFINE,(1/t,0,-dx/t,0,1/t,-dy/t),Image.Resampling.BILINEAR)
selected=Image.open(A/'reference.png').convert('RGBA')
def mask(im,render=False):
 a=np.array(im);m=a[:,:,3]>128
 if not render:m&=a[:,:,:3].max(2)>12
 return m
def metrics(a,b):
 union=(a|b).sum();inter=(a&b).sum();errs=[]
 for m1,m2 in [(a,b),(a.T,b.T)]:
  present=m1.any(1)&m2.any(1);lo1=m1.argmax(1);lo2=m2.argmax(1);hi1=m1.shape[1]-1-m1[:,::-1].argmax(1);hi2=m2.shape[1]-1-m2[:,::-1].argmax(1)
  errs.extend(abs(lo1[present]-lo2[present]));errs.extend(abs(hi1[present]-hi2[present]))
 return dict(iou=float(inter/union),mean_boundary_error_original_px=float(np.mean(errs)/t),p95_boundary_error_original_px=float(np.percentile(errs,95)/t))
def over_black(im):
 bg=Image.new('RGBA',im.size,'black');bg.alpha_composite(im);return bg.convert('RGB')
def edge(m):
 im=Image.fromarray((m*255).astype('uint8'));return np.array(im)!=np.array(im.filter(ImageFilter.MinFilter(3)))
def contour(a,b):
 rgb=np.zeros((W,W,3),dtype=np.uint8);rgb[a|b]=[38,42,48];rgb[edge(a)]=[20,210,245];rgb[edge(b)]=[255,169,40];return Image.fromarray(rgb)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20) if Path('C:/Windows/Fonts/segoeui.ttf').exists() else ImageFont.load_default()
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16) if Path('C:/Windows/Fonts/segoeui.ttf').exists() else ImageFont.load_default()
plate=Image.new('RGB',(7*260,450),(18,23,30));d=ImageDraw.Draw(plate)
overlays=Image.new('RGB',(7*300,680),(18,23,30));od=ImageDraw.Draw(overlays)
report={'method':'Actual alpha silhouettes at saved candidate cameras. Original sprite registered by the existing accepted queen alignment; boundary differences expressed in original 300px units. Cyan reference/orange model contours.','variants':[]}
for k,row in enumerate(manifest['variants']):
 folder=ROOT/row['assetDir'];render=Image.open(folder/'render.png').convert('RGBA');m=mask(render,True);om=mask(original);sm=mask(selected)
 data={'id':row['id'],'elevation':row['elevation'],'original':metrics(m,om),'selected':metrics(m,sm),'height':row['height'],'baseWidth':row['baseWidth'],'heightToBaseWidth':row['heightToBaseWidth']}
 # The coarse sprite only weakly identifies scallop interiors. Report regions separately.
 for name,cut in [('head',(0,500)),('body',(500,W))]:
  y1,y2=cut;data[name]={'original':metrics(m[y1:y2],om[y1:y2]),'selected':metrics(m[y1:y2],sm[y1:y2])}
 (folder/'render-check.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8');report['variants'].append(data)
 profile=Image.open(folder/'profile.png').convert('RGBA');bg=Image.new('RGBA',profile.size,(27,34,43,255));bg.alpha_composite(profile);plate.paste(bg.convert('RGB').resize((250,375),Image.Resampling.LANCZOS),(k*260+5,35))
 d.text((k*260+12,8),row['label'],font=font,fill='white');d.text((k*260+12,416),f"Height / base {row['heightToBaseWidth']:.3f}",font=small,fill=(174,183,197))
 overlay=Image.blend(over_black(original),over_black(render),.5);overlay.save(folder/'overlay-original.png');contour(om,m).save(folder/'contour-original.png');contour(sm,m).save(folder/'contour-selected.png')
 od.text((k*300+10,8),row['label'],font=font,fill='white');overlays.paste(overlay.resize((300,300),Image.Resampling.LANCZOS),(k*300,40));overlays.paste(contour(om,m).resize((300,300),Image.Resampling.LANCZOS),(k*300,340));od.text((k*300+10,643),f"Original IoU {data['original']['iou']:.4f}",font=small,fill=(174,183,197))
base=Image.open(ROOT/'history/queen-before-54-finish/assets/queen/queen-matched.png').convert('RGBA');low=Image.open(A/manifest['baseline']/'render.png').convert('RGBA')
report['reduced_render_vs_dense']=metrics(mask(base,True),mask(low,True));report['reduced_render_vs_dense']['silhouette_xor_pixels']=int(np.count_nonzero(mask(base,True)^mask(low,True)))
report['limitations']='Higher elevations require a taller queen and increasingly change the visible ring ellipses and crown cavities. Bounded fitting preserves the accepted crown topology and chunky carving, so endpoint fits deliberately retain residual mismatch. A single shaded sprite cannot uniquely identify hidden depth or camera elevation.'
plate.save(A/'profiles.png');overlays.save(A/'original-comparison.png');(A/'render-analysis.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
