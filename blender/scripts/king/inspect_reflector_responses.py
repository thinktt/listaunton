"""Locate measured real-light responses in the fixed camera for diagnosis."""
from pathlib import Path
import argparse,json,sys
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('directory');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=ROOT/a.directory;fit=json.loads((out/'fit.json').read_text(encoding='utf-8'));rows=[]
for i,name in enumerate(fit['original_powers']):
    im=bpy.data.images.load(str(out/('response-%02d.exr'%i)),check_existing=False);w,h=im.size;ar=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[::-1];bpy.data.images.remove(im);lum=ar[:,:,:3]@np.array([.2126,.7152,.0722]);y,x=np.unravel_index(lum.argmax(),lum.shape);yy,xx=np.indices(lum.shape);weight=np.maximum(lum-lum.max()*.5,0);mass=weight.sum()
    rows.append(dict(light=name,maximum_linear_luminance=float(lum.max()),max_pixel=[int(x),int(y)],bright_centroid=[float((weight*xx).sum()/mass),float((weight*yy).sum()/mass)] if mass else None,fitted_power=fit['fitted_powers'][name]))
(out/'response-locations.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8');print(json.dumps(rows,indent=2))
