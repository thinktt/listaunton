"""Round the cross's upper cap without changing body, camera or overall height."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,bmesh,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run,meshes

def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    cross=next(o for o in meshes(s) if 'cross' in o.name);body=next(o for o in meshes(s) if 'body' in o.name)
    original_body=np.array([v.co[:] for v in body.data.vertices],dtype='<f4').tobytes()
    old_top=max(v.co.z for v in cross.data.vertices)
    for ob in bpy.context.selected_objects:ob.select_set(False)
    cross.select_set(True);bpy.context.view_layer.objects.active=cross
    for modifier in list(cross.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm=bmesh.new();bm.from_mesh(cross.data)
    edges=[e for e in bm.edges if abs((e.verts[1].co-e.verts[0].co).x)>.05 and abs((e.verts[1].co-e.verts[0].co).normalized().x)>.95]
    bmesh.ops.subdivide_edges(bm,edges=edges,cuts=cfg.get('cuts',12),use_grid_fill=True)
    top=max(v.co.z for v in bm.verts);front=min(v.co.y for v in bm.verts);back=max(v.co.y for v in bm.verts);stem=.157142857
    def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
    changed=0
    for v in bm.verts:
        weight=smooth((v.co.z-(top-.20))/.20)
        facing=smooth(-v.co.y/abs(front))
        arc=min(1,(v.co.x/stem)**2)
        drop=(facing*(cfg['center_drop']+cfg['edge_drop']*arc)+(1-facing)*cfg.get('back_edge_drop',0)*arc)*weight
        if drop>1e-10:v.co.z-=drop;changed+=1
    bm.normal_update()
    if cfg.get('smooth_cap',True):
        for face in bm.faces:
            if min(v.co.z for v in face.verts)>top-.22 and face.normal.z>.2:face.smooth=True
    if cfg.get('smooth_edges',False):
        for face in bm.faces:
            if abs(face.normal.y)<.999 and len(face.verts)<=4:face.smooth=True
    assert all(e.is_manifold for e in bm.edges)
    volume=bm.calc_volume(signed=True);assert volume>0
    bm.to_mesh(cross.data);bm.free();cross.data.update()
    assert np.array([v.co[:] for v in body.data.vertices],dtype='<f4').tobytes()==original_body
    assert abs(max(v.co.z for v in cross.data.vertices)-old_top)<1e-6
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rendercfg={k:v for k,v in cfg.items() if k!='source_sha256'};rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),original_source=cfg['source'],original_source_sha256=digest,changed_cross_vertices=changed,cross_volume=volume,body_controls_unchanged=True,overall_height_unchanged=True)
    run(rendercfg)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(a.config).read_text(encoding='utf-8')))
