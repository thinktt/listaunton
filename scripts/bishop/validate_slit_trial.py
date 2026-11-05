"""Audit a declared slit-only edit against the preserved accepted bishop."""
import argparse,hashlib,json,sys,math
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector,kdtree
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--model',required=True);p.add_argument('--config',required=True);p.add_argument('--out',required=True)
p.add_argument('--geometry-only',action='store_true',help='Allow later material/lighting work while retaining the declared geometry and camera.')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads((ROOT/a.config).read_text())

def serial(value):
    if isinstance(value,(str,int,float,bool)) or value is None:return value
    try:return [serial(v) for v in value]
    except TypeError:return str(value)

def nodes(tree):
    data=[]
    for n in tree.nodes:
        inputs=[[s.identifier,serial(s.default_value)] for s in n.inputs if hasattr(s,'default_value')]
        im=getattr(n,'image',None)
        data.append([n.name,n.bl_idname,inputs,hashlib.sha256(im.packed_file.data).hexdigest() if im and im.packed_file else None])
    data.append([[l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier] for l in tree.links])
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()

def capture(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);bpy.context.view_layer.update()
    s=bpy.context.scene;graph=bpy.context.evaluated_depsgraph_get();result={'controls':{},'modifiers':{},'materials':{},'lights':{},'meshes':{}}
    result['camera']={'matrix':serial(s.camera.matrix_world),'scale':s.camera.data.ortho_scale,'shift':[s.camera.data.shift_x,s.camera.data.shift_y]}
    result['world']=nodes(s.world.node_tree)
    for ob in s.objects:
        if ob.type=='LIGHT':
            keys=['type','energy','color','size','size_y','shape','spread','spot_size','spot_blend','shadow_soft_size']
            result['lights'][ob.name]={k:serial(getattr(ob.data,k)) for k in keys if hasattr(ob.data,k)}
            result['lights'][ob.name].update(matrix=serial(ob.matrix_world),diffuse=ob.visible_diffuse,glossy=ob.visible_glossy,receiver=ob.light_linking.receiver_collection.name if ob.light_linking.receiver_collection else None)
        if ob.type!='MESH' or ob.hide_render:continue
        data={'vertices':[list(v.co) for v in ob.data.vertices],'faces':[list(f.vertices) for f in ob.data.polygons],
              'uvs':[[list(v.uv) for v in layer.data] for layer in ob.data.uv_layers],'matrix':serial(ob.matrix_world)}
        result['controls'][ob.name]=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
        modifiers=[]
        for m in ob.modifiers:
            d={'name':m.name,'type':m.type}
            for key in ['levels','render_levels','operation','solver','width','segments','limit_method','angle_limit','profile']:
                if hasattr(m,key):d[key]=serial(getattr(m,key))
            modifiers.append(d)
            if m.type=='BOOLEAN':result['cutter']={'matrix':serial(m.object.matrix_world),'vertices':[list(v.co) for v in m.object.data.vertices],'faces':[list(f.vertices) for f in m.object.data.polygons]}
        result['modifiers'][ob.name]=modifiers
        for material in ob.data.materials:result['materials'][material.name]=nodes(material.node_tree)
        ev=ob.evaluated_get(graph);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
        nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
        assert nonmanifold==0 and volume>0,(ob.name,nonmanifold,volume)
        pos=np.array([list(v.co) for v in me.vertices]);assert np.isfinite(pos).all()
        result['meshes'][ob.name]={'vertices':pos,'volume':volume,'nonmanifold':nonmanifold}
        bm.free();ev.to_mesh_clear()
    return result

source=ROOT/cfg['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['source_sha256']
old=capture(source);new=capture(ROOT/a.model)
for category in ['camera','controls']+([] if a.geometry_only else ['materials','lights','world']):assert old[category]==new[category],category
expected=json.loads(json.dumps(old['modifiers']))
for ms in expected.values():
    for m in ms:
        if m['type']=='BEVEL':m['width']*=cfg.get('bevel_factor',1)
for name,ms in expected.items():
    for i,m in enumerate(ms):
        for key,value in m.items():
            actual=new['modifiers'][name][i][key]
            assert abs(actual-value)<1e-8 if isinstance(value,float) else actual==value,(name,key,actual,value)
assert old['cutter']['matrix']==new['cutter']['matrix']
v=np.array(old['cutter']['vertices']);lo=v.min(0);hi=v.max(0);half=(hi[0]-lo[0])/2;depth=half*cfg['depth_factor'];center=(hi[0]+lo[0])/2
segments=cfg.get('segments',32)
cross=[(lo[0],hi[2])]+[(center+half*math.cos(math.pi-i*math.pi/segments),lo[2]-depth*math.sin(math.pi-i*math.pi/segments)) for i in range(segments+1)]+[(hi[0],hi[2])]
expected_vertices=np.array([(x,y,z) for y in [lo[1],hi[1]] for x,z in cross])
assert expected_vertices.shape==np.array(new['cutter']['vertices']).shape
cutter_error=float(np.max(np.abs(expected_vertices-np.array(new['cutter']['vertices']))))
assert cutter_error<1e-7,('Undeclared cutter shape',cutter_error)
count=len(cross);expected_faces=[tuple(range(count)),tuple(reversed(range(count,2*count)))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
assert sorted(tuple(sorted(f)) for f in expected_faces)==sorted(tuple(sorted(f)) for f in new['cutter']['faces'])
bevel=max(m['width'] for ms in expected.values() for m in ms if m['type']=='BEVEL')
from mathutils import Matrix
inv=Matrix(new['cutter']['matrix']).inverted()
local_report={}
for name,before in old['meshes'].items():
    after=new['meshes'][name]
    assert np.max(np.abs(before['vertices'].min(0)-after['vertices'].min(0)))<1e-6
    assert np.max(np.abs(before['vertices'].max(0)-after['vertices'].max(0)))<1e-6
    distances=[];counts=[]
    for reference,changed in [(before['vertices'],after['vertices']),(after['vertices'],before['vertices'])]:
        tree=kdtree.KDTree(len(reference))
        for i,point in enumerate(reference):tree.insert(Vector(point),i)
        tree.balance();maximum=0;count=0
        for point in changed:
            local=inv@Vector(point)
            affected=abs(local.x-center)<=half+bevel*4 and local.z>=lo[2]-depth-bevel*4
            if affected and 'finial' not in name:continue
            maximum=max(maximum,tree.find(Vector(point))[2]);count+=1
        distances.append(maximum);counts.append(count)
    assert max(distances)<5e-6,('Geometry changed away from slit',name,distances)
    local_report[name]={'bidirectional_outside_cut_max_distance':distances,'outside_cut_samples':counts,'nonmanifold_edges':0,'positive_volume':after['volume'],'vertex_count':len(after['vertices'])}
# Verify the actual through opening at the original straight portion and the new floor.
body=bpy.data.objects['Bishop - continuous turned body'].evaluated_get(bpy.context.evaluated_depsgraph_get())
matrix=Matrix(new['cutter']['matrix']);probes=[]
for along,clear in [(lo[2]+half,True),(lo[2]-depth*.7,True),(lo[2]-depth-half*.2,False)]:
    point=matrix@Vector((center,0,along));point.y=-4
    hit=body.ray_cast(point,Vector((0,1,0)),distance=8)[0]
    assert hit!=clear,('Slit or floor failed',along,clear,hit)
    probes.append({'local_z':float(along),'through_opening':not hit})
record={'passed':True,'source_sha256':cfg['source_sha256'],'model_sha256':hashlib.sha256((ROOT/a.model).read_bytes()).hexdigest(),
        'camera_controls_and_uvs_exactly_preserved':True,
        'lights_world_and_materials_preserved':all(old[k]==new[k] for k in ['lights','world','materials']),
        'material_lighting_preservation_required':not a.geometry_only,'cutter_max_coordinate_error':cutter_error,
        'declared_floor_extension':float(depth),'bevel_factor':cfg.get('bevel_factor',1),
        'geometry_scope':local_report,'slit_and_floor_probes':probes,'config':cfg}
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(record,indent=2)+'\n')
print('SLIT_SCOPE_VALIDATED',json.dumps(record),flush=True)
