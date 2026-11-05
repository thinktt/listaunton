"""Validate a deliberate cross-only shape revision without relaxing body checks."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy,bmesh,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(path):
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/path),load_ui=False);s=bpy.context.scene;objects={};bounds=[]
    for ob in s.objects:
        if ob.type!='MESH' or ob.hide_render:continue
        co=np.array([v.co[:] for v in ob.data.vertices],dtype='<f4');faces=[list(p.vertices) for p in ob.data.polygons]
        objects[ob.name]={'positions_sha256':hashlib.sha256(co.tobytes()).hexdigest(),'faces_sha256':hashlib.sha256(json.dumps(faces).encode()).hexdigest(),'matrix':list(v for row in ob.matrix_world for v in row),'modifiers':[(m.type,m.levels,m.render_levels) for m in ob.modifiers if m.type=='SUBSURF'],'vertices':len(co),'bounds':[co.min(0).tolist(),co.max(0).tolist()]}
        for modifier in ob.modifiers:
            if modifier.type=='SUBSURF':modifier.levels=modifier.render_levels
    bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get()
    for name,row in objects.items():
        ob=bpy.data.objects[name];ev=ob.evaluated_get(graph);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
        row['nonmanifold_edges']=sum(not e.is_manifold for e in bm.edges);row['volume']=bm.calc_volume(signed=True)
        assert row['nonmanifold_edges']==0 and row['volume']>0
        points=np.array([(ob.matrix_world@v.co)[:] for v in me.vertices],dtype='<f4');assert np.isfinite(points).all();bounds.append(points)
        if 'body' in name:
            row['evaluated_positions']=points
            row['atlas_uv']=np.array([v.uv[:] for v in me.uv_layers['Pigment atlas'].data],dtype='<f4')
        bm.free();ev.to_mesh_clear()
    points=np.concatenate(bounds);lo=points.min(0);hi=points.max(0);base=points[points[:,2]<lo[2]+.25*(hi[2]-lo[2])]
    cam=s.camera;axis=cam.matrix_world.to_3x3()@Vector((0,0,1));angle=math.degrees(math.asin(axis.z));assert abs(angle-54)<.001
    camera={'matrix':list(v for row in cam.matrix_world for v in row),'type':cam.data.type,'scale':cam.data.ortho_scale,'shift':[cam.data.shift_x,cam.data.shift_y],'resolution':[s.render.resolution_x,s.render.resolution_y],'elevation':angle}
    return {'objects':objects,'camera':camera,'height':float(hi[2]-lo[2]),'base_diameter':float(max(np.ptp(base[:,0]),np.ptp(base[:,1]))),'source_sha256':sha(ROOT/path)}
def main(args):
    before=read(args.before);after=read(args.after);assert set(before['objects'])==set(after['objects']);assert len(after['objects'])==2;assert before['camera']==after['camera']
    body=next(n for n in before['objects'] if 'body' in n);cross=next(n for n in before['objects'] if 'cross' in n)
    left=before['objects'][body];right=after['objects'][body]
    for key in ['positions_sha256','faces_sha256','matrix','modifiers','vertices','bounds']:assert left[key]==right[key],key
    position_error=float(abs(left.pop('evaluated_positions')-right.pop('evaluated_positions')).max());assert position_error<1e-6,position_error
    uv_error=float(abs(left.pop('atlas_uv')-right.pop('atlas_uv')).max());assert uv_error<1e-6,uv_error
    for key in ['height','base_diameter']:assert abs(before[key]-after[key])<1e-6,key
    assert before['objects'][cross]['positions_sha256']!=after['objects'][cross]['positions_sha256']
    report={'body_controls_topology_transform_subdivision_exact':True,'body_evaluated_position_max_error':position_error,'body_atlas_uv_max_error':uv_error,'camera_exact':True,'overall_height_and_base_diameter_preserved':True,'only_cross_geometry_deliberately_changed':True,'both_components_closed_positive_volume':True,'before_path':args.before,'after_path':args.after,'before':before,'after':after}
    out=ROOT/args.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print('KING_CROSS_CHECKPOINT_PASS',position_error,uv_error)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('output');main(p.parse_args(sys.argv[sys.argv.index('--')+1:]))
