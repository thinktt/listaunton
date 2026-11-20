"""Read the saved bishop light visibility, world shader and area-light settings."""
import argparse,json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);bpy.ops.wm.open_mainfile(filepath=str(ROOT/a.source),load_ui=False);s=bpy.context.scene
lights=[]
for ob in s.objects:
    if ob.type!='LIGHT':continue
    d=ob.data;spec={'name':ob.name,'type':d.type,'energy':d.energy,'color':list(d.color),'position':list(ob.location),
        'visible_diffuse':ob.visible_diffuse,'visible_glossy':ob.visible_glossy,'hide_render':ob.hide_render,
        'receiver':ob.light_linking.receiver_collection.name if ob.light_linking.receiver_collection else None}
    spec['matrix_world']=[list(row) for row in ob.matrix_world]
    for key in ['size','size_y','shape','spread']:
        if hasattr(d,key):spec[key]=getattr(d,key)
    lights.append(spec)
world=[]
for node in s.world.node_tree.nodes:
    values={}
    for socket in node.inputs:
        if hasattr(socket,'default_value'):
            v=socket.default_value
            try:v=list(v)
            except TypeError:pass
            values[socket.name]=v
    world.append({'name':node.name,'type':node.type,'inputs':values})
result={'source':a.source,'lights':lights,'world_nodes':world,'world_links':[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name] for l in s.world.node_tree.links]}
result['world_link_details']=[{'from_node':l.from_node.name,'from_socket':l.from_socket.name,'to_node':l.to_node.name,
    'to_socket':l.to_socket.name,'to_socket_index':list(l.to_node.inputs).index(l.to_socket)} for l in s.world.node_tree.links]
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
