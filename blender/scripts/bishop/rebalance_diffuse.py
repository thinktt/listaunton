"""Give inferred pigment physical headroom without increasing the glossy lights."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--variant',required=True);p.add_argument('--factor',type=float,default=3)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert a.factor>1
source=ROOT/a.source;bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
before=[float(v) for row in s.camera.matrix_world for v in row]
lights={}
for ob in s.objects:
    if ob.type=='LIGHT' and ob.visible_diffuse:
        assert not ob.visible_glossy,'A diffuse balance must not silently multiply shared glossy lights.'
        lights[ob.name]=[ob.data.energy,ob.data.energy*a.factor];ob.data.energy*=a.factor
world=s.world.node_tree.nodes['Background'].inputs[1];world.default_value*=a.factor
materials={m for ob in s.objects if ob.type=='MESH' and not ob.hide_render for m in ob.data.materials if m and m.use_nodes}
for mat in materials:
    n=mat.node_tree.nodes;l=mat.node_tree.links;b=n['Principled BSDF'];old=b.inputs['Base Color'].links[0].from_socket
    node=n.new('ShaderNodeVectorMath');node.name='Diffuse energy balance';node.operation='SCALE';node.inputs['Scale'].default_value=1/a.factor
    l.new(old,node.inputs[0]);l.new(node.outputs[0],b.inputs['Base Color'])
assert before==[float(v) for row in s.camera.matrix_world for v in row]
record={'source':a.source,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'variant':a.variant,'diffuse_light_factor':a.factor,'starting_pigment_factor':1/a.factor,'lights':lights,'glossy_light_powers_unchanged':True,'geometry_and_camera_unchanged':True,
    'reason':'23.55% of confident pixels required red albedo above 0.85 in the prior response. Increase incident diffuse energy and reduce starting pigment so the next fit stays physically bounded without a green clipping artifact. Indirect bounces may differ; fit and inspect actual BSDF.'}
s['bishop_diffuse_balance']=json.dumps(record,sort_keys=True)
out=ROOT/'build/bishop-mission'/a.variant;out.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'bishop.blend'))
record['saved_model_sha256']=hashlib.sha256((out/'bishop.blend').read_bytes()).hexdigest()
(out/'parameters.json').write_text(json.dumps(record,indent=2)+'\n')
print('BISHOP_DIFFUSE_BALANCE_PREPARED',json.dumps(record),flush=True)
