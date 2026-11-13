"""Test whole-neck wood replacement, allowing reference-visible pigment edits."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'history/rook-mission-066/assets/rook/pigment.png';assert hashlib.sha256((ROOT/'history/rook-mission-066/models/rook/rook-rebuilt.blend').read_bytes()).hexdigest()=='4e1557a8dbfd4e93c6c837403ffaed7b7f08e1565f063f576eb6e5c338856cf7'
a=np.asarray(Image.open(source).convert('RGB'),dtype=np.float32);m=np.load(ROOT/'build/rook-mission/067-neck-visibility/visibility.npz');x0,y0,x1,y1=m['box'];hidden=m['covered'];im=Image.fromarray((hidden*255).astype(np.uint8));soft=np.asarray(im.filter(ImageFilter.MinFilter(33)).filter(ImageFilter.GaussianBlur(16)),dtype=float)/255;soft*=hidden
V=1-(np.arange(y0,y1)+.5)/3072;t=np.minimum(np.clip((V-.61)/.035,0,1),np.clip((.77-V)/.035,0,1));t=t*t*(3-2*t);mask=soft*t[:,None];donor=a[y0+369:y1+369,x0:x1]
for n,scale in [(72,.563090750970072)]:
 out=ROOT/f'build/rook-mission/{n:03d}-neck-wood';out.mkdir(parents=True,exist_ok=True);result=a.copy();result[y0:y1,x0:x1]=a[y0:y1,x0:x1]*(1-mask[:,:,None])+donor*scale*mask[:,:,None];result=np.clip(result,0,255).round().astype(np.uint8);Image.fromarray(result).save(out/'pigment.png');protected_ok=bool(np.array_equal(result[y0:y1,x0:x1][m['protected']],a[y0:y1,x0:x1].astype(np.uint8)[m['protected']]))
 (out/'parameters.json').write_text(json.dumps({'source_atlas_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'donor_vertical_offset_pixels':369,'donor_srgb_scale':scale,'visible_triangle_texels_exact':protected_ok,'method':'Whole neck band: shifted nearby grain, darkened, smoothly blended inside smooth neck-region mask. Inferred wood, not observed source geometry.'},indent=2)+'\n')
Image.fromarray((mask*255).astype(np.uint8)).save(ROOT/'build/rook-mission/067-neck-visibility/whole-repair-mask.png')



