"""Separate the accepted upper/lower base reflections without modifying source."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu
from focused_reflections import target
from render_regions import clear_light_path

def main(source_name,output):
    source=ROOT/source_name;digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    s=bpy.context.scene;assert not s.cycles.use_light_tree;gpu(s)
    out=ROOT/output;out.mkdir(parents=True,exist_ok=True)
    groups={'upper':['Base upper focused'],'lower':['Base lower shaped 03','Base lower shaped 04','Base lower shaped 05']}
    names=sum(groups.values(),[]);powers={n:bpy.data.objects[n].data.energy for n in names}
    lamps={}
    for name in names:
        ob=bpy.data.objects[name];d=ob.data
        lamps[name]=dict(type=d.type,energy=d.energy,color=list(d.color),position=list(ob.location),rotation=list(ob.rotation_euler),radius=d.shadow_soft_size,cone=d.spot_size,blend=d.spot_blend,casts_shadows=d.use_shadow,receivers=[o.get('king_render_region',o.name) for o in ob.light_linking.receiver_collection.objects])
    probes=[]
    for x,y in [(550,840),(568,854),(580,870),(576,895),(595,930),(608,952)]:
        ob,point,direction,normal=target(s,x,y)
        probes.append(dict(pixel=[x,y],receiver=ob.get('king_render_region'),point=list(point),normal=list(normal),reflection=list(direction),clear_path_1=clear_light_path(s,point,normal,direction,1),clear_path_6=clear_light_path(s,point,normal,direction,6)))
    report=dict(source=source_name,source_sha256=digest,groups=groups,lights=lamps,probes=probes,light_tree=False,samples=s.cycles.samples,note='Actual real-BSDF group responses. Probes use smooth geometric normals, not perturbed coat normals. Diagnostic only; source and reference images unchanged.')
    (out/'response-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(lamps,indent=2),flush=True)
    w,h=s.render.resolution_x,s.render.resolution_y;s.render.use_border=True;s.render.use_crop_to_border=False
    s.render.border_min_x=195/w;s.render.border_max_x=805/w;s.render.border_min_y=1-1110/h;s.render.border_max_y=1-750/h
    def capture(name):
        s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='32';s.render.filepath=str(out/(name+'.exr'))
        bpy.ops.render.render(write_still=True);im=bpy.data.images.load(s.render.filepath,check_existing=False)
        a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);a=a.reshape(h,w,4)[::-1].copy();np.save(out/(name+'.npy'),a)
        s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';im.save_render(str(out/(name+'.png')),scene=s);bpy.data.images.remove(im);return a
    for name in names:bpy.data.objects[name].data.energy=0
    fixed=capture('fixed')
    for group,members in groups.items():
        for name in members:bpy.data.objects[name].data.energy=powers[name]
        response=capture(group);np.save(out/(group+'-response.npy'),response-fixed)
        for name in members:bpy.data.objects[name].data.energy=0
    for name in names:bpy.data.objects[name].data.energy=powers[name]
    capture('all');assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    print('KING_BASE_RESPONSE_LAYERS_PASS',flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.source,a.output)
