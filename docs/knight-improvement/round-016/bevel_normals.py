"""Locate the real change of surface angle under the photographed crest."""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np

root, assets, model, output = [Path(arg).resolve() for arg in sys.argv[1:]]
sys.path.insert(0, str(root / 'scripts/knight'))
from probe_reflections import surface_probe

probe, source_hash = surface_probe(assets)
assert source_hash == hashlib.sha256(model.read_bytes()).hexdigest()
anchors = [(276,356),(288,351),(300,346),(320,341),(340,338),(360,338),
           (380,338),(400,339),(420,340),(440,342),(452,345),(462,350),
           (470,354),(477,358),(484,365)]
guide_x, guide_y = np.array(anchors).T
xs = np.arange(292, 483, 4)
offsets = np.arange(-18, 19, 2)
rows = []
for x in xs:
    y = int(round(np.interp(x, guide_x, guide_y)))
    hits = [probe(int(x), y + int(dy)) for dy in offsets]
    normals = [hit['normal'] if hit else None for hit in hits]
    owners = [hit['part'].split('|')[-1].strip() if hit else None for hit in hits]
    change = []
    for i, (a,b) in enumerate(zip(normals, normals[1:])):
        if a is None or b is None or owners[i] != owners[i + 1]:
            change.append(None)
        else:
            change.append(round(float(np.degrees(np.arccos(np.clip(np.dot(a,b), -1, 1)))), 3))
    rows.append({'x':int(x),'guide_y':y,'parts':owners,'smooth_normal_angle_change_deg':change})
areas = {}
for name,lo,hi in [('rear',298,340),('middle',341,409),('forward',410,450),('return',451,477)]:
    group = [row for row in rows if lo <= row['x'] <= hi]
    widths, centers, totals, peak_rates = [], [], [], []
    for row in group:
        change = np.array(row['smooth_normal_angle_change_deg'], dtype=float)
        # A jump across two separate components cannot measure rounding on a bevel.
        if not np.all(np.isfinite(change)) or np.sum(change) < 1: continue
        cdf = np.r_[0, np.cumsum(change)] / change.sum()
        q = np.interp([.1,.5,.9], cdf, offsets)
        widths.append(float(q[2]-q[0]))
        centers.append(float(q[1]))
        totals.append(float(change.sum()))
        peak_rates.append(float(change.max()/2))
    def median(values):return round(float(np.median(values)), 2) if values else None
    mane_at_source = sum(row['parts'][9] == 'swept rounded mane' for row in group)
    areas[name]={'columns':len(group),'single_surface_columns':len(widths),'mane_columns_at_source_edge':mane_at_source,
                 'median_10_90_turn_width_px':median(widths),'median_center_offset_px':median(centers),
                 'median_total_turn_deg':median(totals),'median_peak_deg_per_px':median(peak_rates)}
output.write_text(json.dumps({'model':source_hash,'mesh':hashlib.sha256((assets/'mesh.bin').read_bytes()).hexdigest(),
    'offsets_from_source_px':offsets.tolist(),'columns':rows,'sections':areas,
    'method':'Cast the saved reference camera through narrow cross-sections of the registered upper mane. Each sample uses the nearest exported triangle and its interpolated unit normal. Successive same-part samples give the surface turn over two image pixels. The central 80% of integrated turn describes its apparent width in this view. Crossings onto a different component are shown separately and excluded from width statistics.'},indent=2)+'\n',encoding='utf-8')
print(areas)
