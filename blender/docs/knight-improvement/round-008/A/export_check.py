"""Verify the packed pigment and exercise this mission's actual WebGL mesh exporter."""
from pathlib import Path
import sys,json,bpy,numpy as np,hashlib
D=Path(__file__).resolve().parent;ROOT=D.parents[2];sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'scripts/knight'))
from export_mission import export
from mission_scene import visible_meshes,sha,json_file,world_vertices
from lower_carving_fit import rest_coords
def read(file):
    bpy.ops.wm.open_mainfile(filepath=str(file),load_ui=False);s=bpy.context.scene
    imgs=[im for im in bpy.data.images if im.packed_file]
    mat=bpy.data.objects['Knight | continuous horse head and neck'].active_material
    active=mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image
    vals={}
    p=json.loads(s['knight_mission_pose']);pose=[p[k] for k in ('dx','dy','twist_degrees')]
    for obj in visible_meshes(s):
        uv={}
        for layer in obj.data.uv_layers:
            xy=np.empty((len(layer.uv),2),np.float32);layer.uv.foreach_get('vector',xy.ravel());uv[layer.name]=hashlib.sha256(xy.tobytes()).hexdigest()
        vals[obj.name]=(rest_coords(world_vertices(obj),pose),uv)
    return vals,sha(file),active,dict((im.name,hashlib.sha256(im.packed_file.data).hexdigest()) for im in imgs),np.array(s.camera.matrix_world)
old,ph,_,oi,oc=read(D/'parent.blend');new,nh,atlas,ni,nc=read(D/'knight.blend')
assert bytes(atlas.packed_file.data)==(D/'pigment.png').read_bytes()
dif={}
for name,(v,uv) in old.items():
    moved=np.linalg.norm(new[name][0]-v,axis=1)
    dif[name]={'max_position_change':float(moved.max()),'uv_exact':uv==new[name][1]}
    assert uv==new[name][1]
    if 'eye' not in name and 'head and neck' not in name:assert moved.max()==0
out=D/'webgl-check';out.mkdir(exist_ok=True)
meta=export(bpy.context.scene,D/'pigment.png',output=out,source=D/'knight.blend')
assert meta['sourceSha256']==nh and meta['textureSha256']==sha(D/'pigment.png') and meta['exactCornerData']
assert meta['uvLayer']=='Knight wood atlas' and len(meta['parts'])==7 and meta['finish']['file']
assert np.array_equal(oc,nc)
json_file(D/'export-verification.json',{'model_sha256':nh,'parent_sha256':ph,'pigment_sha256':meta['textureSha256'],
             'same_camera':True,'packed_png_matches':True,'uv_and_geometry':dif,'parts':7,'triangles':meta['triangleCount'],
             'atlas_datablock':atlas.name,'packed_before':oi,'packed_after':ni,'webgl_mesh':str(out.relative_to(D)/'mesh.json'),
             'finish_file_bytes':(out/'varnish.bin').stat().st_size})
print('WEBGL_CHECK',nh,meta['textureSha256'],meta['triangleCount'],flush=True)
