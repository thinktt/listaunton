"""Fit bounded RGB power changes to existing lamps using actual Cycles responses."""
import argparse,json,math,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,BUILD,render,save_json,sha
from polish_trial import open_source,save_trial
from refine_stem_reflector import read_rgb

def install(scene,rows):
    for row in rows:
        ob=scene.objects[row['name']]
        assert ob.type=='LIGHT' and not ob.visible_diffuse and ob.visible_glossy
        ob.data.energy=row['energy'];ob.data.color=row['color']

def run(cfg):
    scene,body=open_source(cfg);out=BUILD/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    if cfg.get('fitted_lights'):
        install(scene,cfg['fitted_lights']);save_trial(scene,cfg);return
    lamps=[scene.objects[name] for name in cfg['lights']]
    assert all(o.type=='LIGHT' and not o.visible_diffuse and o.visible_glossy for o in lamps)
    old=[{'name':o.name,'energy':o.data.energy,'color':list(o.data.color)} for o in lamps]
    def apply(p):
        rows=[]
        for i,row in enumerate(old):
            color=np.array(row['color'])*np.exp(p[3*i:3*i+3]);gain=float(color.max())
            rows.append({'name':row['name'],'energy':row['energy']*gain,'color':(color/gain).tolist()})
        install(scene,rows);return rows
    x0,y0,x1,y1=cfg['crop'];roi=np.s_[y0:y1,x0:x1]
    scene.render.use_border=True;scene.render.use_crop_to_border=False
    scene.render.border_min_x=x0/1254;scene.render.border_max_x=x1/1254
    scene.render.border_min_y=1-y1/1254;scene.render.border_max_y=1-y0/1254
    target=read_rgb(ROOT/'assets/pawn/reference.png')[roi]
    weights=np.ones(target.shape[:2],float)
    for row in cfg.get('regions',[]):
        a,b,c,d=row['box'];weights[max(0,b-y0):min(y1-y0,d-y0),max(0,a-x0):min(x1-x0,c-x0)]=row['weight']
    def response(name,p):
        apply(p);path=out/(name+'.png');render(scene,path);im=read_rgb(path)[roi]
        return im,{'parameters':p.tolist(),'loss':float(np.mean(weights[:,:,None]*(im-target)**2)),'sha256':sha(path)}
    count=3*len(lamps);p=np.zeros(count);base,record=response('baseline-crop',p);records={'baseline':record}
    columns=[];step=cfg.get('step',.18)
    for i in range(count):
        q=p.copy();q[i]=step;im,record=response('response-'+str(i),q);records['response-'+str(i)]=record
        columns.append(((im-base)/step).reshape(-1))
    J=np.column_stack(columns).astype(float);w=np.repeat(weights.ravel(),3);rhs=(target-base).reshape(-1)
    limit=cfg.get('limit',.45);G=J.T@(w[:,None]*J)+np.eye(count)*cfg.get('ridge',.003)/(limit**2);v=J.T@(w*rhs)
    q=np.zeros(count)
    for _ in range(160):
        prev=q.copy()
        for i in range(count):q[i]=np.clip(q[i]+(v[i]-G[i]@q)/max(G[i,i],1e-10),-limit,limit)
        if abs(q-prev).max()<1e-5:break
    best=p.copy();best_loss=records['baseline']['loss']
    for rate in cfg.get('rates',[.5,1.]):
        _,record=response('step-'+str(rate),q*rate);records['step-'+str(rate)]=record
        if record['loss']<best_loss:best=q*rate;best_loss=record['loss']
    rows=apply(best);report={'config':cfg,'before':old,'after':rows,'proposed':q.tolist(),'selected':best.tolist(),'records':records,
        'method':'Actual rendered per-channel power derivatives; bounded log-gain and independent full-image evaluation. Only existing lamp color/energy changes.'}
    save_json(out/'fit.json',report)
    replay={**cfg,'fitted_lights':rows};save_json(out/'reproduction.json',replay)
    scene['pawn_lamp_color_fit']=json.dumps(report,sort_keys=True)
    scene.render.use_border=False;scene.render.use_crop_to_border=False
    save_trial(scene,cfg)
    print('COLOR_FIT',json.dumps({'baseline':records['baseline']['loss'],'selected':best_loss,'lights':rows}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    run(json.loads(a.config.read_text(encoding='utf8')))
