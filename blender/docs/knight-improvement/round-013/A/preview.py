from pathlib import Path
import sys,bpy
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from diagnostic_views import configure_render,render,use_side_camera,clay_studio
for n in (['knight'] if '--candidate' in sys.argv else ['parent','knight']):
    for mat in ['wood','clay']:
        bpy.ops.wm.open_mainfile(filepath=str(D/(n+'.blend')),load_ui=False);s=bpy.context.scene;configure_render(s,64)
        if mat=='clay':clay_studio(s,10.3)
        for which in ['fixed','side']:
            if which=='side':use_side_camera(s)
            x,y,a,b=(416,418,619,549) if which=='fixed' else (545,215,818,435)
            s.render.use_border=s.render.use_crop_to_border=True
            s.render.border_min_x=(x+.01)/1254;s.render.border_max_x=(a+.01)/1254
            s.render.border_min_y=(1254-b+.01)/1254;s.render.border_max_y=(1254-y+.01)/1254
            render(s,D/f'detail-{n}-{mat}-{which}.png')
