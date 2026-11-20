"""Verify preserved source pigment, BSDF finish and old rig for the floor checkpoint."""
from pathlib import Path
import bpy,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];variant=sys.argv[sys.argv.index('--')+1];out=ROOT/'build/rook-mission'/variant
base=ROOT/'history/rook-mission-037/models/rook/rook-rebuilt.blend';trial=out/'rook.blend'
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);s=bpy.context.scene;body=next(o for o in s.objects if o.get('rook_editable_control'));bs=body.data.materials[0].node_tree.nodes['Principled BSDF']
 values={}
 for socket in bs.inputs:
  if hasattr(socket,'default_value'):
   v=socket.default_value
   try:v=list(v)
   except TypeError:pass
   values[socket.identifier]=v
 lights={o.name:{'matrix':list(map(list,o.matrix_world)),'energy':o.data.energy,'color':list(o.data.color),'type':o.data.type,'size':getattr(o.data,'size',None),'size_y':getattr(o.data,'size_y',None),'diffuse':o.visible_diffuse,'glossy':o.visible_glossy,'shadow':o.data.use_shadow,'receivers':sorted(p.get('rook_render_receiver') for p in o.light_linking.receiver_collection.objects) if o.light_linking.receiver_collection else None} for o in s.objects if o.type=='LIGHT'}
 images={i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file}
 return values,lights,images
va,la,ia=snapshot(base);vb,lb,ib=snapshot(trial);assert va==vb
for name,row in la.items():assert row==lb[name],name
for name,h in ia.items():assert ib[name]==h,name
new=set(lb)-set(la);assert new=={'Rook floor-edge strip'};row=lb['Rook floor-edge strip'];assert row['energy']==1000 and row['receivers']==['floor_edge'] and row['glossy'] and not row['diffuse'] and row['shadow'];assert max(abs(a-b) for a,b in zip(row['color'],[1,.72,.49]))<1e-6
body=next(o for o in bpy.context.scene.objects if o.get('rook_editable_control'));mat=body.data.materials[0];bs=mat.node_tree.nodes['Principled BSDF'];assert mat.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node==bs;assert bs.inputs['Base Color'].links[0].from_node.image.name=='Rook pigment atlas v2'
report={'principled_finish_parameters_exact':True,'old_lights_and_receiver_tags_exact':True,'source_packed_images_preserved':True,'new_warm_floor_only_glossy_strip':row,'final_surface':'Principled BSDF with packed pigment atlas v2','current_lights_not_baked':True,'inherited_pigment_illumination_artifacts_remain':True,'source_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'trial_sha256':hashlib.sha256(trial.read_bytes()).hexdigest()};(out/'finish-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('FLOOR_FINISH_VALIDATED')
