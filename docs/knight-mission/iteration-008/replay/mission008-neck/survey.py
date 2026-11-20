"""Recover the neck, platform and mane cross sections from the actual saved scene."""
from pathlib import Path
import sys,json
import bpy,numpy as np
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;ROOT=D.parents[2];sys.path[:0]=[str(D),str(ROOT/'scripts/knight')]
from mission_scene import world_vertices
from mission_pose import posed
from lower_carving_fit import rest_coords
HEAD='Knight | continuous horse head and neck';HIDDEN='Knight | curved neck and chest';BASE='Knight | turned pedestal';MANE='Knight | swept rounded mane'
def pose(s):
    a=json.loads(s['knight_mission_pose']);return [a[k] for k in ('dx','dy','twist_degrees')]
def ease(q):
    a=np.clip(q,0,1);return a*a*(3-2*a)
def foot(s,z):return float(s.get('knight_foot_center_x',0))*ease((2.48-z)/.72)
def rest(s,world):
    a=world.copy();a[:,0]-=foot(s,a[:,2]);return rest_coords(a,pose(s))
def world(s,a):
    q=posed(a,*pose(s));q[:,0]+=foot(s,q[:,2]);return q
def mesh(s,name,unpose=True):
    o=s.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());m=o.data;m.calc_loop_triangles()
    w=world_vertices(o);v=rest(s,w) if unpose else w
    f=np.empty((len(m.loop_triangles),3),np.int32);m.loop_triangles.foreach_get('vertices',f.ravel())
    return v,f
def slices(v,f,z):
    fs=v[f];a=fs.reshape(-1,3);b=np.roll(fs,-1,axis=1).reshape(-1,3)
    use=(a[:,2]>z)!=(b[:,2]>z);a=a[use];b=b[use]
    return a+(b-a)*((z-a[:,2])/(b[:,2]-a[:,2]))[:,None]
def run(s,key):
    zs=np.r_[np.linspace(1.44,1.94,26),np.linspace(1.98,3.63,34),3.75];angles=np.linspace(-np.pi,np.pi,361)
    results={};summary={};meta={}
    for name in [BASE,MANE,HEAD,HIDDEN]:
        o=s.objects[name];v,f=mesh(s,name);native=rest(s,world_vertices(o));meta[name]={'n':len(native),'z_range':[float(native[:,2].min()),float(native[:,2].max())],
            'faces':len(f),'mods':[m.name for m in o.modifiers],'part_object_matrix':np.array(o.matrix_world).tolist()}
        if name==BASE:
            print('PLATFORM TOP',np.unique(np.round(v[v[:,2]>1.45,2],4),return_counts=True))
            for z in np.unique(np.round(v[v[:,2]>1.5,2],4)):
                vs=v[np.round(v[:,2],4)==z];r=np.hypot(vs[:,0],vs[:,1]);print('RING',z,r.min(),r.max())
        tree=BVHTree.FromPolygons(v.tolist(),f.tolist(),all_triangles=True);radii=[];rows=[]
        for z in zs:
            cross=slices(v,f,z);mid=np.array([0.,0.]) if name==BASE or not len(cross) else (cross[:,:2].min(0)+cross[:,:2].max(0))/2
            r=[]
            for a in angles:
                u=np.array([np.cos(a),np.sin(a)]);start=np.r_[mid+u*3,z];hit=tree.ray_cast(start,np.r_[-u,0],6)[0]
                r.append(float(np.dot(np.asarray(hit)[:2]-mid,u)) if hit else np.nan)
            radii.append(r)
            rows.append([float(z),*mid.tolist(),*[float(i) for i in ([*cross[:,:2].min(0),*cross[:,:2].max(0)] if len(cross) else [np.nan]*4)]])
        results[name+'r']=np.array(radii);results[name+'info']=np.array(rows);summary[name]=np.array(rows)[::4].round(4).tolist()
    np.savez_compressed(D/f'sections-{key}.npz',z=zs,angles=angles,**results)
    (D/f'section-summary-{key}.json').write_text(json.dumps({'native':meta,'sample':summary},indent=2)+'\n')
if __name__=='__main__':
    key=sys.argv[-1];bpy.ops.wm.open_mainfile(filepath=str(D/f'{key}.blend'),load_ui=False);run(bpy.context.scene,key)
