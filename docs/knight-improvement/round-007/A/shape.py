"""Symmetric rest-space shear and settling of the poll and its interfaces."""
import numpy as np

def ease(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)

def offsets(points,q):
    rear,front,rear_onset,front_onset,ear_set,forehead_set=q
    x,y,z=points.T
    t=ease((x+.77)/1.52)
    rear_weight=ease((z-rear_onset)/.61)
    front_weight=ease((z-front_onset)/.59)
    # Preserve the eye floor, upper and lower lids and their cheek transitions.
    eye_x=x-.412;eye_z=z-4.158
    u=(eye_x-.76*eye_z)/np.hypot(1,.76);v=(.76*eye_x+eye_z)/np.hypot(1,.76)
    clear=ease((np.hypot(u/.31,v/.15)-1.56)/.64)
    dx=-((1-t)*rear*rear_weight+t*front*front_weight)*clear
    # The forward crown enters the forehead slightly deeper. The weight is
    # shared by both ears, the mane and the skull wherever they meet.
    dz=-clear*(ear_set*np.exp(-((x+.43)/.51)**2)*ease((z-4.57)/.28)
                +forehead_set*np.exp(-((x-.34)/.48)**2)*ease((z-4.68)/.34))
    return np.column_stack((dx,np.zeros(len(points)),dz))
