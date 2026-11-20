"""Replay the frozen recipe from its upstream model and compare every native mesh byte."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import load,proposal,PIGMENT,MANE
def surfaces(s):
    result={}
    for ob in s.objects:
        if ob.type!='MESH':continue
        m=ob.data;h=hashlib.sha256()
        for rows,key,dtype,dims in [(m.vertices,'co',np.float32,3),(m.loops,'vertex_index',np.int32,1),(m.polygons,'loop_start',np.int32,1)]:
            a=np.empty(len(rows)*dims,dtype);rows.foreach_get(key,a);h.update(a.tobytes())
        for uv in m.uv_layers:
            a=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',a);h.update(a.tobytes())
        finish=m.attributes.get('Knight varnish coverage')
        if finish:
            a=np.empty(len(finish.data),np.float32);finish.data.foreach_get('value',a);h.update(a.tobytes())
        result[ob.name]=h.hexdigest()
    return result
def studio(s):
    state={}
    for o in s.objects:
        if o.type=='LIGHT':
            c=o.light_linking.receiver_collection
            state[o.name]=[np.asarray(o.matrix_world).round(6).tolist(),list(o.data.color),o.data.energy,o.data.shape,o.data.size,o.data.size_y,o.data.spread,sorted(i.name for i in c.objects) if c else None]
    return state
def pigment(s):
    im=s.objects[MANE].active_material.node_tree.nodes['Knight delivered albedo'].image
    return hashlib.sha256(bytes(im.packed_file.data)).hexdigest()
recipe=json.loads((D/'recipe.json').read_text())['design'];s=load('parent.blend');proposal(s,recipe)
import bpy
bpy.context.view_layer.update()
rebuilt=surfaces(s);lamps=studio(s);tex=pigment(s);s=load('knight.blend');frozen=surfaces(s)
assert frozen==rebuilt and lamps==studio(s) and tex==pigment(s)
(D/'replay.json').write_text(json.dumps({'native_mesh_uv_varnish_bytes_identical_under_replay':True,'all_studio_lamps_reproduced':True,
    'packed_pigment_sha256':tex,'sha256_by_object':frozen},indent=2)+'\n')
