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
    lights={o.name:{'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'matrix':list(map(list,o.matrix_world)),'diffuse':o.visible_diffuse,'glossy':o.visible_glossy,'shadow':o.data.use_shadow,'size':getattr(o.data,'size',None),'size_y':getattr(o.data,'size_y',None),'shape':getattr(o.data,'shape',None),'receivers':sorted(x.name for x in o.light_linking.receiver_collection.objects) if o.light_linking.receiver_collection else [],'radius':getattr(o.data,'shadow_soft_size',None),'spot_size':getattr(o.data,'spot_size',None)} for o in s.objects if o.type=='LIGHT'}
    return mats,lights,shader(s.world)


base=ROOT/'build/rook-mission/086-foot-finish/rook.blend';trial=out/'rook.blend'
params=json.loads((out/'parameters.json').read_text())
ma,la,wa=snapshot(base);mb,lb,wb=snapshot(trial);assert ma==mb and wa==wb
for name,row in la.items():
 expected=dict(row)
 if name=='Rook foot flank right':expected['energy']=0
 assert expected==lb[name],name
new={name:row for name,row in lb.items() if name not in la};assert set(new)=={'Rook foot arc inner','Rook foot arc outer'}
for row in new.values():
 assert row['energy']==params['new_power_each'] and row['type']=='AREA' and row['shape']=='RECTANGLE'
 assert abs(row['size']-.4)<1e-6 and abs(row['size_y']-.03)<1e-6
 assert not row['diffuse'] and row['glossy'] and row['shadow']
 assert row['receivers']==la['Rook foot flank right']['receivers']
(out/'arc-scope.json').write_text(json.dumps({'material_and_packed_images_world_exact':True,'old_lights_exact_except_disabled_right_flank':True,'two_declared_foot_area_lights':new,'source_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256(trial.read_bytes()).hexdigest()},indent=2)+'\n')
print('FOOT_ARC_SCOPE_VALID',variant)
