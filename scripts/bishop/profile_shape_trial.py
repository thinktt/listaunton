"""Controlled profile edits with regenerated exact receivers and neutral views."""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy, numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from render_regions import partition_socket, BODY
from validate_render_receivers import snapshot, check

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('config');p.add_argument('--no-render',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);config_path=ROOT/a.config
cfg=json.loads(config_path.read_text());source=ROOT/cfg['source']
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(source)==cfg['source_sha256']
out=ROOT/'build/bishop-mission'/cfg['variant']
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
out.mkdir(parents=True,exist_ok=True)
profile=json.loads((ROOT/cfg['profile']).read_text())
align=json.loads((ROOT/'assets/bishop/original-alignment.json').read_text())
factor=1254/300/align['scale']/profile['scale'];co=math.cos(math.radians(54))
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
before=snapshot()
body=bpy.data.objects[BODY]
old_parts=[o for o in s.objects if o.get('bishop_render_region')]
part_names=[o.name for o in old_parts]
receiver_cfg=json.loads(s['bishop_receiver_trial'])
band=list(receiver_cfg['socket_z_band'])
# Capture every membership before removing derived geometry. Restore these
# exact semantic links after replacing the receivers with the new surface.
memberships={c.name:[o.name for o in c.objects] for c in bpy.data.collections
             if any(o.name in part_names for o in c.objects)}
region_collections={c.name for part in old_parts for c in part.users_collection
                    if c.name.startswith('Bishop exact render regions')}
for ob in old_parts:
    mesh=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
    if mesh.users==0:bpy.data.meshes.remove(mesh)
for name in region_collections:
    c=bpy.data.collections.get(name)
    if c and not c.objects and not c.children:bpy.data.collections.remove(c)
body.hide_render=False
for key,(radius,axis_y) in cfg.get('body_rings',{}).items():
    i=int(key);old_radius,old_y=profile['profile'][i]
    for v in body.data.vertices[i*128:(i+1)*128]:
        v.co.x*=radius/old_radius;v.co.y*=radius/old_radius
        v.co.z+=(old_y-axis_y)*factor/co
    profile['profile'][i]=[radius,axis_y]
body.data.update();bpy.context.view_layer.update()
parts,partition=partition_socket(s,*band)
for name,names in memberships.items():
    collection=bpy.data.collections.get(name)
    assert collection is not None,name
    for ob in list(collection.objects):
        if ob.name not in names:collection.objects.unlink(ob)
    for obname in names:
        if obname not in collection.objects:collection.objects.link(bpy.data.objects[obname])
after=snapshot()
for key in ['lights','materials','camera','world','color_management','render_path','objects']:
    assert before[key]==after[key],('Unintended scene change',key)
for name,row in before['meshes'].items():
    if name in part_names:continue
    new=after['meshes'][name]
    if name==BODY:
        for k in row:
            if k!='mesh':assert row[k]==new[k],(name,k)
        for k in row['mesh']:
            if k!='hashes':assert row['mesh'][k]==new['mesh'][k],(name,k)
        for k,value in row['mesh']['hashes'].items():
            if k not in ['positions','normals']:assert value==new['mesh']['hashes'][k],(name,k)
    else:assert row==new,('Unintended mesh change',name)
profile['revision']=cfg['variant']
profile['mission_shape_refit']={'config':str(config_path.relative_to(ROOT)).replace('\\','/'),
                              'source':cfg['source'],'source_sha256':cfg['source_sha256'],
                              'profile':cfg['profile'],'body_rings':cfg['body_rings']}
s['bishop_shape_refit']=json.dumps(profile['mission_shape_refit'],sort_keys=True)
s.cycles.samples=cfg.get('samples',128);s.cycles.use_adaptive_sampling=False
s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False
s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'bishop.blend'))
(out/'profile.json').write_text(json.dumps(profile,indent=2)+'\n')
bpy.ops.wm.open_mainfile(filepath=str(out/'bishop.blend'),load_ui=False);s=bpy.context.scene
reopened=snapshot()
for key in ['lights','materials','camera','world','color_management','render_path','objects']:
    assert after[key]==reopened[key],('Saved scene differs',key)
receiver_check=check(s,receiver_cfg)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
if not a.no_render:
    bpy.ops.render.render(write_still=True)
    # Neutral material removes inherited pigment and relief. The saved wood
    # scene is not overwritten by this diagnostic override.
    mat=bpy.data.materials.new('Geometry comparison neutral');mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    balance=json.loads(s.get('bishop_diffuse_balance','{}')).get('diffuse_light_factor',1)
    bsdf.inputs['Base Color'].default_value=(.28/balance,.30/balance,.34/balance,1)
    bsdf.inputs['Roughness'].default_value=.3
    for ob in s.objects:
        if ob.type=='MESH' and not ob.hide_render:
            ob.data.materials.clear();ob.data.materials.append(mat)
    s.cycles.samples=64;s.render.filepath=str(out/'neutral.png')
    bpy.ops.render.render(write_still=True)
report={'config':cfg,'model_sha256':sha(out/'bishop.blend'),'source_unchanged':sha(source)==cfg['source_sha256'],
        'source_state':before,'reopened_state':reopened,'receiver_check':receiver_check,
        'materials_lighting_camera_uvs_topology_button_and_cutter_preserved':True,
        'saved_and_reopened':True,'partition':partition}
(out/'trial-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('BISHOP_PROFILE_SHAPE_TRIAL_COMPLETE',cfg['variant'],flush=True)
