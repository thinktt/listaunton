"""Regional deformation in the bishop's native meridian coordinates."""
import numpy as np

# Foot through first stem support, underside of collar stack, mitre root.
SOCKET, COLLAR, MITRE = 39, 46, 72


def smooth(t):
    t = np.clip(t, 0., 1.)
    return t*t*(3.-2.*t)


def shape(old, height, spec, case):
    """Map control rings by anatomical region, keeping socket and cap tangents."""
    foot = case.get('base_factor',spec['base_factor'])
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
    # Radius controls taper to zero at the ends of each named region. This
    # leaves the original cap seat and all forty donor rings intact.
    for name,lo,peak,hi in [('lower_rim',46,52,57),('middle_rim',57,60,66),
                            ('upper_rim',66,70,72),('mitre_lower',72,82,101),
                            ('mitre_upper',83,97,110)]:
        if name in case:
            i=np.arange(lo,hi+1)
            weight=smooth((i-lo)/(peak-lo))*smooth((hi-i)/(hi-peak))
            out[lo:hi+1,0]+=case[name]*weight
    if case.get('mitre_lift'):
        # Lift the bulb's existing curved sections together. The integral
        # profile keeps one crest and meets the original seat tangentially.
        sl=slice(MITRE,111)
        z=old[sl,1]
        u=(z-z[0])/(z[-1]-z[0])
        out[sl,1]+=case['mitre_lift']*16*u*u*(1-u)**2
        assert np.all(np.diff(out[sl,1])>0),'Mitre sections must rise monotonically'
    return out, target_top-height*hz
