"""Compare physical frosted-card sizes and directions on one saved carving."""
from pathlib import Path
import sys,bpy
sys.dont_write_bytecode=True;D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from lamps import place,measure
from mission_scene import configure_render,render
bpy.ops.wm.open_mainfile(filepath=str(D/'knight.blend'),load_ui=False);s=bpy.context.scene;configure_render(s,96)
s.render.use_crop_to_border=s.render.use_border=True;s.render.border_min_x=451.01/1254;s.render.border_max_x=580.01/1254;s.render.border_min_y=(1254-515+.01)/1254;s.render.border_max_y=(1254-449+.01)/1254
aim=measure(s)
for name,points,axes,energy,lpoints,ld,lp in [
    ('soft',[(496,469),(499,470),(503,474)],(.32,.21),.046,[(493,497),(500,499),(506,500),(515,501),(522,500)],(.55,.28),.106),
    ('scattered',[(491,470),(496,471),(501,473)],(.23,.17),.039,[(488,495),(494,498),(502,499),(508,500),(517,500)],(.44,.34),.103),
    ('close',[(495,469),(497,471),(501,473)],(.23,.13),.046,[(491,497),(495,498),(501,499),(509,500),(519,500)],(.39,.29),.097),
    ('front',[(500,470),(503,471),(506,473),(509,474)],(.30,.20),.061,[(494,498),(500,499),(507,501),(515,501),(522,500)],(.49,.25),.101),
    ('broad',[(492,470),(497,472),(503,474),(510,478)],(.36,.265),.075,[(488,494),(498,499),(508,500),(520,501)],(.52,.31),.089)]:
    place(s,aim,'Eye reflection upper','near eye',points,.61,axes,energy,24)
    place(s,aim,'Eye reflection lower','continuous horse head and neck',lpoints,.60,ld,lp,22)
    s.objects['Eye reflection lower'].data.color=(1.,.60,.35)
    render(s,D/f'card-{name}.png')
