"""Visual and geometric inspection of the final, shortened dome and its physical bevel."""
from pathlib import Path
import sys,json
import bpy,numpy as np
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D))
from carve import sculpt,DESIGNS,load,flat,border
from poll_card import meter,fitted
from dimensions import height
from diagnostics import camera
from mission_scene import configure_render,render,use_side_camera

def self_cross(scene):
    obj=scene.objects['Knight | swept rounded mane'].evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=obj.to_mesh()
    mesh.calc_loop_triangles()
    tris=np.empty((len(mesh.loop_triangles),3),np.int32)
    mesh.loop_triangles.foreach_get('vertices',tris.ravel())
    pts=np.empty((len(mesh.vertices),3),np.float32)
    mesh.vertices.foreach_get('co',pts.ravel())
    tree=BVHTree.FromPolygons(pts.tolist(),tris.tolist(),all_triangles=True)
    overlaps=tree.overlap(tree)
    cross=[(a,b) for a,b in overlaps if a<b and not np.any(tris[a][:,None]==tris[b])]
    if cross:
        pts_cross=np.array([(pts[tris[a]].mean(0)+pts[tris[b]].mean(0))*.5 for a,b in cross])
        print('NATIVE_CROSS_BOUNDS',pts_cross.min(0),pts_cross.max(0),flush=True)
    obj.to_mesh_clear()
    return len(cross)
def test():
    idx=int(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else 16
    s=load('parent.blend')
    base=height(s)
    old_cross=self_cross(s)
    sculpt(s,DESIGNS[idx])
    q=height(s);new_cross=self_cross(s)
    data={'parent':base,'candidate':q,'nonadjacent_mane_triangle_intersections':[old_cross,new_cross]}
    print('DIMENSIONS',data,flush=True)
    (D/f'preflight-{idx}.json').write_text(json.dumps(data,indent=2)+'\n')
    fitted(s,meter(s),0.,105. if idx>=20 else 62.,.105)
    configure_render(s,72);border(s,(245,281,524,434))
    render(s,D/f'trial-{idx}-crest.png')
    flat(s);render(s,D/f'trial-{idx}-clay-crest.png')
    use_side_camera(s);border(s,(220,92,819,410));s.render.resolution_percentage=70
    render(s,D/f'trial-{idx}-clay-side.png')
    s.render.use_border=s.render.use_crop_to_border=False
    s.render.resolution_x=s.render.resolution_y=600;s.render.resolution_percentage=100
    yaw=json.loads(s['knight_mission_pose'])['twist_degrees']
    for az,name in [(180,'opposite'),(270,'rear'),(90,'front')]:
        camera(s,yaw+az,12)
        render(s,D/(f'trial-{idx}-clay-'+name+'.png'))
if __name__=='__main__':
    if '--check' in sys.argv:
        for value in sys.argv[sys.argv.index('--check')+1:]:
            i=int(value)
            scene=load('parent.blend')
            sculpt(scene,DESIGNS[i])
            print('OVERLAPS',value,self_cross(scene),flush=True)
    else:test()
