"""Compare collar-glint color separately from grain placement and brightness."""
import argparse,json
from pathlib import Path
import numpy as np
from audit_mission import ROOT,BUILD,rgba,registered,black

def run(output,trials):
    images=registered();images.pop('original_white')
    images['accepted-baseline']=rgba(ROOT/'assets/pawn/render.png')
    images.update({name:rgba(BUILD/name/'fixed.png') for name in trials})
    regions={'left':(420,596,480,632),'right':(520,587,560,619),'front':(495,619,552,636)}
    report={}
    for label,im in images.items():
        a=np.asarray(black(im),float);stats={}
        for key,(x0,y0,x1,y1) in regions.items():
            b=a[y0:y1,x0:x1];lum=b@np.array([.24,.53,.23]);cut=np.quantile(lum,.8)
            mask=lum>cut;rgb=b[mask].mean(0);mean=float(lum[mask].mean())
            stats[key]={'mean_bright_rgb':rgb.tolist(),'mean_bright_luma':mean,
                        'rgb_per_luma':(rgb/max(mean,1e-8)).tolist(),'selected_pixels':int(mask.sum())}
        report[label]=stats
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({'method':'Each patch uses its own brightest 20% of pixels. Display RGB/luma is a descriptive color statistic, not linear BSDF reflectance. Original is shown separately because its blur and glint positions differ.','images':report},indent=2)+'\n',encoding='utf8')
    for name,stats in report.items():print(name,{k:[round(x,3) for x in v['rgb_per_luma']] for k,v in stats.items()})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('trials',nargs='*');a=p.parse_args();run(a.output,a.trials)
