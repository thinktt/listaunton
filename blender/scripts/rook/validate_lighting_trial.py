"""Verify a rook lighting trial preserves shader, packed pigment and original rig."""
from pathlib import Path
import sys,json,hashlib
import bpy
ROOT=Path(__file__).resolve().parents[2]
args=sys.argv[sys.argv.index('--')+1:];variant=args[0];out=ROOT/'build/rook-mission'/variant
def value(v):
    if isinstance(v,(str,int,float,bool)) or v is None:return v
    try:return list(v)
    except TypeError:return str(v)
def shader(mat):
    nodes=[]
    for node in mat.node_tree.nodes:
        row={'name':node.name,'type':node.type,'inputs':[(a.identifier,value(a.default_value)) for a in node.inputs if hasattr(a,'default_value')]}
        for prop in ['operation','blend_type','uv_map','attribute_name','extension','interpolation','clamp']:
            if hasattr(node,prop):row[prop]=value(getattr(node,prop))
        if node.type=='TEX_IMAGE':
            assert node.image.packed_file
            row['image']={'name':node.image.name,'space':node.image.colorspace_settings.name,'sha256':hashlib.sha256(node.image.packed_file.data).hexdigest()}
        if hasattr(node,'color_ramp'):row['ramp']=[(e.position,list(e.color)) for e in node.color_ramp.elements]
        nodes.append(row)
    return {'nodes':nodes,'links':sorted((a.from_node.name,a.from_socket.identifier,a.to_node.name,a.to_socket.identifier) for a in mat.node_tree.links)}
def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);s=bpy.context.scene
    mats={o.name:shader(o.data.materials[0]) for o in s.objects if o.type=='MESH'}
    lights={o.name:{'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'matrix':list(map(list,o.matrix_world)),'diffuse':o.visible_diffuse,'glossy':o.visible_glossy,'shadow':o.data.use_shadow,'size':getattr(o.data,'size',None),'radius':getattr(o.data,'shadow_soft_size',None),'spot_size':getattr(o.data,'spot_size',None)} for o in s.objects if o.type=='LIGHT'}
    return mats,lights,shader(s.world)
base=ROOT/'models/rook/rook-rebuilt.blend';trial=out/'rook.blend'
ma,la,wa=snapshot(base);mb,lb,wb=snapshot(trial)
assert ma==mb,'Material changed in lighting trial';assert wa==wb,'World changed'
for name,light in la.items():
    expected=dict(light)
    if name in ['Rook upper edge','Rook front crescent','Rook rim edge']:expected['energy']=0
    assert expected==lb[name],name
new={name:row for name,row in lb.items() if name not in la}
assert len(new)==18
assert all(row['type']=='SPOT' and not row['diffuse'] and row['glossy'] and row['shadow'] for row in new.values())
report={'material_nodes_links_and_packed_images_exact':True,'world_exact':True,'original_lights_preserved_except_three_disabled_glossy_sources':True,'new_glossy_only_shadowed_spotlights':len(new),'source_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256(trial.read_bytes()).hexdigest(),'new_light_powers':{name:row['energy'] for name,row in new.items()}}
(out/'lighting-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('ROOK_LIGHTING_SCOPE_VALID',json.dumps(report))
