from pathlib import Path
import json,sys,bpy,numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from export_mission import export
from mission_scene import sha
p=json.loads((D/'parameters.json').read_text());src=D/'knight.blend';tex=D/'pigment.png'
assert sha(src)==p['model_sha256'] and sha(tex)==p['packed_atlas_sha256']
bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False);s=bpy.context.scene
for o in s.objects:
    if o.type=='MESH' and not o.hide_render:
        img=o.active_material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image
        assert bytes(img.packed_file.data)==tex.read_bytes()
out=D/'web-export';out.mkdir(exist_ok=True)
meta=export(s,tex,output=out,source=src);n=meta['vertexCount']
data=np.fromfile(out/'mesh.bin',dtype='<f4',count=n*8).reshape(-1,8)
idx=np.fromfile(out/'mesh.bin',dtype='<u4',offset=n*32)
assert idx.max()<n and np.isfinite(data).all()
assert np.allclose(np.linalg.norm(data[:,3:6],axis=1),1,atol=2e-5)
assert (data[:,6:]>=-.0001).all() and (data[:,6:]<=1.0001).all()
assert (out/'varnish.bin').stat().st_size==n
print('VERIFIED_EXPORT',meta['sourceSha256'],meta['textureSha256'],meta['triangleCount'],meta['bounds'])
