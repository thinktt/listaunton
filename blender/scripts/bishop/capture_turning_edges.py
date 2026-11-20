"""Locate actual collar surfaces behind outline pixels and front rim extents."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy,numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',default='models/bishop/bishop-rebuilt.blend');p.add_argument('--profile',default='scripts/bishop/profile.json')
p.add_argument('--out',default='build/bishop-mission/144-surface-audit/turning-edges.json')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/a.source;digest=hashlib.sha256(source.read_bytes()).hexdigest()
cfg=json.loads((ROOT/a.profile).read_text());al=json.loads((ROOT/'assets/bishop/original-alignment.json').read_text())
factor=1254/300/al['scale']/cfg['scale'];co=math.cos(math.radians(54))
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);scene=bpy.context.scene;bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get();body=bpy.data.objects['Bishop - continuous turned body'].evaluated_get(deps)
assert body.matrix_world==bpy.data.objects['Bishop - continuous turned body'].matrix_world
assert scene.camera.data.type=='ORTHO'
camera=scene.camera;direction=camera.matrix_world.to_3x3()@Vector((0,0,-1))
elevation=math.degrees(math.asin(-direction.normalized().z));assert abs(elevation-54)<1e-4
projection=camera.calc_matrix_camera(deps,x=1254,y=1254)
inverse=(projection@camera.matrix_world.inverted()).inverted()
body_inverse=body.matrix_world.inverted()
def cast(x,y):
    p0=inverse@Vector((2*(x+.5)/1254-1,1-2*(y+.5)/1254,-1,1))
    p1=inverse@Vector((2*(x+.5)/1254-1,1-2*(y+.5)/1254,1,1))
    start=body_inverse@(p0.xyz/p0.w);end=body_inverse@(p1.xyz/p1.w)
    return body.ray_cast(start,(end-start).normalized())
outline=[]
for y in range(372,411,2):
    for x in range(320,420):
        hit,point,normal,face=cast(x,y)
        if hit:
            axis_y=cfg['y0']-point.z*co/factor
            nearest=min(range(len(cfg['profile'])),key=lambda i:abs(cfg['profile'][i][1]-axis_y))
            outline.append({'pixel':[x,y],'axis_y':axis_y,'nearest_control_ring':nearest,'world':list(body.matrix_world@point)})
            break
bands={'upper_collar':[59,64],'middle_collar':[50,56],'lower_collar':[42,48],'socket_lip':[27,30]}
report={}
for name,(first,last) in bands.items():
    ys=[cfg['profile'][i][1] for i in range(first,last+1)];points=[]
    for yy in np.linspace(min(ys),max(ys),401):
        z=(cfg['y0']-yy)*factor/co
        hit,pos,normal,face=body.ray_cast(Vector((0,-4,z)),Vector((0,1,0)))
        assert hit
        pixel=world_to_camera_view(scene,camera,body.matrix_world@pos)
        points.append({'axis_y':float(yy),'radius':float(-pos.y),'x':float(pixel.x*1254),'y':float((1-pixel.y)*1254)})
    report[name]={'control_band':[first,last],'front_band_lowest_projected_point':max(points,key=lambda p:p['y']),
        'largest_radius_point':max(points,key=lambda p:p['radius'])}
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True)
record={'source':a.source,'source_sha256':digest,'camera_degrees_measured':elevation,'outline_surface_samples':outline,'front_bands':report,
    'note':'Actual evaluated surface rays, no shading. Band extents locate geometric surfaces; photographic glints and shadow troughs are not assumed to be these exact points.'}
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
