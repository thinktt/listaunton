"""Capture existing base-light contributions without modifying the king source."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu

def main(args):
    source=ROOT/args.source;digest=hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
    out=ROOT/args.output;out.mkdir(parents=True,exist_ok=True)
    s.cycles.samples=96;s.cycles.use_denoising=True;s.render.use_persistent_data=True
    w,h=s.render.resolution_x,s.render.resolution_y
    s.render.use_border=True;s.render.use_crop_to_border=False;s.render.border_min_x=150/w;s.render.border_max_x=850/w;s.render.border_min_y=1-1120/h;s.render.border_max_y=1-520/h
    names=['Upper varnish','Front varnish','Platter front-right glint'];powers={name:bpy.data.objects[name].data.energy for name in names}
    def capture(label):
        s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='32'
        s.render.filepath=str(out/(label+'.exr'));bpy.ops.render.render(write_still=True)
        im=bpy.data.images.load(s.render.filepath,check_existing=False);a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);a=a.reshape(h,w,4)[::-1].copy();np.save(out/(label+'.npy'),a)
        s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';im.save_render(str(out/(label+'.png')),scene=s);bpy.data.images.remove(im)
        return a
    for name in names:bpy.data.objects[name].data.energy=0
    fixed=capture('fixed');rows=[]
    for index,name in enumerate(names):
        ob=bpy.data.objects[name];ob.data.energy=powers[name];a=capture('light-'+str(index));np.save(out/('response-'+str(index)+'.npy'),a-fixed);ob.data.energy=0
        rows.append({'name':name,'energy':powers[name],'type':ob.data.type,'position':list(ob.location),'size':getattr(ob.data,'size',None),'size_y':getattr(ob.data,'size_y',None),'shape':getattr(ob.data,'shape',None),'receiver_collection':ob.light_linking.receiver_collection.name if ob.light_linking.receiver_collection else None})
    report={'source':args.source,'source_sha256':digest,'lights':rows,'scope':'Actual linear Cycles base responses with fixed diffuse/world and cross lighting. Diagnostic only; no saved-source mutation.'}
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');assert hashlib.sha256(source.read_bytes()).hexdigest()==digest;print('KING_BASE_LIGHT_RESPONSES',json.dumps(report))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');main(p.parse_args(sys.argv[sys.argv.index('--')+1:]))
