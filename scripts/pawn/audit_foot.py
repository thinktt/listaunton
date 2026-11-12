"""Inspect the fixed-view groove, foot arcs and their original-sprite context."""
import argparse,json
from pathlib import Path
import numpy as np
from audit_mission import ROOT,BUILD,rgba,registered,black,sheet
from audit_foot_isolation import REGIONS
from derive_wood import blur

def run(output,trials):
    images=registered();images.pop('original_white')
    images['checkpoint-015']=rgba(ROOT/'history/pawn-mission-015/render.png')
    images.update({name:rgba(BUILD/name/'fixed.png') for name in trials})
    target=np.asarray(black(images['selected']),float);report={}
    for label,im in images.items():
        a=np.asarray(black(im),float);stats={}
        for key,(x0,y0,x1,y1) in REGIONS.items():
            b=a[y0:y1,x0:x1];ref=target[y0:y1,x0:x1]
            lum=b@np.array([.24,.53,.23]);ref_lum=ref@np.array([.24,.53,.23]);cut=np.quantile(lum,.8)
            m=lum>cut;rgb=b[m].mean(0);mean=float(lum[m].mean())
            hp=lum-blur(lum,r=2,passes=2);rp=ref_lum-blur(ref_lum,r=2,passes=2)
            stats[key]={'rgb_mae_255':float(abs(b-ref).mean()),'luma_mae_255':float(abs(lum-ref_lum).mean()),
                        'mean_luma':float(lum.mean()),'fine_contrast':float(np.std(hp)),
                        'fine_correlation':float(np.corrcoef(hp.ravel(),rp.ravel())[0,1]),
                        'bright_rgb_per_luma':(rgb/max(mean,1e-8)).tolist()}
        lum=a@np.array([.24,.53,.23]);stats['profile_x_555_565']=lum[922:984,555:565].mean(1).tolist()
        report[label]=stats
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({'images':report,'note':'Fixed registration. Patch RGB/luma and fine pattern correlation are descriptive display-space diagnostics. Original sprite remains authoritative; it is lower resolution and cannot establish every generated highlight.'},indent=2)+'\n',encoding='utf8')
    keys=['selected','checkpoint-015',*trials]
    sheet([(k,images[k]) for k in keys],(511,916,598,989),280,output.with_suffix('.png'))
    sheet([(k,images[k]) for k in keys],(310,880,665,1006),330,output.with_name(output.stem+'-wide.png'))
    for name,stats in report.items():print(name,{k:round(stats[k]['rgb_mae_255'],3) for k in REGIONS})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('trials',nargs='*');a=p.parse_args();run(a.output,a.trials)
