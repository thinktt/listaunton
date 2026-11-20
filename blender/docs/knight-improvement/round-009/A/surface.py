"""Rest-space cut of the brow and the asymmetric lower orbital chamfer."""
import numpy as np
AXIS=np.array([1.,-.76])/np.hypot(1.,.76)
UP=np.array([-AXIS[1],AXIS[0]])
def chart(p):
    xy=p[:,[0,2]]-[.412,4.158]
    return xy@AXIS,xy@UP
def ease(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)
def bell(x,width):return np.exp(-(x/width)**2)
def margins(u):
    n=u/.267;r=1-n*n
    taper=np.where(r>=.29,r,np.where(r<=-.29,0,(r+.29)**2/1.16))
    axis=-.105*u+.008*taper
    return axis+.067*taper*(1-.16*n),axis-.052*taper*(1+.08*n)
def skirt(rest):
    u,v=chart(rest);_,lower=margins(u);s=v-lower
    # Stretch the original convex bevel outwards from its existing inner edge.
    # A coordinate warp preserves the original order of the surface tangents.
    return (-.023*bell(u-.009,.176)*ease((.255-abs(u))/.073)
            *ease((.002-s)/.026)*bell(s+.029,.075)
            *ease((abs(rest[:,1])-.11)/.16))
def orbit_shape(rest):
    u,v=chart(rest)
    side=ease((abs(rest[:,1])-.11)/.16)
    upper=(.071*bell(u+.076,.182)*ease((u+.32)/.198)
           *(.5+.5*np.tanh((v-.012)/.045))*bell(v-.058,.118))
    corner=(.086*ease((u+.028)/.220)*bell(u-.199,.158)
            *bell(v+.025,.114))
    local=side*ease((.53-abs(u))/.092)*ease((.39-abs(v))/.09)
    return local*(corner+AXIS[1]*upper),local*UP[1]*upper
def relief(rest,eye):
    u,v=chart(rest);top,lower=margins(u);s=v-lower
    ends=ease((.25-abs(u))/.084)
    if eye:
        # Slightly fuller towards the center, with its upper portion tucked
        # below the brow. The perimeter continues behind the same two corners.
        depth=ends*bell(u+.020,.185)*(.0095*bell(v+.001,.048)
                    -.0050*ease((v-.016)/.040)-.0035*bell(v+.054,.030))
        return depth
    # Skive the previously steep lower socket wall diagonally. Its short
    # broad face lies beneath the center and fades before either canthus.
    # The skive meets a modest convex cheek, with its maximum well below the
    # opening. It has no surrounding incision to reflect as a second rim.
    cheek=.007*bell(u+.018,.252)*bell(s+.097,.089)*ease((-.008-s)/.063)
    # Carve the brow's underside separately from its broad upper surface.
    # The deepest point is above the end of the visible eye floor.
    brow=ends*bell(u+.024,.193)*(.015*bell(v-top-.019,.036)-.012*bell(v-top+.007,.019))
    return (cheek+brow)*ease((abs(rest[:,1])-.11)/.16)*ease((.44-abs(u))/.107)*ease((.39-abs(v+.060))/.105)
