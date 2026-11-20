"""Check saved and independently reconstructed middle-collar renders."""
from pathlib import Path
import numpy as np,json,argparse
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--trial',default='155-fitted-ridge-crescents');p.add_argument('--reproduction',default='156-reproduced-middle-collar');args=p.parse_args()
trial=ROOT/'build/queen-mission'/args.trial
r=ROOT
sampling=json.loads((trial/'parameters.json').read_text()).get('render_sampling',{'samples':64})
def delta(a,b):
 a=np.asarray(Image.open(a).convert('RGBA')).astype(np.int16);b=np.asarray(Image.open(b).convert('RGBA')).astype(np.int16);mask=a[:,:,3]>127;d=abs(a[:,:,:3]-b[:,:,:3]);opaque=d[mask]
 return {'mean_rgb_byte_difference':float(d.mean()),'opaque_mean_rgb_byte_difference':float(opaque.mean()),'opaque_p99_rgb_byte_difference':float(np.quantile(opaque,.99)),'opaque_p999_rgb_byte_difference':float(np.quantile(opaque,.999)),
 'opaque_fraction_pixels_over_five_bytes':float((opaque.max(1)>5).mean()),'max_rgb_byte_difference':int(d.max()),'alpha_identical':bool(np.array_equal(a[:,:,3],b[:,:,3]))}
report={'reopened':delta(trial/'wood.png',trial/'wood-reopened.png'),'reproduced':delta(trial/'wood.png',r/'build/queen-mission'/args.reproduction/'wood.png'),
 'render_sampling':sampling,'assessment':f"Quantified over opaque piece pixels. Native {sampling['samples']}-sample render comparisons are not claimed bit exact; use the established checkpoint-15 sampling bounds.",
 'tolerances':{'opaque_mean_bytes_max':.1,'opaque_p999_bytes_max':2,'opaque_fraction_pixels_over_five_bytes_max':.001,'max_bytes':64,'alpha_identical_required':True}}
report['strict_one_byte_check_passed']=all(report[k]['max_rgb_byte_difference']<=1 for k in ['reopened','reproduced'])
for key in ['reopened','reproduced']:
 v=report[key];assert v['alpha_identical'] and v['opaque_mean_rgb_byte_difference']<.1 and v['opaque_p999_rgb_byte_difference']<=2 and v['opaque_fraction_pixels_over_five_bytes']<.001 and v['max_rgb_byte_difference']<=64,(key,v)
(trial/'material-reproduction-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
print('TRIAL_RENDER_CHECKS_DONE',flush=True)
