"""Measure local surface orientation and geometric shelter in the reference hollow."""
import hashlib,json,math,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root,model,trace,out=map(lambda v:Path(v).resolve(),sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(root/'scripts/knight'))
from probe_carving import point_probe
from mission_scene import visible_meshes
source=hashlib.sha256(model.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);s=bpy.context.scene
graph=bpy.context.evaluated_depsgraph_get();vertices=[];triangles=[]
for obj in visible_meshes(s):
    ev=obj.evaluated_get(graph);m=ev.to_mesh()
    try:
        xyz=np.empty((len(m.vertices),3),np.float32);m.vertices.foreach_get('co',xyz.ravel())
        mat=np.asarray(ev.matrix_world);xyz=xyz@mat[:3,:3].T+mat[:3,3]
        m.calc_loop_triangles();indices=np.empty((len(m.loop_triangles),3),np.int32);m.loop_triangles.foreach_get('vertices',indices.ravel())
        triangles.extend((indices+len(vertices)).tolist());vertices.extend(xyz.tolist())
    finally:ev.to_mesh_clear()
tree=BVHTree.FromPolygons(vertices,triangles,all_triangles=True)
probe=point_probe(s)
trace_data=json.loads(trace.read_bytes())
rows={y:x for y,x,*_ in trace_data['Black 2']['samples']}
# Cosine-weighted directions on the outward hemisphere. A rotation per row avoids alignment with the mesh grid.
N=192;golden=math.pi*(3-math.sqrt(5));rows_result=[]
for iy,y in enumerate([460,484,508,532,556,580,604,628]):
    sample={}
    for label,offset in [('mane',-19),('cut',0),('neck',29)]:
        x=rows[y]+offset;hit=probe(x+.5,y+.5)
        if hit is None:continue
        _,part,pos,norm=hit;norm.normalize()
        basis=norm.cross(Vector((0,0,1)) if abs(norm.z)<.90 else Vector((0,1,0))).normalized()
        other=norm.cross(basis);start=pos+.0005*norm
        lengths=[]
        for k in range(N):
            radius=math.sqrt((k+.5)/N);theta=golden*k+iy*.31
            ray=(math.sqrt(1-radius**2)*norm+radius*(math.cos(theta)*basis+math.sin(theta)*other)).normalized()
            _,_,_,dist=tree.ray_cast(start,ray,2.0)
            lengths.append(dist if dist is not None else 3.)
        metrics={}
        for name in ['Walnut key','Walnut soft fill','Walnut upper strip']:
            lamp=s.objects.get(name)
            if lamp is None:continue
            direction=lamp.matrix_world.translation-start;length=direction.length;direction.normalize()
            obstruction=tree.ray_cast(start,direction,length-.001)[0]
            metrics[name]={'dot_surface_to_center':round(float(norm.dot(direction)),4),'center_visible':obstruction is None}
        sample[label]={'x':x,'object':part,'hemisphere_blocked_by_radius':{str(rad):round(float(np.mean(np.array(lengths)<rad)),3) for rad in (.15,.55,1.5)},
                       'geometric_light_directions':metrics}
    rows_result.append({'y':y,'samples':sample})
assert source==hashlib.sha256(model.read_bytes()).hexdigest()
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({'model':source,'samples':rows_result,'method':'192 cosine-weighted rays inside an outward native triangle hemisphere on three registered traces. Reports proportion blocked by the actual visible meshes within three distances. Diagnostic lamp dots and center visibility do not include full area integration, light linking, material or bounce light.'},indent=2)+'\n')
for label in ['mane','cut','neck']:
    vals=[row['samples'][label]['hemisphere_blocked_by_radius']['0.55'] for row in rows_result if 480<=row['y']<=604 and label in row['samples']]
    print(label,'median nearby blocked fraction',round(float(np.median(vals)),3))
