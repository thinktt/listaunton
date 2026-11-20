"""Measure wood color on either side of real seams in the curved mane."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
from PIL import Image


def digest(data):
    return hashlib.sha256(data).hexdigest()


def texture_values(atlas, uv):
    h,w = atlas.shape[:2]
    coords = np.clip(uv*[w,-h]+[-.5,h-.5], [0,0], [w-1.001,h-1.001])
    x,y = coords[:,0],coords[:,1]
    i,j = x.astype(int),y.astype(int)
    s,t = (x-i)[:,None],(y-j)[:,None]
    return (1-t)*((1-s)*atlas[j,i]+s*atlas[j,i+1])+t*((1-s)*atlas[j+1,i]+s*atlas[j+1,i+1])


def quantile(values, weights, q):
    order = np.argsort(values)
    weights = weights[order].cumsum()
    return float(values[order][np.searchsorted(weights,q*weights[-1])])


def continuity(atlas, chart):
    rgb = np.array(Image.open(atlas).convert('RGB'))
    left,right = chart['left'],chart['right']
    size = np.array(rgb.shape[1::-1])
    sep = np.linalg.norm((left[:,:2]-right[:,:2])*size,axis=2).max(axis=1)
    seam = sep > 1.5
    center = chart['xyz']
    back = np.zeros(len(seam),dtype=bool)
    for z in np.arange(2.4,4.31,.08):
        row = (center[:,2]>=z)&(center[:,2]<z+.08)
        if row.any():
            back |= row & (center[:,0] < np.median(center[row,0])) & (abs(center[:,1])<.17)
    observations = []
    for alpha in [.24,.5,.76]:
        colors = []
        for tri in (left,right):
            mid = (1-alpha)*tri[:,0]+alpha*tri[:,1]
            # Take a bilinear sample 0.7 source texels inside each adjacent island.
            inward = tri[:,2]-mid
            distance = np.linalg.norm(inward*size,axis=1)[:,None]
            texel = mid+inward*np.minimum(.45,.70/np.maximum(distance,1e-9))
            colors.append(texture_values(rgb,texel))
        observations.append(np.abs(colors[0]-colors[1]).mean(axis=1))
    rgb_step = np.median(observations,axis=0)
    weight = chart['lengths']
    metrics = {}
    for label, mask in [('all UV seams',seam),('unbroken UV',~seam),('back UV seams',seam&back),('back unbroken UV',(~seam)&back)]:
        if not mask.any():
            metrics[label] = {'edges':0}
            continue
        metrics[label] = {'edges':int(mask.sum()),'model_length':round(float(weight[mask].sum()),3),
                          'median_rgb_step':round(quantile(rgb_step[mask],weight[mask],.5),3),
                          'p90_rgb_step':round(quantile(rgb_step[mask],weight[mask],.9),3),
                          'percent_length_step_over_12':round(100*float(weight[mask&(rgb_step>12)].sum()/weight[mask].sum()),2)}
    return metrics


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path)
    p.add_argument('round',type=int)
    p.add_argument('candidates',nargs='*')
    a = p.parse_args()
    root = a.root.resolve()
    b = root/'build/knight-mission'
    j = b/f'round-{a.round:03}-judge'
    results = {}
    for lab in ['parent',*a.candidates]:
        d = json.loads((j/f'mane-uv-{lab}.json').read_bytes())
        npz = j/f'mane-uv-{lab}.npz'
        assert digest(npz.read_bytes())==d['physical_uv_pairs_sha256']
        targets = {v['packed_atlas'] for v in d['parts'].values()}
        assert len(targets)==1
        atlas_sha = targets.pop()
        if lab=='parent':
            meta = json.loads((root/'assets/knight/mesh.json').read_bytes())
            atlas = root/meta['texture']
            baseline = d
        else:
            folder = b/f'improvement-{a.round:03}-{lab}'
            atlas = next(f for f in folder.glob('*.png') if digest(f.read_bytes())==atlas_sha)
        assert digest(atlas.read_bytes())==atlas_sha
        changes = {}
        for name,part in d['parts'].items():
            changes[name] = [k for k in ('geometry','normals','uv','varnish','uv_layer') if part[k]!=baseline['parts'][name][k]]
        results[lab] = {'scene':d['source_sha256'],'atlas':atlas_sha,'component_changes':changes,
                        'studio_identical':d['settings']==baseline['settings'],'wood_edge_continuity':continuity(atlas,np.load(npz))}
    (j/'uv-continuity.json').write_text(json.dumps({'method':'Adjacent triangles share a physical edge. Measure median RGB difference across it at three positions, 0.7 texture pixels inside each adjacent triangle. Count real UV island seams separately. Weight summaries by physical edge length. This assay can find a color seam but does not measure likeness or beauty.', 'models':results},indent=2)+'\n')
    for lab, record in results.items():
        print(lab,record['wood_edge_continuity'])
        print('Changed geometry or finish', {k:v for k,v in record['component_changes'].items() if v}, 'same studio',record['studio_identical'])

if __name__=='__main__':
    main()
