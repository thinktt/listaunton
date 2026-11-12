"""Propose coupled radial/height profiles; actual renders decide acceptance.

No source pixels or registration change. The analytical envelope is calibrated
to the accepted alpha so its approximation is not mistaken for render truth.
"""
import json
import argparse
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.optimize import least_squares
from scipy.interpolate import BSpline
from overlay_qa import largest_component, fill_holes

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--controls', type=Path, required=True,
    help='A .npy control array or a study control-comparison.npz (before key).')
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--baseline-render', type=Path, default=ROOT/'assets/queen/queen-matched.png')
parser.add_argument('--factors', type=float, nargs='+', default=[.94,.9,.84])
args = parser.parse_args()
data = np.load(args.controls)
controls = data['before'] if isinstance(data, np.lib.npyio.NpzFile) else data

def clean(mask):
    return fill_holes(largest_component(mask))

def model_mask(path):
    return clean(np.asarray(Image.open(path).convert('RGBA'))[:,:,3] > 127)

def refs():
    reg=json.loads((ROOT/'assets/queen/original-reference-alignment.json').read_text())
    scale,dx,dy=reg['scale'],reg['offset_x'],reg['offset_y']
    original=Image.open(ROOT/'references/lichess-staunton-3d/Black-Queen.png').convert('RGBA').transform(
        (1254,1254),Image.Transform.AFFINE,(1/scale,0,-dx/scale,0,1/scale,-dy/scale),Image.Resampling.BILINEAR)
    images={'original_black':original,'selected_highres':Image.open(ROOT/'assets/queen/reference.png').convert('RGBA')}
    result={}
    for name,img in images.items():
        a=np.asarray(img)
        result[name]=clean((a[:,:,3]>127)&(a[:,:,:3].max(2)>12))
    return result
r = np.linalg.norm(controls[:, :, :2], axis=2).mean(1)
z = controls[:, :, 2].mean(1)
ys = np.arange(610., 1090., 3.)
s, floor = 264.61125, 860.223491056495
sn, cs = np.sin(np.deg2rad(54)), np.cos(np.deg2rad(54))

def widths(mask):
    left = mask.argmax(1)
    right = mask.shape[1] - 1 - mask[:, ::-1].argmax(1)
    w = np.where(mask.any(1), (right - left) / 2, 0)
    return np.interp(ys, np.arange(len(w)), w)

index = np.linspace(1, 49, 650)
def smooth(values):
    # Uniform cubic subdivision limit along the meridian. Calibration covers
    # the remaining radial-direction and discrete-render differences.
    basis = BSpline(np.arange(-3, len(values)+1), values, 3, extrapolate=False)
    return basis(index)

def envelope(rr, zz):
    a, b = smooth(rr)*s, smooth(zz)
    center = floor - s*cs*b
    q = a[:, None]**2 - ((ys[None,:]-center[:,None])/sn)**2
    return np.sqrt(np.maximum(q.max(0), 0))

ref = refs()
target = {name:widths(mask) for name,mask in ref.items()}
base_width = widths(model_mask(args.baseline_render))
correction = base_width - envelope(r,z)
knots = np.array([0, 11, 17, 22, 25, 29, 33, 38, 43, 50, 116])

def profile(factor, p):
    new_z = z.copy()
    new_z[:39] *= factor
    t = np.clip((z[39:51]-z[38])/(z[50]-z[38]),0,1)
    new_z[39:51] += (factor-1)*z[39:51]*(1-t*t*(3-2*t))
    # Shared radius shift for the socket's straight wall. Endpoints fixed.
    deltas = np.r_[0,0,p[:4],p[3],p[4:6],0,0]
    new_r = r + np.interp(np.arange(len(r)), knots, deltas)
    return new_r,new_z

def residual(p, factor):
    rr,zz = profile(factor,p)
    prediction = envelope(rr,zz)+correction
    return np.r_[np.sqrt(.8)*(prediction-target['original_black']),
                 np.sqrt(.2)*(prediction-target['selected_highres']),
                 p*24, np.diff(p,2)*12]

out = args.output
out.mkdir(parents=True,exist_ok=True)
for factor in args.factors:
    if not .8 <= factor <= 1:
        raise ValueError('This bounded study expects compression between 0.8 and 1')
    solved = least_squares(residual, np.zeros(6), args=(factor,), bounds=(-.045,.065), diff_step=.02, max_nfev=90)
    rr,zz=profile(factor,solved.x)
    prediction=envelope(rr,zz)+correction
    report={'compression':factor, 'radial_parameters':solved.x.tolist(),
      'scope':'foot/base/socket vertical compression through 38; smooth stem return at 50; coupled radial fit',
      'ring_radii':{str(i):float(rr[i]) for i in range(1,50) if abs(rr[i]-r[i])>1e-7},
      'ring_z_offsets':{str(i):float(zz[i]-z[i]) for i in range(1,50) if abs(zz[i]-z[i])>1e-7},
      'predicted_width_rmse_px':{name:float(np.sqrt(np.mean((prediction-t)**2))) for name,t in target.items()},
      'baseline_width_rmse_px':{name:float(np.sqrt(np.mean((base_width-t)**2))) for name,t in target.items()},
      'caveat':'Analytical proposal only; must render and judge actual geometry.'}
    (out/f'compress-{factor:.2f}.json').write_text(json.dumps(report,indent=2)+'\n')
    print(factor, solved.x, report['predicted_width_rmse_px'], flush=True)
