"""Reduce a suspected baked recess shadow without changing geometry or illumination."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
p=argparse.ArgumentParser();p.add_argument('config',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
cfg=json.loads(a.config.read_text(encoding='utf-8'));source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;o=editable_mesh(s);mat=o.data.materials[0]
nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes['Principled BSDF'];color=bs.inputs['Base Color'].links[0].from_socket
before_nodes={n.name for n in nodes};before_link=(color.node.name,color.identifier)
def node(kind,label):
    n=nodes.new(kind);n.label=label;return n
geo=node('ShaderNodeNewGeometry','Root pigment geometry')
local=node('ShaderNodeVectorTransform','Root pigment local position');local.vector_type='POINT';local.convert_from='WORLD';local.convert_to='OBJECT'
links.new(geo.outputs['Position'],local.inputs['Vector'])
xyz=node('ShaderNodeSeparateXYZ','Root pigment coordinates');links.new(local.outputs['Vector'],xyz.inputs[0])
def ramp(socket,limits,reverse,label):
    n=node('ShaderNodeMapRange',label);n.clamp=True;n.interpolation_type='SMOOTHSTEP'
    n.inputs['From Min'].default_value=limits[0];n.inputs['From Max'].default_value=limits[1]
    n.inputs['To Min'].default_value=1 if reverse else 0;n.inputs['To Max'].default_value=0 if reverse else 1
    links.new(socket,n.inputs['Value']);return n.outputs['Result']
lower=ramp(xyz.outputs['Z'],cfg['height_rise'],False,'Root pigment lower blend')
upper=ramp(xyz.outputs['Z'],cfg['height_fall'],True,'Root pigment upper blend')
xy=node('ShaderNodeCombineXYZ','Root pigment radial plane');links.new(xyz.outputs['X'],xy.inputs['X']);links.new(xyz.outputs['Y'],xy.inputs['Y'])
radius=node('ShaderNodeVectorMath','Root pigment radius');radius.operation='LENGTH';links.new(xy.outputs[0],radius.inputs[0])
radial=ramp(radius.outputs['Value'],cfg['radius_fall'],True,'Root pigment radial blend')
height=node('ShaderNodeMath','Root pigment height mask');height.operation='MULTIPLY';links.new(lower,height.inputs[0]);links.new(upper,height.inputs[1])
mask=node('ShaderNodeMath','Root pigment mask');mask.operation='MULTIPLY';links.new(height.outputs[0],mask.inputs[0]);links.new(radial,mask.inputs[1])
gain=node('ShaderNodeMath','Root pigment gain');gain.operation='MULTIPLY_ADD';gain.inputs[1].default_value=cfg['gain']-1;gain.inputs[2].default_value=1;links.new(mask.outputs[0],gain.inputs[0])
grade=node('ShaderNodeVectorMath','Root pigment correction');grade.operation='SCALE';links.new(color,grade.inputs[0]);links.new(gain.outputs[0],grade.inputs['Scale']);links.new(grade.outputs['Vector'],bs.inputs['Base Color'])
settings=json.loads(s['mission_material_config']);settings['variant']=cfg['variant'];settings['finial_root_pigment']={'source_sha256':digest,'config':cfg,'previous_base_color_link':before_link,'nodes_added':sorted({n.name for n in nodes}-before_nodes),'coordinate_space':'OBJECT','method':'Multiply existing linear pigment only inside a smooth local root mask. Preserve hue, grain, original packed pixels, relief, geometry and all lights. Test whether the inferred pigment contains an excessively dark baked recess.'}
s['mission_material_config']=json.dumps(settings);s['mission_variant']=cfg['variant']
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.samples=256;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=True;s.cycles.use_light_tree=False;s.render.use_persistent_data=True;s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(out/'queen.blend'),load_ui=False);s=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(settings,indent=2)+'\n',encoding='utf-8')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print('ROOT_PIGMENT_TRIAL_RENDERED',cfg['variant'],flush=True)
