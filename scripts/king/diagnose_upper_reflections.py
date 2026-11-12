"""Isolate the accepted king's broad socket/collar glossy illumination."""
from pathlib import Path
import hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu
from render_regions import controls
from focused_reflections import target

def diagnose(source_name,output_name):
    source=ROOT/source_name;digest=hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
    out=ROOT/output_name;out.mkdir(parents=True,exist_ok=True)
    body=next(o for o in controls(s) if 'body' in o.name);co=np.array([v.co[:] for v in body.data.vertices]).reshape(-1,96,3)
    profile=[[i,float(np.linalg.norm(row[:,:2],axis=1).mean()),float(row[:,2].mean())] for i,row in enumerate(co)]
    probes=[]
    for pixel in [(435,426),(440,490),(435,532),(440,758),(500,772),(563,758),(505,635),(505,365)]:
        ob,point,direction,normal=target(s,*pixel);probes.append(dict(pixel=pixel,point=list(point),normal=list(normal),reflection=list(direction),receiver=ob.get('king_render_region')))
    lights=[o for o in s.objects if o.type=='LIGHT'];powers={o.name:o.data.energy for o in lights};world=s.world.node_tree.nodes['Background'].inputs['Strength'];worldpower=world.default_value
    (out/'diagnostic.json').write_text(json.dumps(dict(source=source_name,source_sha256=digest,profile=profile,probes=probes,light_powers=powers),indent=2)+'\n',encoding='utf-8')
    w=s.render.resolution_x;h=s.render.resolution_y;s.render.use_border=True;s.render.use_crop_to_border=False
    s.render.border_min_x=300/w;s.render.border_max_x=710/w;s.render.border_min_y=1-845/h;s.render.border_max_y=1-320/h
    s.cycles.samples=128;s.cycles.use_denoising=True;s.render.use_persistent_data=True
    groups=[('without-upper-varnish',['Upper varnish'],False),('without-front-varnish',['Front varnish'],False),('diffuse-and-focused',['Upper varnish','Front varnish'],False),('upper-only',['Upper varnish'],True),('front-only',['Front varnish'],True)]
    for name,names,isolated in groups:
        for light in lights:light.data.energy=powers[light.name] if ((light.name in names)==isolated) else 0
        world.default_value=0 if isolated else worldpower
        s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    print('KING_UPPER_REFLECTION_DIAGNOSTIC_DONE')

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:];diagnose(*args)
