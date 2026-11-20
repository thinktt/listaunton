"""Registered physical diffuse and clay views. All diagnostic materials are in-memory."""
from pathlib import Path
import sys,math,json
import bpy
from mathutils import Vector
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path[:0]=[str(D),str(R/'scripts/knight')]
from mission_scene import configure_render,render,use_side_camera,visible_meshes,sha
from diagnostic_views import clay_studio,orbit
def open_model(name):
    bpy.ops.wm.open_mainfile(filepath=str(D/(name+'.blend')),load_ui=False);return bpy.context.scene
def crop(s,box):
    x,y,a,b=box;w=s.render.resolution_x;h=s.render.resolution_y
    s.render.use_border=s.render.use_crop_to_border=True
    s.render.border_min_x=(x+.1)/w;s.render.border_max_x=(a+.1)/w
    s.render.border_min_y=(h-b+.1)/h;s.render.border_max_y=(h-y+.1)/h
def light(s):
    clay_studio(s,10.3)
def render_trial(name,assembly=None):
    for kind in ('walnut','clay'):
        s=open_model('parent' if assembly else name)
        if assembly:assembly(s)
        if kind=='clay':light(s)
        configure_render(s,38)
        crop(s,(429,415,620,529));render(s,D/f'{name}-{kind}-fixed.png')
        use_side_camera(s);crop(s,(566,228,794,403));render(s,D/f'{name}-{kind}-side.png')
def whole(name,full):
    for k in ['clay','walnut'] if full else ['clay']:
        s=open_model(name);configure_render(s,22);s.render.resolution_x=s.render.resolution_y=520
        if k=='clay':light(s)
        for angle in [-30,0,30,180]:
            cam=s.camera;az=math.radians(10.3+angle);tar=Vector((-.05,0,3.98));e=math.radians(8)
            cam.data.ortho_scale=4.;cam.data.shift_x=cam.data.shift_y=0
            cam.location=tar+Vector((9*math.sin(az)*math.cos(e),-9*math.cos(az)*math.cos(e),9*math.sin(e)));cam.rotation_euler=(tar-cam.location).to_track_quat('-Z','Y').to_euler()
            render(s,D/f'{name}-head-{k}-{angle}.png')
def final():
    s=open_model('knight');configure_render(s,144);render(s,D/'wood.png');use_side_camera(s);render(s,D/'wood-side.png')
    (D/'rendered.json').write_text(json.dumps({'scene_sha256':sha(D/'knight.blend'),'samples':144,'fixed':sha(D/'wood.png'),'side':sha(D/'wood-side.png')},indent=2)+'\n')
if __name__=='__main__':
    if sys.argv[-1]=='parent':whole('parent',True);render_trial('parent')
    if sys.argv[-1]=='final':final();whole('knight',True);render_trial('knight')
