"""Extract the actual billet in rest space and its inherited atlas mapping."""
from pathlib import Path
import json,sys
import bpy,numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path[:0]=[str(D),str(R/'scripts/knight')]
from evidence import load
from lower_carving_fit import rest_coords
from mission_scene import sha
MANE='swept rounded mane'
def unpose(s,coordinates):
    p=json.loads(s['knight_mission_pose'])
    return rest_coords(coordinates,[p[k] for k in ['dx','dy','twist_degrees']])
def main():
    s=load('parent.blend');data={};g=bpy.context.evaluated_depsgraph_get()
    for src in s.objects:
        if src.type!='MESH' or src.hide_render:continue
        ob=src.evaluated_get(g);m=np.asarray(ob.matrix_world)
        me=ob.to_mesh();me.calc_loop_triangles()
        key=ob.name.removeprefix('Knight | ')
        inds=np.empty((len(me.loop_triangles),3),np.int32)
        me.loop_triangles.foreach_get('loops',inds.ravel())
        uv=np.empty((len(me.loops),2),np.float32);me.uv_layers['Knight wood atlas'].data.foreach_get('uv',uv.ravel())
        data[key]=uv[inds]
        if key==MANE:
            vertices=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',vertices.ravel())
            xyz=unpose(s,vertices@m[:3,:3].T+m[:3,3]);data['xyz']=xyz
            faces=np.empty_like(inds);me.loop_triangles.foreach_get('vertices',faces.ravel());data['tri']=faces
            print('XYZ',len(xyz),'faces',faces[:9], 'UV bounds',uv.min(0),uv.max(0))
            for i in [0,1000,3000,6500,11000]:
                print(i,np.round(xyz[i:i+7],3))
            print('First and last rings',np.round(xyz[:801:32],3),np.round(xyz[-50::10],3))
        ob.to_mesh_clear()
    np.savez_compressed(D/'surfaces.npz',**data)
if __name__=='__main__':main()
