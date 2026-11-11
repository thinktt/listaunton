"""Verify a shape study preserves material, lights, camera and world transform."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
ROOT=Path(__file__).resolve().parents[2]
def value(x):
    if isinstance(x,(str,int,float,bool)) or x is None:return x
    try:return list(x)
    except TypeError:return str(x)
def inspect(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);s=bpy.context.scene;o=editable_mesh(s);m=o.data.materials[0];cam=s.camera
    nodes={n.name:{'type':n.bl_idname,'inputs':{i.identifier:value(i.default_value) for i in n.inputs if hasattr(i,'default_value')},'image':hashlib.sha256(bytes(n.image.packed_file.data)).hexdigest() if getattr(n,'image',None) and n.image.packed_file else None} for n in m.node_tree.nodes}
    links=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links)
    lights={o.name: {'matrix':[x for row in o.matrix_world for x in row],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'shadow':o.data.use_shadow,'diffuse':o.visible_diffuse,'glossy':o.visible_glossy,'radius':getattr(o.data,'shadow_soft_size',None),'parts':sorted(p['mission_render_region'] for p in o.light_linking.receiver_collection.objects) if o.light_linking.receiver_collection else None} for o in s.objects if o.type=='LIGHT'}
    return {'material_nodes':nodes,'material_links':links,'lights':lights,'camera':{'matrix':[x for row in cam.matrix_world for x in row],'type':cam.data.type,'scale':cam.data.ortho_scale,'shift':[cam.data.shift_x,cam.data.shift_y],'resolution':[s.render.resolution_x,s.render.resolution_y]},'object_matrix':[x for row in o.matrix_world for x in row]}
p=argparse.ArgumentParser();p.add_argument('current');p.add_argument('--baseline',default='history/queen-mission-018/queen-rebuilt.blend');p.add_argument('--out',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
before=inspect(ROOT/a.baseline);after=inspect(ROOT/a.current)
for key in before:assert before[key]==after[key],key
report={'passed':True,'source_sha256':hashlib.sha256((ROOT/a.current).read_bytes()).hexdigest(),'baseline_sha256':hashlib.sha256((ROOT/a.baseline).read_bytes()).hexdigest(),'unchanged':list(before),'real_bsdf_material_preserved':True,'all_packed_image_bytes_identical':True,'light_count':len(before['lights'])}
(ROOT/a.out/'profile-preservation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
