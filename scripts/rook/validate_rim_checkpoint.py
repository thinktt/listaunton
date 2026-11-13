from pathlib import Path
import bpy,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
exec((ROOT/'scripts/rook/validate_lighting_trial.py').read_text().split("base=ROOT/")[0])
base=ROOT/'history/rook-mission-025/models/rook/rook-rebuilt.blend';trial=out/'rook.blend'
ma,la,wa=snapshot(base);mb,lb,wb=snapshot(trial)
material=next(iter(ma.values()));assert all(m==material for m in ma.values());assert all(m==material for m in mb.values());assert wa==wb
for name,light in la.items():assert light==lb[name],name
new={n:r for n,r in lb.items() if n not in la};assert len(new)==2
for name,row in new.items():
 assert row['type']=='AREA' and row['energy']==1500 and not row['diffuse'] and row['glossy'] and row['shadow']
 o=bpy.data.objects[name];assert {p.get('rook_render_receiver') for p in o.light_linking.receiver_collection.objects}=={'rim_bevel'};assert o.data.size==6 and abs(o.data.size_y-.12)<1e-6
for name in ['Rook upper edge','Rook rim edge']:
 assert {p.get('rook_render_receiver') for p in bpy.data.objects[name].light_linking.receiver_collection.objects}=={'rim','rim_bevel'}
report={'material_nodes_links_packed_images_exact':True,'world_exact':True,'original_light_properties_exact':True,'old_rim_lights_cover_same_partitioned_surface':True,'new_upper_bevel_only_glossy_strip_count':2,'watts_each':1500,'source_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'trial_sha256':hashlib.sha256(trial.read_bytes()).hexdigest()}
(out/'lighting-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('RIM_LIGHT_VALIDATED',json.dumps(report))
