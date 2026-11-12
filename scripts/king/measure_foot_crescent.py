"""Measure the registered foot strip without moving any comparison image."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]

def measure(render,previous,output):
    paths={'reference':ROOT/'assets/king/reference.png','previous':ROOT/previous,'trial':ROOT/render}
    arrays={k:np.asarray(Image.open(p).convert('RGB'),dtype=float) for k,p in paths.items()}
    rows={};bounds=[270,975,650,1085]
    for name,a in arrays.items():
        assert a.shape==(1254,1254,3);lum=a@np.array([.2126,.7152,.0722]);values=[]
        for x in range(320,601,40):
            predicted=1047-.00175*(x-493)**2;lo=round(predicted)-10;hi=round(predicted)+11
            strip=lum[lo:hi,x-3:x+4].mean(1);k=int(strip.argmax())
            values.append(dict(x=x,peak_y=lo+k,peak_luminance_255=float(strip[k]),peak_on_search_boundary=k in (0,len(strip)-1)))
        rows[name]=values
    x0,y0,x1,y1=bounds;ref=arrays['reference'][y0:y1,x0:x1]
    bright_columns=[r['x'] for r in rows['reference'] if r['peak_luminance_255']>100 and not r['peak_on_search_boundary']]
    report=dict(method='Luminance peaks of seven-pixel-wide columns in a fixed curved foot band. The brighter reference columns (luminance above 100/255, interior maximum) support a limited location diagnostic. Dimmer columns can pick adjacent features. Whole RGB crop MSE also reported. These diagnose placement and tone; they do not measure perceived fidelity or grain agreement.',crop_xyxy=bounds,curve=dict(apex_y=1047,axis_x=493,quadratic=-.00175,half_width=10),columns=rows,bright_columns=bright_columns,rgb_mse_255={k:float(((a[y0:y1,x0:x1]-ref)**2).mean()) for k,a in arrays.items() if k!='reference'},bright_arc_mean_absolute_peak_y_error={k:float(np.mean([abs(r['peak_y']-t['peak_y']) for r,t in zip(rows['reference'],v) if r['x'] in bright_columns])) for k,v in rows.items() if k!='reference'})
    path=ROOT/output;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('render');p.add_argument('previous');p.add_argument('output');a=p.parse_args();measure(a.render,a.previous,a.output)
