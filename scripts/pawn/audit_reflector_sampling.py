"""Compare independent-seed errors and the new light's actual isolated support."""
import argparse,json
from pathlib import Path
import numpy as np
from audit_mission import ROOT,BUILD,rgba,black,mask,REGIONS,sheet
from audit_foot_isolation import REGIONS as FOOT

def run(folder,before,after):
    out=BUILD/folder;target=rgba(ROOT/'assets/pawn/reference.png');t=np.asarray(black(target),float)
    images={'before-0':rgba(ROOT/before),'after-0':rgba(ROOT/after),
            'before-31':rgba(out/'before-seed31.png'),'after-31':rgba(out/'after-seed31.png')}
    values={k:np.asarray(black(v),float) for k,v in images.items()};m=mask(target,True)
    for im in images.values():m &= mask(im,False)
    response=np.load(out/'isolated-response.npy')[:,:,:3];report={'regions':{},'note':'Same camera, maps, original 44 lamps and 512-sample setup. Seed 31 is an independent sample check. RGB is composited on black using the common foreground of all four renders; whole-region values therefore differ from the uncomposited single-pair mission audit. Isolated response is linear radiance at the probe power, not display RGB.'}
    for name,(x0,y0,x1,y1) in {**REGIONS,**FOOT}.items():
        region=np.s_[y0:y1,x0:x1];valid=m[region]
        errors={key:float(abs(a[region]-t[region])[valid].mean()) for key,a in values.items()}
        deltas=[(values['after-'+seed]-values['before-'+seed])[region][valid] for seed in ('0','31')]
        r=response[region][valid]
        report['regions'][name]={'errors_rgb_255':errors,
            'before_seed_difference_rgb':float(abs(values['before-0'][region]-values['before-31'][region])[valid].mean()),
            'after_seed_difference_rgb':float(abs(values['after-0'][region]-values['after-31'][region])[valid].mean()),
            'after_minus_before_mean_rgb':{s:d.mean(0).tolist() for s,d in zip(('0','31'),deltas)},
            'delta_correlation':float(np.corrcoef(deltas[0].ravel(),deltas[1].ravel())[0,1]),
            'isolated_response_mean':r.mean(0).tolist(),'isolated_response_max':float(r.max())}
    (out/'analysis.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    sheet([('selected',target),*images.items()],(511,916,598,989),250,out/'comparison.png')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('before',type=Path);p.add_argument('after',type=Path)
    a=p.parse_args();run(a.folder,a.before,a.after)
