"""Measure the two sides of the top of the mane in native head coordinates."""
from pathlib import Path
from statistics import median
import json,sys
import numpy as np
directory=Path(sys.argv[1])
records={}
for key in sys.argv[2:]:
    src=json.loads((directory/f'crest-{key}.json').read_bytes())
    measurements=[]
    for station,rows in src['profiles'].items():
        data={round(row['y']*100):row['surfaces']['mane'] for row in rows if 'mane' in row['surfaces']}
        # Both sides of the central dome are resolved at these actual lateral offsets.
        use=[iy for iy in range(5,18) if iy in data and -iy in data]
        if len(use)<5:continue
        differences=[data[i]-data[-i] for i in use]
        peak=max(data.values())
        crest=[y/100 for y,z in data.items() if z>=peak-.004]
        width=crest[-1]-crest[0]
        # Locate the middle of the end-to-end span at the very top. A broad
        # flat can span the mid-plane even when one shoulder is much higher.
        top_mid=(crest[0]+crest[-1])*.5
        measurements.append({'station':float(station),'mirror_abs_mean':round(float(np.mean(np.abs(differences))),5),'mirror_max':round(max(abs(x) for x in differences),5),'crest_width':round(width,4),'top_mid':round(top_mid,4),'peak_height':round(peak,5)})
    count=len(measurements)
    if count!=6:raise ValueError(f'Only {count} measured cross sections for '+key)
    records[key]={'source_sha256':src['source_sha256'],'stations':measurements,'mean_mirror_difference':round(float(np.mean([m['mirror_abs_mean'] for m in measurements])),5),'greatest_mirror_difference':max(m['mirror_max'] for m in measurements),'median_width_within_004_of_peak':round(median(m['crest_width'] for m in measurements),4),'median_abs_top_mid':round(median(abs(m['top_mid']) for m in measurements),4)}
    print(key,{k:v for k,v in records[key].items() if k not in ('source_sha256','stations')})
(directory/'crest-symmetry.json').write_text(json.dumps({'method':'All dimensions in model units, measured in the unposed head from the evaluated mane. For each station, compare top-surface height at matched y=±0.05, ±0.06, …, ±0.17. Crest width spans the outermost samples within 0.004 of maximum height. A flat or divided crown can give similar widths; consult the profiles and frontal photographs.','scenes':records},indent=2)+'\n')
