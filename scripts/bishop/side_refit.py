"""Fit bishop 025 to the owner's side proportions at its original physical registration."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).parent))
from shared_turning import (ROOT, BODY, BUTTON, SEGMENTS, control_rings, meridian, digest,
                            remove_receivers, restore_receiver_band, render_saved)
from inspect_shared_turning import measure, render_level

DOC = ROOT/'docs/bishop-mission/iteration-026'
CONFIG = DOC/'side-refit.json'
RUN = ROOT/'build/bishop-mission'
from side_refit_profile import SOCKET, COLLAR, MITRE, shape

def put_rings(obj, rings):
    obj.data.vertices.foreach_set('co', np.ascontiguousarray(rings,dtype=np.float32).ravel())
    obj.data.update()


def build(case_name, spec, samples):
    src=ROOT/spec['source']
    assert digest(src)==spec['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False)
    scene=bpy.context.scene
    body, button=bpy.data.objects[BODY],bpy.data.objects[BUTTON]
    old=control_rings(body)
    old_profile=meridian(old)
    height=json.loads((src.parent/'mesh.json').read_text())['bounds']['size'][2]
    case=spec['cases'][case_name]
    new, dz=shape(old_profile,height,spec,case)
    hr,hz=case['head_radius'],case['head_height']
    memberships=remove_receivers(scene)
    rings=old.copy()
    rings[:,:,:2] *= (new[:,0]/old_profile[:,0])[:,None,None]
    rings[:,:,2] = new[:,1,None]
    put_rings(body,rings)
    finial=control_rings(button)
    finial[:,:,:2]*=hr
    finial[:,:,2]=finial[:,:,2]*hz+dz
    put_rings(button,finial)
    cutter=next(m.object for m in body.modifiers if m.type=='BOOLEAN')
    # Preserve the rounded floor and oblique plane even if the cutter's
    # existing local axes are rotated. Transform its actual cage in that frame.
    affine=Matrix.Diagonal((hr,hr,hz,1.))
    affine[2][3]=dz
    cutter.data.transform(cutter.matrix_world.inverted() @ affine @ cutter.matrix_world)
    cutter.data.update()
    bpy.context.view_layer.update()
    band=json.loads(scene['bishop_receiver_trial'])['socket_z_band']
    restore_receiver_band(scene,memberships,[z*spec['base_factor'] for z in band])
    profile=json.loads((ROOT/spec['source_profile']).read_text())
    factor=1254/300/json.loads((ROOT/'assets/bishop/original-alignment.json').read_text())['scale']/profile['scale']
    cos=math.cos(math.radians(54))
    y0=profile['y0']
    def projected(rz):
        return np.stack((rz[:,0]/factor, y0-rz[:,1]*cos/factor),axis=1).tolist()
    def axis(y):
        return y0-(y0-y)*hz-dz*cos/factor
    profile['profile']=projected(new)
    profile['finial']['profile']=projected(meridian(finial))
    for key in ['head_cap_axis_y','button_bottom_axis_y']:
        profile['head_button_join'][key]=axis(profile['head_button_join'][key])
    slit=profile['slit']
    slit['bottom_center_y']=axis(slit['bottom_center_y'])
    slit['x']*=hr
    old_angle=math.radians(slit['angle'])
    new_angle=math.atan(math.tan(old_angle)*hr/hz)
    slit['width']*=hr*math.cos(new_angle)/math.cos(old_angle)
    slit['angle']=math.degrees(new_angle)
    decl={'config':CONFIG.relative_to(ROOT).as_posix(),'case':case_name,
          'height_factor':spec['height_factor'],'base_factor':spec['base_factor'],
          'head_radius':hr,'head_height':hz,'head_z_translation':dz,
          'axis_slope':hz,'axis_offset':axis(profile['shared_turning']['upper_axis_offset'])}
    profile['side_refit']=decl
    profile['revision']='side-refit-'+case_name
    scene['bishop_side_refit']=json.dumps(decl,sort_keys=True)
    out=RUN/('side-refit-'+case_name)
    out.mkdir(parents=True,exist_ok=True)
    (out/'profile.json').write_text(json.dumps(profile,indent=2)+'\n')
    scene.cycles.samples=samples
    scene.render.filepath='//render.png'
    scene.render.resolution_percentage=100
    scene.render.use_border=scene.render.use_crop_to_border=False
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'bishop.blend'))
    return out


def diagnostics(out,path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    scene=bpy.context.scene
    body=bpy.data.objects[BODY]
    for modifier in body.modifiers:
        if modifier.type=='SUBSURF':
            modifier.levels=modifier.render_levels
    bpy.context.view_layer.update()
    row, section=measure(scene,body,True)
    row.update(side=render_level(scene,body,True,out),source_sha256=digest(path))
    np.save(out/'meridian.npy',section)
    (out/'measures.json').write_text(json.dumps(row,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('cases',nargs='+')
    p.add_argument('--samples',type=int,default=48)
    p.add_argument('--render-existing',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    spec=json.loads(CONFIG.read_text())
    for name in args.cases:
        out=RUN/('side-refit-'+name)
        out.mkdir(parents=True,exist_ok=True)
        if name=='025':
            diagnostics(out,ROOT/spec['source'])
            continue
        if not args.render_existing:
            build(name,spec,args.samples)
        diagnostics(out,out/'bishop.blend')
        render_saved(out,args.samples)
        print('BISHOP_SIDE_REFIT_RENDERED',name,flush=True)
