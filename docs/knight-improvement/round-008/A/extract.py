"""Collect evaluated rest-space coordinates and unmodified atlas corners."""
from pathlib import Path
import sys,json,hashlib
import bpy
import numpy as np
D=Path(__file__).resolve().parent;ROOT=D.parents[2];sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'scripts/knight'))
from mission_scene import visible_meshes,world_vertices,sha
from probe_carving import point_probe,rest as to_rest
from lower_carving_fit import rest_coords
PARENT='8d984d59beea0f86d69bbb5b8f5dc57becf7e707e576412eb8eda4503e81a948'
assert sha(D/'parent.blend')==PARENT
bpy.ops.wm.open_mainfile(filepath=str(D/'parent.blend'),load_ui=False)
s=bpy.context.scene;cfg=json.loads(s['knight_mission_pose']);pose=[cfg[k] for k in ('dx','dy','twist_degrees')]
probe=point_probe(s);samples={}
for y,xs in [(469,[478,495,520]),(480,[478,495,505,520]),(491,[478,490,495,500,510,520,530]),
             (500,[455,480,500,525]),(517,[455,480,500,525]),(535,[455,480,500,525]),(545,[420,455,490,525])]:
    for x in xs:
        h=probe(x+.5,y+.5)
        if h:samples[f'{x},{y}']=[h[1],np.round(to_rest(h[2],cfg),4).tolist()]
(D/'samples.json').write_text(json.dumps(samples,indent=2))
obj=bpy.data.objects['Knight | continuous horse head and neck']
material=obj.material_slots[0].material
node=material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node
im=node.image;(D/'source-atlas.png').write_bytes(bytes(im.packed_file.data))
indexed=[];uvs=[];tris=[];v0=0;parts=[]
for ob in visible_meshes(s):
    g=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(g)
    m=ev.to_mesh(preserve_all_data_layers=True,depsgraph=g);m.calc_loop_triangles()
    vs=np.empty((len(m.vertices),3),np.float32);m.vertices.foreach_get('co',vs.ravel())
    mat=np.array(ob.matrix_world);vs=rest_coords(vs@mat[:3,:3].T+mat[:3,3],pose)
    tri=np.empty((len(m.loop_triangles),3),np.int32);lp=np.empty_like(tri)
    m.loop_triangles.foreach_get('vertices',tri.ravel());m.loop_triangles.foreach_get('loops',lp.ravel())
    layer=m.uv_layers['Knight wood atlas'];uv=np.empty((len(layer.uv),2),np.float32)
    layer.uv.foreach_get('vector',uv.ravel())
    idx=len(parts);parts.append(ob.name)
    indexed.append(vs);tris.append(tri+v0);v0+=len(vs);uvs.append(uv[lp]);ev.to_mesh_clear()
    np.savez_compressed(D/f'chart-{idx}.npz',position=vs,tri=tri,uv=uv[lp])
(D/'charts.json').write_text(json.dumps({'names':parts,'source_atlas':im.name,'source_sha256':sha(D/'source-atlas.png'),
  'pixels':list(im.size),'materials':[m.name for m in bpy.data.materials if m.use_nodes and any(n.type=='TEX_IMAGE' and n.image==im for n in m.node_tree.nodes)]},indent=2))
print(im.name,list(im.size),[(k,v) for k,v in samples.items() if k.endswith((',517',',535'))])
