"""Native transverse ray sections through both physical flanks."""
from pathlib import Path
import json,sys
import bpy,numpy as np
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent; R=D.parents[2]
sys.path[:0]=[str(D),str(R/'scripts/knight')]
from mission_scene import world_vertices,sha
from lower_carving_fit import rest_coords
from mission_pose import posed

MANE='swept rounded mane'
HEAD='continuous horse head and neck'
BUILD='coherent skull cheek and conical muzzle'
NECK='curved neck and chest'

def pose(scene):
    q=json.loads(scene['knight_mission_pose'])
    return [q[k] for k in ['dx','dy','twist_degrees']]

def tree(s,name):
    ob=s.objects['Knight | '+name].evaluated_get(bpy.context.evaluated_depsgraph_get())
    me=ob.to_mesh();m=np.array(ob.matrix_world)
    v=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',v.ravel())
    v=rest_coords(v@m[:3,:3].T+m[:3,3],pose(s))
    me.calc_loop_triangles();f=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('vertices',f.ravel())
    tr=BVHTree.FromPolygons(v.tolist(),f.tolist(),all_triangles=True)
    ob.to_mesh_clear();return tr

def sample(s):
    xs=np.arange(-2.03,.415,.008)
    zs=np.arange(1.68,4.86,.025)
    fields=np.full((2,2,len(zs),len(xs)),np.nan,np.float32)
    for i,n in enumerate([MANE,HEAD]):
        tr=tree(s,n)
        for si,sg in enumerate([-1,1]):
            for j,z in enumerate(zs):
                for k,x in enumerate(xs):
                    v=tr.ray_cast((x,sg*3,z),(0,-sg,0))[0]
                    if v is not None:fields[i,si,j,k]=sg*v.y
    return xs,zs,fields

def describe(xs,zs,fields):
    print('z, bounds, exposed intersection, pre-pose widths near/far at old join and at target')
    for z in [1.98,2.28,2.56,2.80,3.02,3.22,3.45,3.61,3.82,4.02,4.23,4.40,4.58,4.73]:
        j=np.argmin(abs(zs-z))
        own=np.nan_to_num(fields[0,0,j],nan=-10)>np.nan_to_num(fields[1,0,j],nan=-10)
        ranges=[]
        for ind in np.where(own&~np.r_[False,own[:-1]])[0]:
            last=ind
            while last+1<len(own) and own[last+1]:last+=1
            ranges.append([round(xs[ind],3),round(xs[last],3)])
        sub=lambda x:np.round(fields[:,:,j,np.argmin(abs(xs-x))],3).tolist()
        print(round(zs[j],3),ranges,sub(-.94),sub(-.64))

if __name__=='__main__':
    name=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'parent'
    bpy.ops.wm.open_mainfile(filepath=str(D/(name+'.blend')),load_ui=False)
    s=bpy.context.scene
    x,z,q=sample(s);np.savez_compressed(D/f'{name}-sections.npz',x=x,z=z,sides=q)
    describe(x,z,q)
