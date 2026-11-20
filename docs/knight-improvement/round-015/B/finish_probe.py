"""Inspect native corner finish and the change of facing under a light bank."""
import sys,json
from pathlib import Path
import bpy,numpy as np
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import load,sculpt,DESIGNS
from lamp_probe import measure
from probe_carving import point_probe
def inspect(key):
    s=load('parent.blend' if key.isdigit() or key=='parent' else 'knight.blend')
    if key.isdigit():sculpt(s,DESIGNS[int(key)])
    q=measure(s);r=point_probe(s);dg=bpy.context.evaluated_depsgraph_get()
    for sample in q.values():
        x,y=sample['xy'];hit=r(x+.5,y+.5);o=s.objects[hit[1]]
        local=o.matrix_world.inverted()@hit[2];tree=BVHTree.FromObject(o,dg)
        face=tree.find_nearest(local)[2];obj=o.evaluated_get(dg);me=obj.data
        values=me.attributes['Knight varnish coverage'].data;ids=me.polygons[face].vertices
        sample['varnish']=round(float(np.mean([values[i].value for i in ids])),4)
        normal=hit[3];view=s.camera.matrix_world.to_quaternion()@__import__('mathutils').Vector((0,0,1))
        spec=2*normal.dot(view)*normal-view
        sample['banks']={}
        for lamp in [o for o in s.objects if o.type=='LIGHT' and not o.hide_render]:
            delta=lamp.matrix_world.translation-hit[2];dist=delta.length;delta.normalize()
            occ=s.ray_cast(dg,hit[2]+normal*.00012,delta,distance=dist)[4]
            angle=np.degrees(np.arccos(np.clip(spec.dot(delta),-1,1)))
            sample['banks'][lamp.name]=[round(float(angle),2),occ.name if occ else None]
    (D/f'finish-{key}.json').write_text(json.dumps(q,indent=2)+'\n')
    print(key,[(i['xy'],i['varnish'],i['banks']['Eye reflection upper']) for i in q.values()])
    if key=='parent':
        mat=s.objects['Knight | near eye'].active_material
        print(mat.name,[(n.name,n.type) for n in mat.node_tree.nodes])
if __name__=='__main__':
    for k in sys.argv[sys.argv.index('--')+1:]:inspect(k)
