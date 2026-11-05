"""Read-only pixel and format diagnostics for packed inferred pigment."""
from pathlib import Path
import argparse,json,sys
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('variants',nargs='+');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
records={}
for variant in args.variants:
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'build/queen-mission'/variant/'queen.blend'),load_ui=False)
 im=next((i for i in bpy.data.images if i.name.startswith('Queen linear inferred pigment')),None)
 if im is None:im=next(i for i in bpy.data.images if i.name.startswith('Queen inferred diffuse pigment'))
 values=np.empty(im.size[0]*im.size[1]*4,dtype=np.float32);im.pixels.foreach_get(values);values=values.reshape(im.size[1],im.size[0],4)[::-1]
 records[variant]={'file_format':im.file_format,'colorspace':im.colorspace_settings.name,'is_float':im.is_float,'source':im.source,'filepath':im.filepath,'packed_magic':list(bytes(im.packed_file.data[:8])) if im.packed_file else None,'center_rgb':values[650,480,:3].tolist(),'foreground_median':np.median(values[:,:,:3][values[:,:,3]>.9],axis=0).tolist()}
 expected=ROOT/'build/queen-mission'/variant/'expected-pigment.npy'
 if expected.exists():
  delta=abs(values-np.load(expected));records[variant]['roundtrip_max_error']=float(delta.max());records[variant]['roundtrip_mean_error']=float(delta.mean());assert delta.max()<.001,records[variant]
(ROOT/'build/queen-mission/packed-pigment-check.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records,indent=2))
