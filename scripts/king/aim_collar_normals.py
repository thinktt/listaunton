"""Aim existing real collar reflectors using captured varnish normals."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run
from focused_reflections import target
from render_regions import clear_light_path
from validate_render_regions import check

def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
    capture=ROOT/cfg['capture'];manifest=json.loads((capture/'manifest.json').read_text(encoding='utf-8'));assert manifest['source_sha256']==digest
    position=np.load(capture/'position.npy');normals=np.load(capture/'coat-normal.npy');x0,y0,_,_=manifest['crop']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;check(s)
    for name,power in cfg.get('existing_light_power',{}).items():bpy.data.objects[name].data.energy=power
    view=(s.camera.matrix_world.to_3x3()@Vector((0,0,1))).normalized();report=[]
    for row in cfg['targets']:
        ob=bpy.data.objects[row['name']];assert ob.data.type=='AREA'
        x,y=row['pixel'];xx=x-x0;yy=y-y0;assert position[yy,xx,3]>.999
        point=Vector(position[yy,xx,:3]);local=[]
        for v in range(yy-1,yy+2):
            for u in range(xx-1,xx+2):
                if position[v,u,3]>.999 and np.linalg.norm(position[v,u,:3]-np.array(point))<.03:local.append(normals[v,u,:3])
        normal=Vector(np.mean(local,axis=0)).normalized();assert normal.dot(view)>.03
        direction=(2*normal.dot(view)*normal-view).normalized();distance=row['distance']
        hit,_,_,_=target(s,x,y);assert hit.get('king_render_region')==row['name'].split()[1]+'-collar'
        ob.location=point+distance*direction;ob.rotation_euler=(point-ob.location).to_track_quat('-Z','Y').to_euler()
        ob.data.size=row['size'];ob.data.size_y=row['size_y'];ob.data.energy=row['energy']
        if 'use_shadow' in row:ob.data.use_shadow=row['use_shadow']
        report.append(dict(row,position=list(point),actual_normal=list(normal),normal_samples=len(local),center_light_path_clear=clear_light_path(s,point,normal,direction,distance)))
    check(s);out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0;prepared=out/'aim-prepared.blend';bpy.ops.wm.save_as_mainfile(filepath=str(prepared))
    rc=dict(cfg,source=prepared.relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256(prepared.read_bytes()).hexdigest(),aim_original_source=cfg['source'],aim_original_source_sha256=digest,normal_targeting=report)
    run(rc);assert hashlib.sha256(source.read_bytes()).hexdigest()==digest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(a.config).read_text(encoding='utf-8-sig')))
