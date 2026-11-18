"""Regional deformation in the bishop's native meridian coordinates."""
import numpy as np

# Foot through first stem support, underside of collar stack, mitre root.
SOCKET, COLLAR, MITRE = 39, 46, 72


def smooth(t):
    t = np.clip(t, 0., 1.)
    return t*t*(3.-2.*t)


def shape(old, height, spec, case):
    """Map control rings by anatomical region, keeping socket and cap tangents."""
    foot = spec['base_factor']
    hz, hr = case['head_height'], case['head_radius']
    target_top = spec['height_factor']*height
    za, zb, zc = old[[SOCKET, COLLAR, MITRE], 1]
    new_c = target_top + (zc-height)*hz
    new_b = new_c + (zb-zc)*case['collar_height']
    stem_h = new_b - za*foot
    span = zb-za
    assert stem_h>0
    out = old.copy()
    out[:SOCKET+1] *= foot
    sl = slice(SOCKET+1,COLLAR)
    t = (old[sl,1]-za)/span
    # Hermite joins continue the scales on either side of the stem. A small
    # mid-stem correction can move its waist without shifting either join.
    out[sl,1] = (za*foot + stem_h*smooth(t)
                 + span*foot*t*(1.-t)**2 - span*case['collar_height']*t*t*(1.-t)
                 + case.get('waist_height',0.)*16*t*t*(1-t)**2)
    rs = (foot + (case['stem_radius']-foot)*smooth(t/.36)
          + (case['collar_radius']-case['stem_radius'])*smooth((t-.68)/.32))
    out[sl,0] = old[sl,0]*rs
    sl = slice(COLLAR,MITRE)
    out[sl,1] = new_c + (old[sl,1]-zc)*case['collar_height']
    f = smooth((np.arange(COLLAR,MITRE)-(MITRE-6))/6.)
    out[sl,0] *= case['collar_radius'] + (hr-case['collar_radius'])*f
    out[MITRE:,0] *= hr
    out[MITRE:,1] = target_top + (old[MITRE:,1]-height)*hz
    return out, target_top-height*hz
