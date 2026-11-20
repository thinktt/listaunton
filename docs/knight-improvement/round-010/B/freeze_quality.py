"""Verify the frozen scene at matched sections and export all geometric measurements."""
from pathlib import Path
import hashlib,json,sys
import bpy,numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D))
from carve import load,pose,rest_coords,world_vertices,sha,PARENT,PIGMENT
from sections import sections
from dimensions import height
from check_final import self_cross

def inspect(name):
    scene=load(name);p=pose(scene)
    geoms={s:rest_coords(world_vertices(scene.objects['Knight | '+s+' swept ear']),p).reshape(7,64,3) for s in ['near','far']}
    mat=scene.objects['Knight | swept rounded mane'].active_material
    im=mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image
    return {'model_sha256':sha(D/name),'height':height(scene),'sections':sections(scene),
        'ear_mirror_error':float(np.abs(geoms['near']-geoms['far']*[1,-1,1]).max()),
        'native_self_intersections':{part:self_cross(scene,part) for part in ['swept rounded mane','near swept ear','far swept ear']},
        'packed_pigment':{'image_name':im.name,'sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest()}},geoms
def main():
    parent,ear0=inspect('parent.blend');candidate,ear1=inspect('knight.blend')
    endmax=max(float(np.abs(ear0[k][[0,6]]-ear1[k][[0,6]]).max()) for k in ear0)
    assert parent['model_sha256']==PARENT
    assert parent['packed_pigment']==candidate['packed_pigment']
    assert sha(D/'pigment.png')==candidate['packed_pigment']['sha256']==PIGMENT
    assert abs(candidate['height']['height']/parent['height']['height']-1)<.01
    assert endmax<1e-6 and candidate['ear_mirror_error']<1e-5
    assert max(candidate['native_self_intersections'].values())==0
    assert candidate['sections']['max_medial_shortfall']<1e-5
    assert candidate['sections']['maximum_absolute_top_midpoint']<.006
    assert candidate['sections']['max_positive_step_outward']<1e-5
    assert candidate['sections']['max_mirror_abs']<.0006
    out={'parent':parent,'candidate':candidate,'maximum_endpoint_movement':endmax}
    (D/'frozen-sections-and-height.json').write_text(json.dumps(out,indent=2)+'\n')
    print('NATIVE_SECTIONS_PASS',candidate['model_sha256'],candidate['height'])
if __name__=='__main__':main()
