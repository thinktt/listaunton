"""Apply the selected finish to a loaded scene containing the frozen 008 mane.

Import apply(scene) from an integration script. Nothing is saved by this module.
"""
from pathlib import Path
from hashlib import sha256
import json
import numpy as np
from mathutils import Matrix

def apply(scene,resources=None):
    root=Path(resources) if resources else Path(__file__).resolve().parent
    cfg=json.loads((root/'recipe.json').read_bytes())
    mane=scene.objects['Knight | swept rounded mane']
    pts=np.empty((len(mane.data.vertices),3),np.float32)
    mane.data.vertices.foreach_get('co',pts.ravel())
    assert sha256(pts.tobytes()).hexdigest()==cfg['geometry_sha256']
    assert sha256((root/'varnish.npy').read_bytes()).hexdigest()==cfg['varnish_sha256']
    wax=np.load(root/'varnish.npy',allow_pickle=False)
    assert wax.shape==(len(pts),) and np.isfinite(wax).all() and min(wax)>=0 and max(wax)<=1
    for name,setting in cfg['lights'].items():
        obj=scene.objects[name]
        assert obj.data.type=='AREA' and {o.name for o in obj.light_linking.receiver_collection.all_objects}=={mane.name}
    mane.data.attributes['Knight varnish coverage'].data.foreach_set('value',wax)
    mane.data.update()
    for name,setting in cfg['lights'].items():
        obj=scene.objects[name];obj.matrix_world=Matrix(setting['matrix'])
        obj.data.shape=setting['shape'];obj.data.size=setting['size'];obj.data.size_y=setting['width']
        obj.data.energy=setting['energy'];obj.data.spread=setting['spread'];obj.data.color=setting['color']
