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


base=ROOT/'build/rook-mission/082-foot-flanks/rook.blend';trial=out/'rook.blend'
ma,la,wa=snapshot(base);mb,lb,wb=snapshot(trial)
params=json.loads((out/'parameters.json').read_text())
if 'foot_lights' in params:
 for label in ['left','right']:
  la['Rook foot flank '+label]['energy']=params['foot_lights'][label+'_power']
  la['Rook foot flank '+label]['size_y']=lb['Rook foot flank '+label]['size_y']
  assert abs(lb['Rook foot flank '+label]['size_y']-params['foot_lights']['size_y'])<1e-6
assert la==lb and wa==wb
for name,a in ma.items():
 b=mb[name]
 additions=[link for link in b['links'] if link[0].startswith('Foot finish ') and not link[2].startswith('Foot finish ')]
 permitted={'Roughness','Coat Roughness'} | ({'Coat Normal'} if params['coat_bump'] else set())
 assert len(additions)==len(permitted) and {link[3] for link in additions}==permitted
 assert all(link[2]=='Principled BSDF' for link in additions)
 b['nodes']=[n for n in b['nodes'] if not n['name'].startswith('Foot finish ')]
 b['links']=[link for link in b['links'] if not link[0].startswith('Foot finish ') and not link[2].startswith('Foot finish ')]
 assert a==b,name
(out/'finish-scope.json').write_text(json.dumps({'original_nodes_inputs_images_exact':True,'original_links_exact':True,'only_added_nodes_prefix':'Foot finish ','lights_world_preserved_except_declared_foot_changes':True,'source_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256(trial.read_bytes()).hexdigest()},indent=2)+'\n')
print('FOOT_FINISH_SCOPE_VALID',variant)
