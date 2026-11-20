"""Independently prove the declared fine-relief node is the only scene edit."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from validate_render_receivers import snapshot,check
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--config',required=True);p.add_argument('--model',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads((ROOT/a.config).read_text());source=ROOT/cfg['source'];model=ROOT/a.model
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);before=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);s=bpy.context.scene;after=snapshot()
old=before['materials'][cfg['material']];new=after['materials'][cfg['material']]
name='Bishop band-passed pigment relief'
assert set(new['nodes'])-set(old['nodes'])=={name}
node=bpy.data.materials[cfg['material']].node_tree.nodes[name]
assert node.bl_idname=='ShaderNodeTexImage' and node.interpolation=='Linear' and node.extension=='EXTEND'
assert node.image.colorspace_settings.name=='Non-Color' and node.image.packed_file
height=ROOT/cfg['height']['height_map'];assert sha(height)==cfg['height']['height_map_sha256']
disk=bpy.data.images.load(str(height),check_existing=False);disk.colorspace_settings.name='Non-Color'
assert np.array_equal(np.array(node.image.pixels[:]),np.array(disk.pixels[:]))
bpy.data.images.remove(disk)
removed=set(map(tuple,old['links']))-set(map(tuple,new['links']))
added=set(map(tuple,new['links']))-set(map(tuple,old['links']))
assert len(removed)==1 and next(iter(removed))[:2]==('Pigment relief','Val')
target=next(iter(removed))[2:]
uv=next(link for link in old['links'] if link[2:]==('Baked boxwood pigment','Vector'))
assert added=={(name,'Color',*target),(uv[0],uv[1],name,'Vector')},added
new['nodes'].pop(name);new['links']=old['links']
for key in before:assert json.dumps(before[key],sort_keys=True)==json.dumps(after[key],sort_keys=True),key
receivers=check(s,json.loads(s['bishop_receiver_trial']))
record=dict(passed=True,source=cfg['source'],source_sha256=sha(source),model=a.model,model_sha256=sha(model),
 config=a.config,config_sha256=sha(ROOT/a.config),height_map_sha256=sha(height),
 only_declared_fine_relief_node_and_two_links_changed=True,
 geometry_uvs_modifiers_original_nodes_color_atlas_pixels_lights_camera_world_render_paths_preserved=True,
 render_receivers=receivers,reopened_audit=True)
path=ROOT/a.out;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(record,indent=2)+'\n',newline='\n')
print('FINE_RELIEF_SCOPE_PASSED',flush=True)
