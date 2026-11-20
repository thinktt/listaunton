"""Anatomic profiles in the head's own unposed frame, shared by both flanks."""
import numpy as np
CENTER=np.array([.432,4.172])
ANGLE=np.radians(38.)
ALONG=np.array([np.cos(ANGLE),-np.sin(ANGLE)])
UP=np.array([-ALONG[1],ALONG[0]])
def chart(p):
    delta=p[:,[0,2]]-CENTER
    return delta@ALONG,delta@UP
def ease(t):
    t=np.clip(t,0,1);return t*t*(3-2*t)
def bell(x,w):return np.exp(-(x/w)**2)
def baseline(p,coef):
    axis=np.array([1.,-.76])/np.hypot(1,.76);up=np.array([-axis[1],axis[0]])
    d=p[:,[0,2]]-[.412,4.158];a=d@axis;b=d@up
    return np.column_stack([np.ones_like(a),a,b,a*a,a*b,b*b,a**3,a*a*b,a*b*b,b**3])@coef
def contours(u):
    native=u/(1+.19*ease((u+.006)/.217))
    n=native/.276
    # Smooth elliptical ends lead into two short, independently tapering folds.
    r=1-n*n
    taper=np.where(r>.23,r,np.where(r<-.23,0,(r+.23)**2/.92))
    axis=-.045*u+.004*taper-.043*ease((u+.022)/.263)
    top=axis+taper*(.104*(1-.28*n)-.035*ease((u+.055)/.234))
    lower=axis-taper*(.071*(1+.13*n)-.014*ease((u-.080)/.195))
    return top,lower
def socket(u,v,top,lower):
    native=u/(1+.19*ease((u+.006)/.217))
    end=ease((.295-abs(native))/.065)
    # A high hood emerges from the brow and thins over the forward corner.
    hood=end*(.034*bell(v-top-.018,.047)+.012*bell(v-top-.065,.084))*(.88+.12*bell(u+.07,.20))
    hood*=1-.69*ease((u-.072)/.24)
    upper_cut=-.015*end*bell(v-top+.009,.020)*(1-.37*ease((u-.15)/.15))
    # At the lower lid the first bank meets the globe. A short lower fold
    # dies out in the cheek before reaching either corner.
    roll=end*.030*bell(v-lower+.015,.067)*(1-.65*ease((u-.097)/.17))
    under=0.
    cheek=.019*bell(u+.004,.235)*bell(v-lower+.103,.097)
    radius=.036+.006*bell(u+.016,.181)
    cut=end*ease((top-v+.007)/.043)*(.5+.5*np.tanh((v-lower+.004)/radius))
    corner=-.009*bell(u-.288,.060)*bell(v+.062,.036)-.005*bell(u+.239,.054)*bell(v+.001,.024)
    return hood+upper_cut+roll+under+cheek-.069*cut+corner
def dress(p,coef):
    u,v=chart(p);top,lower=contours(u)
    outer=np.hypot(u/.310,(v+.003)/.167)
    blend=ease((1.49-outer)/.53)*ease((abs(p[:,1])-.11)/.15)
    target=baseline(p,coef)+socket(u,v,top,lower)
    # A short, gently convex turn beneath the inner rim follows the cheek
    # around the eye. It retains the surrounding slope at both ends and
    # widens towards the middle, where the tool leaves its broadest face.
    center=lower-.055+.012*ease((u+.08)/.23)
    shift=v-center;width=.039+.020*bell(u-.025,.17)
    def surface(vv):
        xz=CENTER+u[:,None]*ALONG+vv[:,None]*UP
        probe=np.column_stack([xz[:,0],p[:,1],xz[:,1]])
        return baseline(probe,coef)+socket(u,vv,top,lower)
    base=surface(center);slope=(surface(center+.006)-surface(center-.006))/.012
    roll=base+slope*shift-2.2*shift*shift
    length=bell(u-.018,.158)*ease((.282-abs(u-.016))/.10)
    width_mask=ease((width-abs(shift))/.022)
    target+=length*width_mask*(roll-target)
    return blend*(target-abs(p[:,1])),blend,top,lower
def ocular_coordinates(unit,side,coef):
    # The front and back share an x,z chart; the signed depth gives this
    # continuous globe a closed, outward-facing surface.
    su,depth,sv=unit.T
    local=.297*su;u=local*(1+.19*ease((local+.004)/.217))
    v=.145*sv-.031*u+.008-.048*ease((u-.009)/.228)
    xz=CENTER+u[:,None]*ALONG+v[:,None]*UP
    out=np.column_stack((xz[:,0],np.zeros(len(xz)),xz[:,1]))
    soft_iris=.025*bell(u+.038,.133)*bell(v-.027,.064)
    # The lower corneal plane rises on a crescent inside the opening. Its
    # ends dissolve beneath the hood, away from the long exterior cheek fold.
    a=(u+.038)/.155
    arc=.038-.074*np.sqrt(np.maximum(0,1-a*a))
    cover=ease((1-abs(a))/.31)
    crescent=cover*(.0077*bell(v-arc+.009,.023)-.0073*bell(v-arc-.006,.018))
    slope=-.011*ease((u-.031)/.160)
    outer=ease((side*depth+.06)/.48)
    # A shallow horizontal incision in the upper corneal plane gives the
    # wood a pupil under its brow. It dies into the continuous dome at both
    # ends and leaves the lower crescent clean.
    strip=np.exp(-((u+.088)/.081)**4)
    h=v-(.055+.135*(u+.088))
    pupil=-.0068*strip*bell(h,.015+.003*strip)
    bed=baseline(out,coef)-.039+(.049*side*depth)+(soft_iris+crescent+slope+pupil)*outer
    out[:,1]=side*bed
    return out
