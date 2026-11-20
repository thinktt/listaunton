"""Keep every atlas texel outside a baked local repair byte-for-byte unchanged."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--previous',required=True);p.add_argument('--bake',required=True);p.add_argument('--texture',required=True)
a=p.parse_args();prior=ROOT/a.previous;folder=ROOT/a.bake;dest=ROOT/a.texture
digest=hashlib.sha256(prior.read_bytes()).hexdigest()
previous=Image.open(prior).convert('RGB');old=np.asarray(previous);patch=np.asarray(Image.open(folder/'color.png').convert('RGB'))
coverage=np.asarray(Image.open(folder/'coverage.png').convert('RGB'))
assert old.shape==patch.shape==coverage.shape
mask=coverage.max(2)>0;assert 100<mask.sum()<old.shape[0]*old.shape[1]*.03,int(mask.sum())
result=old.copy();result[mask]=patch[mask]
assert np.array_equal(result[~mask],old[~mask])
dest.parent.mkdir(exist_ok=True,parents=True);Image.fromarray(result).save(dest)
reopened=np.asarray(Image.open(dest).convert('RGB'));assert np.array_equal(reopened,result)
assert hashlib.sha256(prior.read_bytes()).hexdigest()==digest
changed=(old!=result).any(2);yy,xx=np.nonzero(changed)
report={'previous':a.previous,'previous_sha256':digest,'texture':a.texture,'texture_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
        'bake':a.bake,'masked_texels':int(mask.sum()),'changed_texels':int(changed.sum()),'changed_bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],
        'outside_mask_bytes_exact':True,'previous_file_unchanged':True,'png_reopened_exact':True,'bakes_lighting':False,
        'method':'Replace only texels reached by the local pigment repair mask. All remaining v8 texels are copied unchanged. The bake contains Base Color and coverage only.'}
(folder/'merge.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
