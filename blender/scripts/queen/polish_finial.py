"""Reduce relief only on the exposed finial, retaining the body's wood surface."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh

def apply_finial_polish(scene,factor):
    assert 0<=factor<=1
    mat=editable_mesh(scene).data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links
    bump=nodes.get('Bump.001');assert bump.type=='BUMP' and not bump.inputs['Distance'].is_linked
    old=float(bump.inputs['Distance'].default_value)
    geom=nodes.new('ShaderNodeNewGeometry');local=nodes.new('ShaderNodeVectorTransform');local.label='Local finial coordinates';local.vector_type='POINT';local.convert_from='WORLD';local.convert_to='OBJECT';links.new(geom.outputs['Position'],local.inputs['Vector'])
    xyz=nodes.new('ShaderNodeSeparateXYZ');links.new(local.outputs['Vector'],xyz.inputs[0])
    height=nodes.new('ShaderNodeMapRange');height.clamp=True;height.interpolation_type='SMOOTHSTEP'
    links.new(xyz.outputs['Z'],height.inputs['Value']);height.inputs['From Min'].default_value=4.04;height.inputs['From Max'].default_value=4.12
    xy=nodes.new('ShaderNodeCombineXYZ');links.new(xyz.outputs['X'],xy.inputs['X']);links.new(xyz.outputs['Y'],xy.inputs['Y'])
    length=nodes.new('ShaderNodeVectorMath');length.operation='LENGTH';links.new(xy.outputs[0],length.inputs[0])
    radial=nodes.new('ShaderNodeMath');radial.operation='LESS_THAN';radial.inputs[1].default_value=.235;links.new(length.outputs['Value'],radial.inputs[0])
    mask=nodes.new('ShaderNodeMath');mask.operation='MULTIPLY';links.new(height.outputs['Result'],mask.inputs[0]);links.new(radial.outputs[0],mask.inputs[1])
    distance=nodes.new('ShaderNodeMapRange');links.new(mask.outputs[0],distance.inputs['Value']);distance.inputs['To Min'].default_value=old;distance.inputs['To Max'].default_value=old*factor
    links.new(distance.outputs['Result'],bump.inputs['Distance'])
    return {'factor':factor,'original_distance':old,'finial_distance':old*factor,'coordinate_space':'OBJECT','local_z_transition':[4.04,4.12],'local_radius_max':.235,'method':'Smooth local relief reduction on the seated egg only, in object coordinates so it follows the piece. The same existing height field drives the wood and varnish normals; all other surface parameters stay unchanged.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',default='build/queen-mission/163-finial-pigment-repair/queen.blend');p.add_argument('--variant',default='166-finial-polish');p.add_argument('--factor',type=float,default=.25)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    source=ROOT/args.source;digest=hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    cfg=json.loads(s['mission_material_config']);cfg['finial_polish']=dict(apply_finial_polish(s,args.factor),source_sha256=digest);cfg['variant']=args.variant
    s['mission_material_config']=json.dumps(cfg);s['mission_variant']=args.variant
    out=ROOT/'build/queen-mission'/args.variant;out.mkdir(exist_ok=True,parents=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
    (out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
    print('FINIAL_POLISH_SAVED',json.dumps(cfg['finial_polish']),flush=True)
if __name__=='__main__':main()
