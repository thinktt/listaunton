"""Material and carve coordinates in the unposed skull. The view is irrelevant."""
import numpy as np
AXIS=np.array([1.,-.76])/np.hypot(1.,.76)
UP=np.array([-AXIS[1],AXIS[0]])
def chart(p):
    delta=p[:,[0,2]]-np.array([.412,4.158])
    return delta@AXIS,delta@UP
def ease(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)
def stain(p):
    u,v=chart(p)
    r=np.hypot((u-.015)/.79,(v+.235)/.45)
    cheek=(1-ease((r-.53)/.62))*(.26+.74*ease((.035-v)/.20))
    return cheek*ease((abs(p[:,1])-.08)/.19)
def bell(x,width):return np.exp(-(x/width)**2)
def orbit(p):
    u,v=chart(p);n=u/.267
    # The orbital corners keep their sharply tapered termination. The convex
    # malar surface lies below them, with a thin concave return to the eye.
    width=1-n*n
    soft=.29
    taper=np.where(width>=soft,width,np.where(width<=-soft,0,(width+soft)**2/(4*soft)))
    lower=-.105*u+.008*taper-.052*taper*(1+.08*n)
    extended=lower-.020*ease((n-.60)/.62)
    shelf=ease((1.36-abs(n-.06))/.68)
    old_roll=.020*bell(v-extended+.021,.041)+.014*bell(v-extended+.072,.091)
    # Replace the old narrow roll with one convex surface. Its forward end
    # turns into the noseward corner and its underside dissolves into the jaw.
    crest=lower-.035+.017*ease((u-.012)/.20)
    new_roll=.035*bell(v-crest,.068)+.012*bell(v-crest+.022,.128)
    length=bell(u+.004,.255)*ease((.301-abs(u))/.123)
    delta=shelf*length*(new_roll-old_roll)
    # Lift the inside of the lower recess into the roll as a single bank.
    # A deep incised wall here would expose a separate golden shelf.
    delta+=.021*length*bell(v-lower-.017,.035)
    delta+=.008*bell(u+.036,.33)*bell(v+.17,.125)
    delta*=1-ease((v+.014)/.056)
    # The upper bank overlaps more of the shallow floor. It turns down over
    # the middle of the eye and disappears before each established canthus.
    upper=-.105*u+.008*taper+.067*taper*(1-.16*n)
    delta+=.017*bell(u+.012,.170)*ease((.237-abs(u))/.070)*bell(v-upper+.013,.047)
    side_weight=ease((abs(p[:,1])-.10)/.16)
    return delta*side_weight,crest,lower
