"""Recover walnut variation on the upper turning from its measured diffuse response."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path);p.add_argument('model_dir',type=Path)
    p.add_argument('response',type=Path);p.add_argument('out',type=Path)
    a=p.parse_args();root=a.root.resolve();assets=root/'assets/knight'
    sys.path.insert(0,str(root/'scripts/knight'))
    from refit_face_pigment import diffuse_field, ease, project_surface, sha
    model=a.model_dir/'knight.blend';texture=assets/json.loads((assets/'mission-checkpoint.json').read_bytes())['texture_file']
    record=json.loads((a.response/'measurement.json').read_bytes())
    assert record['source_sha256']==sha(model) and record['texture_sha256']==sha(texture)
    response=np.load(a.response/'light-response.npz')
    depth=response['depth'];height,width=depth.shape
    camera=json.loads((assets/'camera.json').read_bytes())
    view_to_world=np.linalg.inv(np.reshape(camera['worldToCamera'],(4,4)))
    projection=np.reshape(camera['projectionMatrix'],(4,4))
    y,x=np.indices(depth.shape)
    x_cam=((x+.5)*2/width-1-projection[0,3])/projection[0,0]
    y_cam=(1-(y+.5)*2/height-projection[1,3])/projection[1,1]
    z_world=x_cam*view_to_world[2,0]+y_cam*view_to_world[2,1]-depth*view_to_world[2,2]+view_to_world[2,3]
    field=diffuse_field(response,record,'pedestal')
    # A soft transition ends on the carved shoulder; foot and lower turning use their established pigment.
    scope=ease(z_world,1.27,1.43)
    prior=np.asarray(Image.open(texture).convert('RGB'))
    atlas=np.zeros(prior.shape[:2],np.float32)
    receiver=next(row for row in record['objects'] if row['object'].endswith('turned pedestal'))
    visible=project_surface(a.response/receiver['file'],depth,scope*field,atlas,(244,540,739,908))
    changed=np.abs(atlas)>.001
    assert 1000<changed.sum()<.45*atlas.size
    linear_gain=np.exp(np.clip(atlas[changed],-.75,.48))
    srgb=prior[changed].astype(float)/255
    linear=np.where(srgb<=.04045,srgb/12.92,((srgb+.055)/1.055)**2.4)*linear_gain[:,None]
    fresh=prior.copy()
    fresh[changed]=np.rint(255*np.clip(np.where(linear<=.0031308,12.92*linear,1.055*linear**(1/2.4)-.055),0,1)).astype(np.uint8)
    a.out.mkdir(exist_ok=True,parents=True);out=a.out/'pigment.png'
    Image.fromarray(fresh).save(out)
    result={'source_sha256':sha(model),'pigment_sha256':sha(out),'previous_texture_sha256':sha(texture),
            'region':'upper pedestal','changed_pixels':int(np.any(fresh!=prior,axis=2).sum()),
            'visible_samples':int(visible),'gain_percentile_05_50_95':np.percentile(linear_gain,[5,50,95]).tolist(),
            'method':'Two Cycles light-response measurements separate walnut chroma from neutral reflection. Only registered visible upper-pedestal UVs change. Surface gain fades to zero below the shoulder.'}
    (a.out/'grade.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result)
if __name__=='__main__':main()
