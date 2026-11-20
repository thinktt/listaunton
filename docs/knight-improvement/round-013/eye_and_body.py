"""Measure changes in the eye and protected areas using the final reopened render pair."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
root=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);codes=sys.argv[3:];assets=root/'assets/knight'
build=root/'build/knight-mission';out=build/f'round-{n:03}-judge'
def photo(p):return np.array(Image.open(p).convert('RGBA'),dtype=np.int16)
report={}
for view,model,trial in [('fixed','render.png','wood.png'),('side','guide-render.png','wood-side.png')]:
    parent=photo(assets/model);ref=photo(assets/'ref.png') if view=='fixed' else None
    for code in codes:
        candidate=photo(build/f'improvement-{n:03}-{code}'/trial)
        union=(parent[:,:,3]>127)|(candidate[:,:,3]>127)
        opaque=(parent[:,:,3]>245)&(candidate[:,:,3]>245)
        diff=np.abs(parent[:,:,:3]-candidate[:,:,:3])
        stats={'mask_xor_pixels':int(np.count_nonzero((parent[:,:,3]>127)^(candidate[:,:,3]>127))),
               'mask_union_pixels':int(union.sum()),'color_mae':round(float(diff[opaque].mean()),3)}
        if view=='fixed':
            rects={'eye and cheek':(445,438,568,520),'upper mane':(260,300,500,378),'long mane':(186,421,331,661),'chest':(375,577,645,777),'pedestal':(294,824,727,1001)}
            for name,(l,t,r,b) in rects.items():
                sl=np.s_[t:b,l:r];m=opaque[sl]&(ref[sl][:,:,3]>245)
                parent_err=np.abs(parent[sl][:,:,:3]-ref[sl][:,:,:3])[m].mean()
                candidate_err=np.abs(candidate[sl][:,:,:3]-ref[sl][:,:,:3])[m].mean()
                stats[name]={'change_mae':round(float(diff[sl][m].mean()),3),'parent_mae_to_black2':round(float(parent_err),3),'candidate_mae_to_black2':round(float(candidate_err),3)}
        report.setdefault(view,{})[code]=stats
(out/'eye-and-body.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
