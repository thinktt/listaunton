"""Read the actual 11B packed colour and triangular UV islands."""
from pathlib import Path
import sys,bpy,numpy as np,json
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from mission_scene import visible_meshes
from lower_carving_fit import rest_coords
bpy.ops.wm.open_mainfile(filepath=str(D/'parent.blend'),load_ui=False)
s=bpy.context.scene;q=json.loads(s['knight_mission_pose']);pose=[q[k] for k in ('dx','dy','twist_degrees')]
obj=s.objects['Knight | swept rounded mane']
img=obj.active_material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image
(D/'source-atlas.png').write_bytes(bytes(img.packed_file.data))
out={};other=[]
for obj in visible_meshes(s):
    ob=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ob.to_mesh();m.calc_loop_triangles()
    uv=np.empty((len(m.loops),2),np.float32);m.uv_layers['Knight wood atlas'].data.foreach_get('uv',uv.ravel())
    ids=np.empty((len(m.loop_triangles),3),np.int32);m.loop_triangles.foreach_get('loops',ids.ravel());tri=uv[ids]
    if obj.name.endswith('swept rounded mane'):
        vi=np.empty_like(ids);m.loop_triangles.foreach_get('vertices',vi.ravel())
        co=np.empty((len(m.vertices),3),np.float32);m.vertices.foreach_get('co',co.ravel());T=np.asarray(ob.matrix_world)
        out['xyz']=rest_coords(co@T[:3,:3].T+T[:3,3],pose)[vi];out['uv']=tri
    else:other.append(tri)
    ob.to_mesh_clear()
np.savez_compressed(D/'mane-chart.npz',other_uv=np.concatenate(other),**out)
