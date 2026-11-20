"""Fit one existing real reflector using measured local Cycles derivatives."""
import argparse,json,math,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source,save_trial
from mission_render import ROOT,BUILD,Surface,render,save_json,sha
from fit_lighting import shape

def read_rgb(path):
    im=bpy.data.images.load(str(path),check_existing=False)
    im.colorspace_settings.name='Non-Color'
    a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a)
    w,h=im.size;bpy.data.images.remove(im)
    return a.reshape(h,w,4)[::-1,:,:3].copy()

def run(cfg):
    scene,body=open_source(cfg);out=BUILD/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    ob=scene.objects[cfg['light']];d=ob.data
    assert ob.type=='LIGHT' and d.type=='AREA' and not ob.visible_diffuse
    old={'position':list(ob.location),'rotation':list(ob.rotation_euler),'size':d.size,'size_y':d.size_y,'energy':d.energy,'color':list(d.color),'spread':d.spread,'normalize':d.normalize}
    surface=Surface(scene,body);spec=cfg['landmark'];x,y=spec['pixel']
    derivatives=[]
    for dx,dy in [(1,0),(0,1)]:
        up=shape(surface,{**spec,'pixel':[x+dx,y+dy]})
        down=shape(surface,{**spec,'pixel':[x-dx,y-dy]})
        derivatives.append((np.array(up['position'])-np.array(down['position']))/2)
    rotation=ob.rotation_euler.to_quaternion();local_axis=Vector((0,0,1))
    def apply(p):
        from mathutils import Quaternion
        ob.location=np.asarray(old['position'])+p[0]*derivatives[0]+p[1]*derivatives[1]
        ob.rotation_euler=(rotation@Quaternion(local_axis,float(p[5]))).to_euler()
        d.size=old['size']*math.exp(p[2]);d.size_y=old['size_y']*math.exp(p[3]);d.energy=old['energy']*math.exp(p[4])
    x0,y0,x1,y1=cfg['crop'];roi=np.s_[y0:y1,x0:x1]
    scene.render.use_border=True;scene.render.use_crop_to_border=False
    scene.render.border_min_x=x0/1254;scene.render.border_max_x=x1/1254
    scene.render.border_min_y=1-y1/1254;scene.render.border_max_y=1-y0/1254
    target=read_rgb(ROOT/'assets/pawn/reference.png')[roi]
    weight=1+cfg.get('bright_weight',2)*np.clip((target.min(2)-.2)/.55,0,1)
    def response(name,p):
        apply(p);path=out/(name+'.png');render(scene,path)
        im=read_rgb(path)[roi];loss=float(np.mean(weight[:,:,None]*(im-target)**2))
        return im,{'parameters':np.asarray(p).tolist(),'loss':loss,'sha256':sha(path)}
    p=np.zeros(6);base,base_record=response('baseline-crop',p);records={'baseline':base_record}
    steps=np.array(cfg['steps']);columns=[]
    for i,step in enumerate(steps):
        q=p.copy();q[i]=step
        up,record=response('response-'+str(i),q);records['response-'+str(i)]=record
        columns.append(((up-base)/step).reshape(-1))
    J=np.column_stack(columns).astype(float);w=np.repeat(weight.ravel(),3)
    rhs=(target-base).reshape(-1).astype(float)
    G=J.T@(w[:,None]*J);v=J.T@(w*rhs)
    limits=np.array(cfg['limits']);G+=np.diag(cfg.get('ridge',.001)/limits**2)
    q=np.zeros(6)
    for _ in range(160):
        previous=q.copy()
        for i in range(6):q[i]=np.clip(q[i]+(v[i]-G[i]@q)/max(G[i,i],1e-10),-limits[i],limits[i])
        if abs(q-previous).max()<1e-5:break
    best=p.copy();best_loss=base_record['loss']
    for rate in cfg.get('rates',[.4,.7,1.]):
        name='step-'+str(rate);_,record=response(name,q*rate);records[name]=record
        if record['loss']<best_loss:best=q*rate;best_loss=record['loss']
    apply(best)
    after={'position':list(ob.location),'rotation':list(ob.rotation_euler),'size':d.size,'size_y':d.size_y,'energy':d.energy,'color':list(d.color),'spread':d.spread,'normalize':d.normalize}
    report={'config':cfg,'before':old,'after':after,'position_derivatives':[x.tolist() for x in derivatives],
            'parameter_names':['aim_x_pixels','aim_y_pixels','log_major','log_minor','log_energy','in_plane_angle_radians'],
            'proposed':q.tolist(),'selected':best.tolist(),'records':records,
            'note':'Only local fit selection; full images and originals must be judged independently before acceptance.'}
    save_json(out/'fit.json',report)
    scene['pawn_stem_reflector_fit']=json.dumps(report,sort_keys=True)
    scene.render.use_border=False;scene.render.use_crop_to_border=False
    save_trial(scene,cfg)
    print('REFLECTOR_FIT',json.dumps({'baseline':base_record['loss'],'selected':best_loss,'parameters':best.tolist()}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    run(json.loads(a.config.read_text(encoding='utf8')))
