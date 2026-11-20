from pathlib import Path
import sys,json,hashlib,bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/rook'));from render_regions import validate
exec(compile((ROOT/'scripts/rook/validate_lighting_trial.py').read_text().split("base=ROOT/")[0],'lighting-snapshot','exec'))
base=ROOT/'history/rook-mission-021/models/rook/rook-rebuilt.blend';trial=out/'rook.blend';ma,la,wa=snapshot(base);mb,lb,wb=snapshot(trial)
assert ma==mb and wa==wb
for name,expected in la.items():
 expected=dict(expected)
 if name=='Rook front crescent':expected['energy']=0
 assert lb[name]==expected,name
assert set(lb)-set(la)=={'Rook shoulder strip'}
s=bpy.context.scene;new=s.objects['Rook shoulder strip'];assert new.data.energy==300 and not new.visible_diffuse and new.visible_glossy and new.data.use_shadow
assert {o.get('rook_render_receiver') for o in new.light_linking.receiver_collection.objects}=={'shoulder'}
for name in ['Rook upper edge','Rook rim edge']:
 assert {o.get('rook_render_receiver') for o in s.objects[name].light_linking.receiver_collection.objects}=={'rim'}
rr=validate(s)
(out/'lighting-validation.json').write_text(json.dumps({'materials_images_world_exact':True,'old_lights_exact_except_front_crescent_disabled_and_two_receiver_links':'Rook upper edge and Rook rim edge restricted to rim','new_shoulder_strip_watts':300,'foot_preserved':True,'receivers':rr,'source_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256(trial.read_bytes()).hexdigest()},indent=2)+'\n');print('SHOULDER_LIGHT_SCOPE_VALID')
