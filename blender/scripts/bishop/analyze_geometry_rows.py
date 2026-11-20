"""Unchanged-registration exterior row diagnostics; not an interior-form score."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--out',default='build/bishop-mission/144-surface-audit')
p.add_argument('--render',default='assets/bishop/render.png');a=p.parse_args()
out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
refs={'selected':Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA')}
for name,image,alignment in [('white','original.png','original-alignment.json'),('black','black-original.png','black-alignment.json')]:
    al=json.loads((ROOT/'assets/bishop'/alignment).read_text());s=al['scale']*300/1254
    refs[name]=Image.open(ROOT/'assets/bishop'/image).convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(s,0,al['x']*3,0,s,al['y']*3),Image.Resampling.BILINEAR)
render=np.array(Image.open(ROOT/a.render).convert('RGBA'));mask=render[:,:,3]>127
regions={'button':[130,240],'upper_head':[240,325],'lower_head':[325,448],'upper_collar':[448,515],
    'middle_collar':[515,566],'lower_collar':[566,609],'visible_stem':[609,629],
    'rear_base_shoulder':[629,795],'base_sides':[795,1020],'foot':[1020,1140]}
reports={};row_data={}
for name,ref in refs.items():
    ar=np.array(ref);rm=(ar[:,:,3]>127)&(ar[:,:,:3].max(2)>12)
    rows=[]
    for y in range(1254):
        r=np.flatnonzero(rm[y]);m=np.flatnonzero(mask[y])
        if not len(r) or not len(m):continue
        rows.append([y,int(r[0]),int(r[-1]),int(m[0]),int(m[-1])])
    values=np.array(rows);rr={}
    for region,(y0,y1) in regions.items():
        v=values[(values[:,0]>=y0)&(values[:,0]<y1)]
        error=v[:,3:5]-v[:,1:3]
        rr[region]={'mean_absolute_edge_error_px':float(abs(error).mean()),'maximum_absolute_edge_error_px':int(abs(error).max()),
            'mean_left_signed_error_px':float(error[:,0].mean()),'mean_right_signed_error_px':float(error[:,1].mean())}
    reports[name]=rr;row_data[name]=rows
    rgb=ar[:,:,:3].copy()//2
    re=rm&~(np.roll(rm,1,0)&np.roll(rm,-1,0)&np.roll(rm,1,1)&np.roll(rm,-1,1))
    me=mask&~(np.roll(mask,1,0)&np.roll(mask,-1,0)&np.roll(mask,1,1)&np.roll(mask,-1,1))
    rgb[re]=[50,225,255];rgb[me]=[255,75,185]
    Image.fromarray(rgb).crop((280,130,705,630)).resize((680,800)).save(out/(name+'-head-contour.png'))
report={'method':'Outermost eligible pixel in each row. Reference threshold max RGB >12 and alpha >127; model alpha >127. No alignment adjustment. This diagnoses exterior only; regions are image rows, not semantic surface segmentation.',
    'render':a.render,'render_sha256':hashlib.sha256((ROOT/a.render).read_bytes()).hexdigest(),'regions':regions,'results':reports}
(out/'geometry-rows.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'row-coordinates.json').write_text(json.dumps(row_data)+'\n')
print(json.dumps(reports,indent=2))
