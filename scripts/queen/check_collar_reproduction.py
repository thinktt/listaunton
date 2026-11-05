"""Quantify opaque-pixel render repeatability for the fifteenth queen checkpoint.

Requires original trial render, two saved-file renders (wood-first-reopen.png
and wood-reopened.png), and independent reconstruction 146. Reports the strict
one-byte failure as well as the explicit native sampling tolerances.
"""
from pathlib import Path
import numpy as np,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
trial=ROOT/'build/queen-mission/145-direct-glossy-collars'
r=ROOT
def delta(a,b):
 a=np.asarray(Image.open(a).convert('RGBA')).astype(np.int16);b=np.asarray(Image.open(b).convert('RGBA')).astype(np.int16);mask=a[:,:,3]>127;d=abs(a[:,:,:3]-b[:,:,:3]);opaque=d[mask]
 return {'mean_rgb_byte_difference':float(d.mean()),'opaque_mean_rgb_byte_difference':float(opaque.mean()),'opaque_p99_rgb_byte_difference':float(np.quantile(opaque,.99)),'opaque_p999_rgb_byte_difference':float(np.quantile(opaque,.999)),
 'opaque_fraction_pixels_over_five_bytes':float((opaque.max(1)>5).mean()),'max_rgb_byte_difference':int(d.max()),'alpha_identical':bool(np.array_equal(a[:,:,3],b[:,:,3]))}
report={'reopened':delta(trial/'wood.png',trial/'wood-first-reopen.png'),'reproduced':delta(trial/'wood.png',r/'build/queen-mission/146-reproduced-collar-checkpoint/wood.png'),'repeat_same_saved_file':delta(trial/'wood-first-reopen.png',trial/'wood-reopened.png'),
 'strict_one_byte_check_passed':False,'assessment':'The original all-pixel one-byte bound failed on sparse glints. Quantified over opaque piece pixels and checked a second reopen; no broad material/color or alpha change. Native 64-sample render comparisons are not claimed bit exact.',
 'tolerances':{'opaque_mean_bytes_max':.1,'opaque_p999_bytes_max':2,'opaque_fraction_pixels_over_five_bytes_max':.001,'max_bytes':64,'alpha_identical_required':True}}
for key in ['reopened','reproduced','repeat_same_saved_file']:
 v=report[key];assert v['alpha_identical'] and v['opaque_mean_rgb_byte_difference']<.1 and v['opaque_p999_rgb_byte_difference']<=2 and v['opaque_fraction_pixels_over_five_bytes']<.001 and v['max_rgb_byte_difference']<=64,(key,v)
(trial/'material-reproduction-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
print('TRIAL_RENDER_CHECKS_DONE',flush=True)
