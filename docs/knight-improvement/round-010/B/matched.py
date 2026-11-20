"""Compare the frozen carving and parent under identical lights and view registrations."""
from pathlib import Path
import sys,json
import bpy
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D))
from carve import load,border,sculpt,DESIGNS
from diagnostics import camera
from evidence import flat
from mission_scene import configure_render,render
def get_card(scene):
    lamp=scene.objects['Walnut | poll rear oval']
    return [lamp.matrix_world.copy(),lamp.data.energy,lamp.data.size,lamp.data.size_y]
def set_card(scene,values):
    lamp=scene.objects['Walnut | poll rear oval']
    lamp.matrix_world=values[0]
    lamp.data.energy,lamp.data.size,lamp.data.size_y=values[1:]
    bpy.context.view_layer.update()
def create():
    original=load('parent.blend')
    card=get_card(original)
    idx=int(sys.argv[sys.argv.index('--preview')+1]) if '--preview' in sys.argv else None
    for name,path in [('parent','parent.blend'),('B','knight.blend' if idx is None else 'parent.blend')]:
        scene=load(path)
        prefix='matched-' if idx is None else f'common-{idx}-'
        if idx is not None and name=='B':sculpt(scene,DESIGNS[idx])
        set_card(scene,card)
        configure_render(scene,72)
        border(scene,(245,281,524,434))
        render(scene,D/f'{prefix}{name}-fixed-walnut.png')
        scene.render.use_border=scene.render.use_crop_to_border=False
        scene.render.resolution_x=scene.render.resolution_y=576 if idx is None else 444
        scene.cycles.samples=32 if idx is None else 20
        yaw=json.loads(scene['knight_mission_pose'])['twist_degrees']
        for mode in ['walnut','clay']:
            if mode=='clay':flat(scene)
            for label,degree in [('near',0),('opposite',180),('rear',270),('front',90)]:
                camera(scene,yaw+degree,10)
                render(scene,D/f'{prefix}{name}-{label}-{mode}.png')
if __name__=='__main__':create()
