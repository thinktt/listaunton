"""Report measured lower-flare normal reversals and fixed-view glint diagnostics."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--before',required=True);p.add_argument('--after',required=True);p.add_argument('--out',required=True)
a=p.parse_args();report={'note':'A normal reversal is a geometry diagnostic, not proof of the unknown original curvature. Bright-core statistics also include pigment and transport. Fixed reference and camera are unchanged.','surfaces':{}}
for name,path in [('before',a.before),('after',a.after)]:
    data=json.loads((ROOT/path/'base-surface.json').read_text());samples=[v for v in data['samples'] if v['pixel'][0]==584 and 940<=v['pixel'][1]<=1000]
    values=np.array([v['normal_tilt_degrees'] for v in samples]);steps=np.diff(values)
    report['surfaces'][name]={'source':data['source'],'source_sha256':data['source_sha256'],'column_x':584,'image_y_range':[940,1000],
      'total_positive_normal_tilt_step_degrees':float(np.maximum(steps,0).sum()),'max_positive_step_degrees':float(max(0,steps.max())),
      'samples':[{'y':v['pixel'][1],'normal_tilt_degrees':v['normal_tilt_degrees']} for v in samples]}
report['bright_blue_base_core']={}
for name,path in [('reference','assets/bishop/reference.png'),('accepted_007','history/bishop-mission-007/render.png'),('trial_067','build/bishop-mission/067-smooth-base-curvature/wood.png')]:
    ar=np.array(Image.open(ROOT/path).convert('RGB'));region=ar[920:1030,500:670];v=region[:,:,2]
    mask=v>np.percentile(v,98);yy,xx=np.nonzero(mask)
    report['bright_blue_base_core'][name]={'image':path,'box':[500,920,670,1030],'pixels':int(mask.sum()),'centroid':[float(xx.mean()+500),float(yy.mean()+920)],'mean_rgb':region[mask].mean(0).tolist()}
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:{kk:vv for kk,vv in v.items() if kk!='samples'} for k,v in report['surfaces'].items()},indent=2))
