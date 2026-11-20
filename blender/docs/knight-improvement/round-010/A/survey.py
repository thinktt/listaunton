"""Survey the visible crown, the protected ear tips and the paired ring cages."""
from pathlib import Path
import json,sys
import bpy
import numpy as np
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from mission_scene import world_vertices,sha
from lower_carving_fit import rest_coords
from probe_carving import point_probe,rest
def main():
    tag='candidate' if '--candidate' in sys.argv else 'parent'
    source=D/('knight.blend' if tag=='candidate' else 'parent.blend')
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    s=bpy.context.scene;p=json.loads(s['knight_mission_pose'])
    pose=[p[k] for k in ('dx','dy','twist_degrees')]
    data={};arrays={}
    probe=point_probe(s)
    coords=[(343,305),(336,306),(352,306),(371,307),(387,307),(411,311),(454,321),
            (319,340),(347,338),(377,337),(408,340),(454,351),(375,357),(423,360),(465,364),
            (440,373),(449,376),(460,374),(469,370),(462,386),(476,379),(481,372),(470,359),(475,353),
            (372,372),(390,383),(450,396),(492,397),(502,398),(514,405),(525,415)]
    for part in ['swept rounded mane','near swept ear','far swept ear']:
        ob=s.objects['Knight | '+part];v=rest_coords(world_vertices(ob),pose).reshape(-1,64,3)
        cov=np.array([k.value for k in ob.data.attributes['Knight varnish coverage'].data]).reshape(-1,64)
        arrays[part]=v;arrays[part+' finish']=cov
        data[part]={'mods':[[k.type,getattr(k,'levels',None)] for k in ob.modifiers],'rings':np.round(v.mean(1),3).tolist()}
    hits=[]
    for xy in coords:
        h=probe(xy[0]+.5,xy[1]+.5)
        if h:
            pt=rest(h[2],p);label=h[1].split(' | ')[-1]
            result={'xy':xy,'part':label,'rest':np.round(pt,4).tolist()}
            if label in arrays:
                rings=arrays[label];idx=np.unravel_index(np.argmin(np.linalg.norm(rings-np.array(pt),axis=2)),rings.shape[:2])
                result['ring_and_lane']=list(map(int,idx));result['finish_at_closest_cage_point']=round(float(arrays[label+' finish'][idx]),3)
            hits.append(result)
    np.savez_compressed(D/(tag+'-cages.npz'),**arrays)
    (D/(tag+'-survey.json')).write_text(json.dumps({'sha256':sha(source),'cages':data,'fixed_probe':hits},indent=2))
    print(tag,data)
if __name__=='__main__':main()
