"""New queen controls drawn from the side concept, independent of earlier meshes."""
import math
import numpy as np

# (height, radius), from the floor up to the crown. The proportions were
# estimated from side-01.png: a wide, low foot and flare, full socket, broad
# curved stem, three round stacked collars, and short flaring crown body.
PROFILE=[
(0,.002),(0,.90),(.012,.974),(.025,1.0),(.045,1.01),(.08,1.01),(.23,1.01),(.27,1.0),(.29,.985),(.30,.965),
(.315,.963),(.335,.978),(.365,.995),(.405,1.0),(.45,.992),(.50,.98),(.57,.95),(.64,.91),(.70,.865),(.78,.79),(.86,.695),(.94,.59),
(.98,.55),(1.02,.548),(1.07,.56),(1.12,.575),(1.19,.575),(1.25,.568),(1.30,.552),(1.33,.52),(1.35,.47),(1.36,.435),
(1.39,.41),(1.48,.385),(1.60,.355),(1.75,.325),(1.92,.30),(2.08,.28),(2.22,.275),(2.34,.28),(2.45,.30),(2.52,.33),(2.56,.37),
(2.575,.405),(2.585,.46),(2.60,.51),(2.62,.55),(2.65,.575),(2.69,.58),(2.72,.56),(2.745,.52),(2.755,.47),
(2.765,.45),(2.775,.47),(2.79,.50),(2.81,.525),(2.84,.535),(2.87,.53),(2.895,.51),(2.905,.47),
(2.915,.44),(2.925,.435),(2.94,.445),(2.96,.458),(2.98,.46),(3.00,.455),(3.02,.435),(3.03,.405),
(3.045,.398),(3.09,.402),(3.15,.411),(3.22,.426),(3.29,.445),(3.36,.47),(3.42,.50),(3.47,.535)]

# (height, radius, tip-height amplitude, tip-radius amplitude). Continue the
# surface outward across the crown lip, inward through its bowl, then up the
# seated egg. Eight rounded peaks rise smoothly from the outer wall.
CROWN=[
(3.50,.56,.015,.005),(3.53,.59,.04,.01),(3.55,.62,.09,.018),
(3.56,.635,.155,.025),(3.565,.625,.155,.025),(3.555,.60,.15,.02),
(3.53,.57,.075,.014),(3.49,.53,.03,.008),(3.44,.48,.008,.003),
(3.39,.42,.01,0),(3.36,.35,0,0),(3.35,.27,0,0),(3.36,.215,0,0),
(3.37,.19,0,0),(3.40,.185,0,0),(3.44,.182,0,0),(3.50,.172,0,0),
(3.56,.16,0,0),(3.62,.145,0,0),(3.68,.125,0,0),(3.72,.09,0,0),(3.74,.05,0,0),(3.745,.001,0,0)]

def controls(segments=192):
    theta=np.arange(segments)*2*math.pi/segments
    peak=((1+np.cos(8*(theta-math.pi/8)))/2)**4.0
    rows=[]
    for z,r in PROFILE:
        # Lift the crown wall gradually into the lip, preserving a seamless flow.
        lift=float(np.interp(z,[0,3.03,3.47],[0,0,.16]))
        rows.append(np.stack((r*np.cos(theta),r*np.sin(theta),np.full(segments,z+lift)),axis=1))
    for j,(z,r,amp,ra) in enumerate(CROWN):
        radius=r+ra*peak
        # The source shows a shallow bowl and a finial seated higher than a
        # deep cup would put it. Blend the rise into the inner bowl.
        inner_lift=float(np.interp(j,[0,8,9,10,11,12,13,21],[0,0,.03,.07,.10,.13,.14,.14]))
        rows.append(np.stack((radius*np.cos(theta),radius*np.sin(theta),z+.16+inner_lift+amp*peak),axis=1))
    return np.asarray(rows)

def apply_fit(rings,fit):
    points=rings.copy();p=np.asarray(fit['parameters'])
    mean_z=rings[:,:,2].mean(1)
    knots=np.array([0,.3,.8,1.25,1.7,2.3,2.7,3.02,3.4,3.8])
    radial=np.interp(mean_z,knots,np.r_[0,p[:8],p[7]])
    offsets=np.interp(mean_z,[0,.5,1.2,1.7,2.55,3.06,3.8],np.r_[0,p[8:13],0])
    points[:,:,:2]*=(1+radial[:,None,None])
    points[:,:,2]=points[:,:,2]*fit['height_multiplier']+offsets[:,None]
    return points
