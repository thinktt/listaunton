"""Add controlled real glossy spotlights at reference glints; keep the BSDF."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run

def target(scene,x,y):
    graph=bpy.context.evaluated_depsgraph_get();cam=scene.camera
    w,h=scene.render.resolution_x,scene.render.resolution_y
    projection=cam.calc_matrix_camera(graph,x=w,y=h)
    p=projection.inverted()@Vector((2*x/w-1,1-2*y/h,-1,1));origin=cam.matrix_world@(p.xyz/p.w)
    view=(cam.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
    hit,point,normal,fi,ob,_=scene.ray_cast(graph,origin,-view);assert hit,(x,y)
    ev=ob.evaluated_get(graph);mesh=ev.to_mesh();mesh.calc_loop_triangles();found=False
    for tri in mesh.loop_triangles:
        if tri.polygon_index!=fi:continue
        a,b,c=[ob.matrix_world@mesh.vertices[i].co for i in tri.vertices];ab=b-a;ac=c-a;ap=point-a
        aa=ab.dot(ab);bb=ab.dot(ac);cc=ac.dot(ac);dd=ap.dot(ab);ee=ap.dot(ac);den=aa*cc-bb*bb
        if abs(den)<1e-18:continue
        v=(cc*dd-bb*ee)/den;z=(aa*ee-bb*dd)/den;u=1-v-z
        if min(u,v,z)<-.001:continue
        normal=sum((mesh.corner_normals[li].vector*weight for li,weight in zip(tri.loops,[u,v,z])),Vector())
        normal=(ob.matrix_world.to_3x3().inverted().transposed()@normal).normalized();found=True;break
    ev.to_mesh_clear();assert found
    return ob,point,(2*normal.dot(view)*normal-view).normalized(),normal

def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    probes=[]
    for row in cfg['reflectors']:
        ob,point,direction,normal=target(s,*row['pixel']);position=point+direction*row.get('distance',6)
        data=bpy.data.lights.new(row['name'],'SPOT');data.energy=row['energy'];data.color=row.get('color',[1,.76,.56])
        data.shadow_soft_size=row.get('radius',.06);data.spot_size=math.radians(row.get('degrees',4));data.spot_blend=.9
        light=bpy.data.objects.new(row['name'],data);s.collection.objects.link(light);light.location=position;light.rotation_euler=(point-position).to_track_quat('-Z','Y').to_euler()
        light.visible_diffuse=False;light.visible_glossy=True
        receivers=bpy.data.collections.new(row['name']+' receiver');receivers.objects.link(ob);light.light_linking.receiver_collection=receivers
        probes.append(dict(row,point=list(point),normal=list(normal),position=list(position),receiver=ob.name,diffuse=False,glossy=True))
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(exist_ok=True,parents=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rendercfg={k:v for k,v in cfg.items() if k!='source_sha256'};rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),original_source=cfg['source'],original_source_sha256=digest,reflector_probes=probes)
    run(rendercfg)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(args.config).read_text(encoding='utf-8')))
