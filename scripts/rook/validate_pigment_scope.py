"""Verify that a pigment-only trial preserves shader graph, rig and all control UVs."""
from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2];variant=sys.argv[sys.argv.index('--')+1];out=ROOT/'build/rook-mission'/variant

def plain(v):
 if isinstance(v,(str,int,float,bool)):return v
 try:return list(v)
 except:return str(v)
def snap(p):
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);s=bpy.context.scene;body=next(o for o in s.objects if o.get('rook_editable_control'));mat=body.data.materials[0];nodes={n.name:{'type':n.bl_idname,'inputs':{str(i)+sock.name:plain(sock.default_value) for i,sock in enumerate(n.inputs) if hasattr(sock,'default_value')}} for n in mat.node_tree.nodes};links=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in mat.node_tree.links)
 lights={o.name:{'matrix':list(map(list,o.matrix_world)),'data':{k:plain(getattr(o.data,k)) for k in ['type','energy','color','size','size_y','shape','use_shadow'] if hasattr(o.data,k)},'visibility':{k:getattr(o,k) for k in ['visible_glossy','visible_diffuse','hide_render']},'receivers':sorted(x.name for x in o.light_linking.receiver_collection.objects) if o.light_linking.receiver_collection else []} for o in s.objects if o.type=='LIGHT'}
 uvs={o.name:{u.name:hashlib.sha256(np.array([v.uv[:] for v in u.data],np.float32).tobytes()).hexdigest() for u in o.data.uv_layers} for o in s.objects if o.type=='MESH'};image=mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image;assert image.packed_file
 return {'nodes':nodes,'links':links,'lights':lights,'uvs':uvs},image.name
baseline_path=Path(sys.argv[sys.argv.index('--baseline')+1]) if '--baseline' in sys.argv else ROOT/'models/rook/rook-rebuilt.blend'
baseline,old=snap(baseline_path);actual,new=snap(out/'rook.blend');assert baseline==actual,'Unexpected non-image shader/rig/UV edit';assert old!=new
(out/'pigment-scope-validation.json').write_text(json.dumps({'shader_graph_and_defaults_exact':True,'lights_and_links_exact':True,'all_control_and_receiver_uvs_exact':True,'old_image':old,'new_image':new,'scope':'Node types/default inputs/links, light parameters/transforms/receiver membership, mesh UV bytes. Complements geometry and material validator; not visual proof.'},indent=2)+'\n');print('PIGMENT_SCOPE_VALIDATED',variant)
