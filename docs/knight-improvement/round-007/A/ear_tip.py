"""Relax the bilateral free ear tips while retaining the seated roots."""
import numpy as np
from shape import ease,offsets

def ear_displacement(rest,q):
    step=offsets(rest,q)
    # Preserve almost the released free point. Blend continuously into the
    # shared crown pose before the fixed forehead attachment of each ear.
    # Broad overlapping transitions avoid kinks between the seven loft rings.
    recover=.89*ease((-.24-rest[:,0])/.69)
    step[:,0]*=1-recover
    # Turn the free ear points outward and slightly upward as they shorten.
    # This carries the paired ears above the crown face and maintains their
    # broad crest envelope. The same physical opening is used on both sides.
    opening=.036*ease((-.20-rest[:,0])/.69)**1.6
    step[:,1]+=np.sign(rest[:,1])*opening
    step[:,2]+=1.37*opening
    return step
