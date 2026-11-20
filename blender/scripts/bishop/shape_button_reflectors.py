"""Shape two physical area reflectors using local surface-reflection derivatives."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--landmarks',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);data=json.loads((ROOT/a.landmarks).read_text());lights=[];details={}
for prefix,name in [('main','button reflection'),('small','Button second glint')]:
    point=data[prefix];center=np.array(point['position']);direction=np.array(point['light_direction'])
    # Project the reflected rays from four patch edges onto the central lamp plane.
    def edge(suffix):
        q=data[prefix+'_'+suffix];loc=np.array(q['surface']);ray=np.array(q['light_direction'])
        distance=np.dot(center-loc,direction)/np.dot(ray,direction)
        return loc+distance*ray
    mapping=np.stack([(edge('x1')-edge('x0'))/2,(edge('y1')-edge('y0'))/2],axis=1)
    U,singular,_=np.linalg.svd(mapping,full_matrices=False)
    major=U[:,0];minor=np.cross(direction,major);minor/=np.linalg.norm(minor)
    rotation=Matrix((Vector(major),Vector(minor),Vector(direction))).transposed().to_euler()
    lights.append({'name':name,'shape':'ELLIPSE','size':float(singular[0]*2),'size_y':float(singular[1]*2),
        'location':center.tolist(),'rotation_euler':list(rotation)})
    details[name]={'pixel_center':point['pixel'],'half_axis_lengths_world':singular.tolist(),
        'note':'First-order shape estimate from smooth geometry; actual rough BSDF response must be rendered.'}
result={'source':data['_provenance']['source'],'variant':'033-shaped-button','samples':48,'lights':lights,'shape_measurements':details}
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
