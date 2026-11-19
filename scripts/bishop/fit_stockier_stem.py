"""Build alternative load-bearing profiles under the original 54-degree outline."""
import json

import numpy as np
from PIL import Image

from compare_shared_turning import sprite
from fit_reference_turning import TurningFit
from fit_short_reference import DOC,OUT,ROOT,read
from fit_side_refit import half_widths,smooth_meridian


def register_waist(fit,source,controls):
    """Find the lowest visible waist that preserves the original outline below the collars."""
    yy=np.arange(589,638,2)
    f=fit.f
    def width(rz):
        r,z=smooth_meridian(rz).T
        front=(yy[None,:]+.5-f.cy+f.zy*z[:,None])/np.maximum(f.yr*r[:,None],1e-7)
        return f.xr*np.sqrt(np.max(np.maximum(1-front*front,0)*r[:,None]**2,axis=0))
    original=sprite()
    chosen=Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA')
    def widths(image):
        a=np.asarray(image)
        return half_widths((a[:,:,3]>127)&(a[:,:,:3].max(2)>12))[yy]
    target,secondary=widths(original),widths(chosen)
    a=np.asarray(Image.open(ROOT/'history/bishop-mission-024/render-clay.png').convert('RGBA'))
    bias=half_widths(a[:,:,3]>127)[yy]-width(fit.old)
    # Ring 35 sets the source outline only for a short arc. Ring 37 and the
    # collar underside are hidden here, so their requested fullness stays.
    lo=np.array([-.006,0.,.004,.015,.032,.005,.22])
    hi=np.array([.012,.070,.037,.145,.086,.16,.48])
    x=np.array([.002,.022,.019,.083,.066,.093,.35])
    def shape(values):
        test=controls.copy()
        for n,i in enumerate([34,35,36]):
            test[i]=source[i]+values[2*n:2*n+2]
        test[20:32]=source[20:32]+(controls[20:32]-source[20:32])*(values[6]/.35)
        return test
    def loss(values):
        test=shape(values)
        w=width(test)+bias
        r,z=smooth_meridian(test).T
        local=(z>1.65)&(z<2.65)
        waist=2*np.min(r[local])
        return np.mean(np.abs(w-target))+.17*np.mean(np.abs(w-secondary))+100*max(.594-waist,0)
    best=loss(x)
    for step in (.35,.2,.1,.05,.025,.012,.005):
        for _ in range(10):
            improved=False
            for i in range(len(x)):
                for sign in (-1,1):
                    v=x.copy();v[i]=np.clip(v[i]+sign*step*(hi[i]-lo[i]),lo[i],hi[i])
                    score=loss(v)
                    if score<best-1e-5:x,best,improved=v,score,True
            if not improved:break
    return shape(x)


def fair_stem(fit,original,strength):
    """Fair both sides of the waist with a shared vertical tangent."""
    controls=original.copy()
    i=np.arange(len(controls))
    knots=[14,16,18,20,22,24,27,29,31,32,33,34,35,36,37,38,39,40,41,42,43]
    dr=np.interp(i,knots,[0,.005,.029,.047,.035,.012,.012,.015,.020,0,0,0,0,0,0,0,0,.019,.002,0,0])
    dz=np.interp(i,knots,[0,-.009,-.043,-.062,-.032,.012,.017,.041,.070,.050,.021,.050,.087,.078,.047,-.011,-.097,-.067,-.016,0,0])
    controls+=strength*np.stack((dr,dz),axis=1)
    root=controls[31,1];end=controls[39,1];waist_z=2.15
    r0=controls[31,0];r1=.290+.003*(strength-1);rend=.352+.012*(strength-1)
    for idx in range(32,40):
        z=controls[idx,1]
        if z<waist_z:
            controls[idx,0]=r1+(r0-r1)*((waist_z-z)/(waist_z-root))**1.90
        else:
            controls[idx,0]=r1+(rend-r1)*((z-waist_z)/(end-waist_z))**2.25
    return controls

# The projected tips of the collars and foot are already registered. Most
# upper-shaft rings sit behind the lower collar in the saved view. The lower
# shaft briefly supplies the outside contour, near rings 33 and 34.
# Radius and height are in model units. The socket lip follows the original
# front arc (dz/dr = tan(54 degrees)). A shoulder below the lowest collar
# is gradually carved down into the stem in a true side elevation.
OFFSETS=[
    (20,0,0),(22,.008,.006),(24,.029,.039),(28,.031,.0426),(31,.032,.044),
    (32,.012,.022),(33,0,.003),(34,.002,0),(35,.031,-.010),
    (36,.061,-.030),(37,.072,-.061),(38,.070,-.112),(39,.062,-.153),
    (40,.036,-.125),(41,.011,-.069),(42,0,-.019),(43,0,0),
]


def main():
    fit=TurningFit()
    source=read(DOC/'before-stem-fit.json')
    result={}
    indices=np.arange(len(fit.old))
    knots,dr,dz=np.asarray(OFFSETS).T
    offsets=np.stack((np.interp(indices,knots,dr),np.interp(indices,knots,dz)),axis=1)
    original=fit.old.copy()
    for key,(r,y) in source['body_rings'].items():
        original[int(key)]=[r*fit.f.fac,(fit.f.s['y0']-y)*fit.f.fac/fit.f.cos]
    for name,strength,lower in [('balanced',.78,1.),('full',1.,1.),('shoulder',1.13,.35),('broad',1.25,.95),
                                ('registered',1.18,.35),('deep-cove',1.33,.35),('fair',1.,1.),('fair-full',1.30,1.),
                                ('turned',1.33,.35)]:
        change=offsets*strength
        change[:32]*=lower
        controls=original+change
        if name in ('registered','deep-cove','turned'):
            controls=register_waist(fit,original,controls)
            if name=='turned':
                # Keep the tuck under the lower collar near the shaft. The
                # outer third of the plate retains its thin, turned edge.
                controls[37:43,0]=[.324,.338,.355,.380,.501,original[42,0]]
                controls[37:43,1]=original[37:43,1]+np.array([-.030,-.104,-.164,-.095,-.018,-.002])
            change=controls-original
        if name in ('fair','fair-full'):
            controls=fair_stem(fit,original,strength)
            change=controls-original
        rings={str(i):[float(r/fit.f.fac),float(fit.f.s['y0']-z*fit.f.cos/fit.f.fac)]
               for i,(r,z) in enumerate(controls) if np.any(abs(controls[i]-fit.old[i])>1e-9)}
        cfg={**source,'variant':'185-stock-'+name,'body_rings':rings,'samples':64}
        (OUT/('stock-'+name+'.json')).write_text(json.dumps(cfg,indent=2)+'\n')
        width=fit.project(controls)[0]+fit.bias
        result[name]={'strength':strength,'socket_fraction':lower,
                      'stock_offsets_model_units':(change[20:44]).tolist(),
                      'projected_mean_half_width_difference_from_original':float(np.mean(abs(width-fit.target[0]))),
                      'shaft_control_span':float(controls[39,1]-controls[31,1]),
                      'waist_control_diameter':float(2*np.min(controls[32:40,0]))}
    (DOC/'stem-proposals.json').write_text(json.dumps({'rings_from_20_to_43':result,'source_fit':'Restored 024 with the registered 029 button, rounded saw, turned body and original full-width foot.'},indent=2)+'\n')
    for name,r in result.items():print(name,r['shaft_control_span'],r['waist_control_diameter'],r['projected_mean_half_width_difference_from_original'])


if __name__=='__main__':main()
