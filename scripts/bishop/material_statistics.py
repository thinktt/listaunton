"""Reference-pixel statistics on the shared opaque interior, not fidelity scores."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser(description=__doc__);p.add_argument('renders',nargs='+');p.add_argument('--out')
a=p.parse_args()
ref=np.array(Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA'),dtype=np.float32)/255
regions={'all':(0,0,1254,1254),'button':(420,160,560,280),'head':(320,275,655,470),
    'upper_head':(450,278,590,355),'lower_head_glare':(535,417,630,477),
    'collars':(310,460,675,610),'stem':(410,610,575,765),'socket':(355,740,635,865),'base':(230,850,755,1035),'foot':(220,1020,760,1120)}
records={}
for name in a.renders:
    ren=np.array(Image.open(ROOT/name).convert('RGBA'),dtype=np.float32)/255
    mask=(ref[:,:,3]>127/255)&(ren[:,:,3]>.995)&(ref[:,:,:3].max(2)>12/255)
    mask=blur(mask.astype(np.float32),radius=4)>.999
    values={}
    for region,(x1,y1,x2,y2) in regions.items():
        sl=np.s_[y1:y2,x1:x2];m=mask[sl];r=ref[sl][:,:,:3][m];v=ren[sl][:,:,:3][m]
        assert len(r)>100, (region,'Not enough foreground pixels for a meaningful statistic')
        values[region]={'pixels':len(r),'mean_absolute_rgb_error_8bit':float(np.abs(v-r).mean()*255),
            'mean_reference_rgb_8bit':(r.mean(0)*255).round(2).tolist(),'mean_render_rgb_8bit':(v.mean(0)*255).round(2).tolist()}
    records[name]=values
result={'note':'Diagnostic only. RGB differences include geometry and lighting, and do not replace the visual scorecard. Reference alpha >127 and max RGB >12; model alpha >.995; shared mask eroded 4 pixels. The supplied reference has alpha 253 across much of its interior. Background and silhouette edges excluded.', 'renders':records}
if a.out:(ROOT/a.out).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
