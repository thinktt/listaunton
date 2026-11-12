"""Read-only reflection visibility and response images for the king collars."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from focused_reflections import target
from render_regions import clear_light_path

def main(directory):
    out=ROOT/directory;source=out/'king.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    fit=json.loads((out/'fit.json').read_text(encoding='utf-8'))
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
    rows=[]
    for i,name in enumerate(fit['original_powers']):
        im=bpy.data.images.load(str(out/('response-%02d.exr'%i)),check_existing=False)
        w,h=im.size;a=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[::-1]
        lum=a[:,:,:3]@np.array([.2126,.7152,.0722]);y,x=np.unravel_index(lum.argmax(),lum.shape)
        im.save_render(str(out/('response-%02d.png'%i)),scene=s);bpy.data.images.remove(im)
        rows.append(dict(light=name,maximum_linear_luminance=float(lum.max()),max_pixel=[int(x),int(y)],fitted_power=fit['fitted_powers'][name]))
    probes=[]
    for pixel in [[470,423],[555,428],[445,491],[445,486],[450,487],[580,477],[450,517],[566,531]]:
        ob,p,d,n=target(s,*pixel)
        probes.append(dict(pixel=pixel,receiver=ob.get('king_render_region'),normal=list(n),reflection=list(d),
            clear_distance={str(length):clear_light_path(s,p,n,d,length) for length in [.03,.05,.08,.12,.2,.4,.8,1.6]}))
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    (out/'response-diagnostic.json').write_text(json.dumps(dict(source_sha256=digest,source_unchanged=True,responses=rows,probes=probes),indent=2)+'\n',encoding='utf-8')
    print('KING_COLLAR_RESPONSES_INSPECTED')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.directory)
