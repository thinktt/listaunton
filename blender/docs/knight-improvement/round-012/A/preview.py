from pathlib import Path
import sys
import bpy
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D))
from diagnostic_views import configure_render,open_model,render,use_side_camera
for scene_name in (['knight'] if '--candidate' in sys.argv else ['parent','knight']):
    scene=open_model(scene_name+'.blend')
    configure_render(scene,28)
    for material in ['wood','clay']:
        if material=='clay':
            for obj in scene.objects:
                if obj.type=='MESH' and not obj.hide_render:
                    for slot in obj.material_slots:slot.material=bpy.data.materials['Neutral satin clay']
        for view in ['fixed','side']:
            if view=='side':use_side_camera(scene)
            box=(185,392,395,705) if view=='fixed' else (270,330,675,915)
            scene.render.use_border=scene.render.use_crop_to_border=True
            a,c,b,d=box
            scene.render.border_min_x=a/1254;scene.render.border_max_x=b/1254
            scene.render.border_min_y=1-d/1254;scene.render.border_max_y=1-c/1254
            render(scene,D/f'{scene_name}-{material}-{view}-detail.png')
            if view=='side':
                scene=open_model(scene_name+'.blend');configure_render(scene,28)
