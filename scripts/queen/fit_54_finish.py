"""Fit a 54-degree queen while retaining the owner's chosen set proportions.

The outline model approximates a turned surface as projected rings.  Its residual
is calibrated against the existing actual Blender render; real renders remain the
final check. The generated high-resolution image aids fitting, while the original
sprite retains the greater weight.
"""
from pathlib import Path
import json, math, sys
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
from projection_geometry import deform

root = Path(__file__).resolve().parents[2]
a = root / 'assets/queen-projections'
info = json.loads((a / 'baseline-info.json').read_text())
fit = json.loads((a / 'angle-54/fit.json').read_text())
pts0 = np.load(a / 'baseline-controls.npz')['points']
pts, floor0 = deform(pts0, info, 54, fit['parameters'])
rings = pts.reshape(info['ringCount'], info['ringSegments'], 3)
z0 = rings[:,:,2].mean(axis=1)
r0 = np.linalg.norm(rings[:,:,:2], axis=2).mean(axis=1)
zmax = float(z0.max())
base = 2.0734214782714844
scale_report = json.loads((root / 'assets/side-views/scale.json').read_text())
king = next(p for p in scale_report['pieces'] if p['piece'] == 'king')
queen = next(p for p in scale_report['pieces'] if p['piece'] == 'queen')
chosen = json.loads((root / 'assets/side-views/defaults.json').read_text())['shown_height_percent_of_king']['queen'] / 100
target_ratio = chosen * (king['model']['height'] / king['model']['base_diameter']) * (king['original']['base_width_px'] / queen['original']['base_width_px'])
height_multiplier = target_ratio / (4.143457412719727 / base)

ys = np.arange(32, 1115, 3, dtype=float)
def row_widths(im, rendered=False):
    ar = np.asarray(im.convert('RGBA'))
    mask = ar[:,:,3] > 128
    if not rendered: mask &= ar[:,:,:3].max(2) > 12
    lo = mask.argmax(1); hi = mask.shape[1]-1-mask[:,::-1].argmax(1)
    w = (hi-lo)/2; w[~mask.any(1)] = 0
    w = np.convolve(np.pad(w,(2,2),mode='edge'),np.ones(5)/5,'valid')
    return np.interp(ys,np.arange(len(w)),w)
reg = json.loads((root/'assets/queen/original-reference-alignment.json').read_text())
t,dx,dy = reg['scale'],reg['offset_x'],reg['offset_y']
orig = Image.open(root/'references/lichess-staunton-3d/Black-Queen.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(1/t,0,-dx/t,0,1/t,-dy/t),Image.Resampling.BILINEAR)
ow = row_widths(orig)
rw = row_widths(Image.open(root/'assets/queen/reference.png'))
bw = row_widths(Image.open(a/'angle-54/render.png'), True)
sn,cs = math.sin(math.radians(54)), math.cos(math.radians(54))
zknots = np.array([0,.2,.48,.75,1.05,1.35,1.8,2.2,2.65,2.95,3.25,3.6,4.2,5.0])
vknots = np.array([0,.5,1.15,1.8,2.6,3.25,3.75,zmax])

def envelope(r,z,s,yfloor):
    # Sample all cross-section line segments, including the crown and bowl.
    idx = np.linspace(0,len(r)-1,500)
    rr=np.interp(idx,np.arange(len(r)),r)*s
    zz=np.interp(idx,np.arange(len(z)),z)
    ycenter = yfloor-s*cs*zz
    q=rr[:,None]**2-((ys[None,:]-ycenter[:,None])/sn)**2
    return np.sqrt(np.maximum(q.max(axis=0),0))
base_env = envelope(r0,z0,fit['scale'],floor0)
calibration = bw-base_env

# Radius multipliers at zknots (first and base-width control fixed), vertical
# offsets at interior vknots, plus camera scale and floor position.
params=np.zeros(14+6+2)
def shape(p):
    radial = np.interp(z0,zknots,p[:14])
    dz = np.interp(z0,vknots,np.r_[0,p[14:20],0])
    r = r0*(1+radial)
    # The same lower-quarter base diameter is used to establish set scale.
    # Do not let a bulge above the foot silently widen that measurement.
    z = z0*height_multiplier+dz
    r = np.where(z < z.max()*.25, np.minimum(r, base/2), r)
    return r, z
def loss(p):
    r,z = shape(p)
    if np.any(np.diff(z)<-0.10): return 1e8
    s=fit['scale']*(1+p[20]); floor=floor0+p[21]
    pred=np.maximum(0,envelope(r,z,s,floor)+calibration)
    def huber(x):
        ab=np.abs(x);return np.where(ab<5,.5*x*x,5*ab-12.5)
    # Disregard the tail of the source's black floor shadow.
    mask=(ys<1090)
    discrepancy=(.7*np.mean(huber((pred-ow)[mask]))+.3*np.mean(huber((pred-rw)[mask])))
    smooth=240*np.mean(np.diff(p[:14],2)**2)+8*np.mean(p[14:20]**2)
    return float(discrepancy+smooth)

initial=loss(params)
free=[2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
for step in [.04,.02,.01,.005,.0025]:
    for sweep in range(5):
        improved=False
        for j in free:
            best=loss(params); bestp=params.copy()
            for direction in [-1,1]:
                trial=params.copy();delta=step*(200 if j==21 else 2 if 14<=j<20 else 1)
                trial[j]+=direction*delta
                limit=25 if j==21 else .20 if 14<=j<20 else .10 if j==20 else .20
                trial[j]=np.clip(trial[j],-limit,limit)
                score=loss(trial)
                if score<best-1e-7: best=score;bestp=trial;improved=True
            params=bestp
        print('fit',step,sweep,round(loss(params),4),flush=True)
        if not improved:break
result={'elevation_degrees_above_board':54,'target_queen_to_king_height':chosen,
        'target_height_to_base_width':target_ratio,'starting_height_to_base_width':4.143457412719727/base,
        'height_multiplier':height_multiplier,'radial_knots':zknots.tolist(),'vertical_knots':vknots.tolist(),
        'parameters':params.tolist(),'camera_scale':fit['scale']*(1+params[20]),
        'camera_floor':floor0+params[21], 'camera_cx':fit['cx'],
        'outline_model_loss_before':initial,'outline_model_loss_after':loss(params),
        'method':'Projected-ring outline approximation calibrated to the previous render; 70% original and 30% selected outline. Fixed 54-degree elevation and 83.4% king-relative physical height under original sprite base-width normalization. Real render checked separately.'}
out=root/'assets/queen/finish-fit.json';out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
