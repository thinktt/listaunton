from pathlib import Path
import bpy,json,math,sys
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'build/queen-mission/168-fitted-polished-finial/queen.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
report=[]
cfg=json.loads(s['mission_material_config'])
for spec in cfg['lights']:
    if ('finial-' in spec['name'] and spec['name'].endswith('-spot')) or spec['name'].startswith('Finial retained '):
        o=bpy.data.objects[spec['name']];data=o.data
        report.append({'name':o.name,'position':list(o.location),'rotation_euler':list(o.rotation_euler),
                       'size':data.shadow_soft_size,'specified_size':spec['size'],'spot_degrees':math.degrees(data.spot_size),
                       'energy':data.energy,'color':list(data.color),'use_shadow':data.use_shadow,
                       'receivers':[r.get('mission_render_region') for r in o.light_linking.receiver_collection.objects]})
out=ROOT/'build/queen-mission/168-fitted-polished-finial'
(out/'actual-finial-lights.json').write_text(json.dumps(report,indent=2)+'\n')
print('ACTUAL_FINIAL_LIGHTS',json.dumps(report),flush=True)
