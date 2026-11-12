"""Build a scoped Queen base or stem/collar transition study.

The last accepted model is the source. A composed profile relative to the
protected checkpoint is recorded for the existing topology/receiver validator.
All lights, packed material pixels, UVs and reference-camera settings survive.
This script stages candidates only; publication is a separate checked step.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from queen_scene import editable_mesh
from refine_socket_flare import read_controls, replace_meridian
from study_foot_lip import render_views

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'models/queen/queen-rebuilt.blend')
    parser.add_argument('--expected-source', required=True)
    parser.add_argument('--variant', required=True)
    parser.add_argument('--base-profile', type=Path)
    parser.add_argument('--join-lift', type=float, default=0)
    parser.add_argument('--samples', type=int, default=32)
    parser.add_argument('--build-only', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if Path(args.variant).name != args.variant or not 0 <= args.join_lift <= .10:
        raise ValueError('Unsafe variant name or out-of-study join lift')
    source = args.source.resolve()
    assert sha(source) == args.expected_source, 'Unexpected source model'
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    control = editable_mesh(scene)
    settings = json.loads(scene['mission_material_config'])
    before = read_controls(control.data, int(control['ring_segments']))
    after = before.copy()
    base = json.loads(args.base_profile.read_text()) if args.base_profile else None
    if base:
        for key, radius in base['ring_radii'].items():
            ring = int(key)
            assert 0 < ring < 50
            lengths = np.linalg.norm(after[ring,:,:2],axis=1)
            after[ring,:,:2] *= (float(radius)/lengths)[:,None]
        for key, dz in base['ring_z_offsets'].items():
            ring = int(key)
            assert 0 < ring < 50
            after[ring,:,2] += float(dz)
    after[48,:,2] += args.join_lift*.15
    after[49,:,2] += args.join_lift
    assert np.array_equal(before[50:],after[50:]), 'Collar/crown controls changed'
    assert np.array_equal(before[0],after[0]), 'Floor control changed'
    assert np.all(np.diff(after[3:51,0,2]) > 0), 'Lower meridian folded vertically'
    assert np.isfinite(after).all()
    config = copy.deepcopy(settings['side_shape_study']['config'])
    offsets = config.setdefault('z_offsets',{})
    radii = config.setdefault('radii',{})
    changed=[]
    for ring in range(50):
        if not np.array_equal(after[ring],before[ring]):
            changed.append(ring)
        if not np.array_equal(after[ring,:,:2],before[ring,:,:2]):
            radii[str(ring)] = float(np.linalg.norm(after[ring,:,:2],axis=1).mean())
        dz = float(after[ring,0,2]-before[ring,0,2])
        if abs(dz)>0:
            offsets[str(ring)] = float(offsets.get(str(ring),0))+dz
    config['variant']=args.variant
    config.setdefault('intent',{})['compact_turning']={
        'source_sha256':args.expected_source,
        'changed_rings':changed,
        'join_lift':args.join_lift,
        'base_profile':base,
        'description':'Coupled profile study; protect socket shelf/drop, collar outer bead, crown and camera.'}
    print('REBUILDING_EXACT_RECEIVERS',args.variant,flush=True)
    partition = replace_meridian(scene,control,settings,after,preserve_face_assignments=True)
    settings['side_shape_study']={'source_sha256':config['source_sha256'],'config':config,
        'control_sha256':hashlib.sha256(after.tobytes()).hexdigest()}
    settings['compact_turning_study']={'source_sha256':args.expected_source,
        'changed_rings':changed,'join_lift':args.join_lift,'base_profile':base,
        'receiver_partition':partition}
    settings['variant']=args.variant
    scene['mission_material_config']=json.dumps(settings,sort_keys=True)
    scene['mission_variant']=args.variant
    out=ROOT/'build/queen-mission'/args.variant
    out.mkdir(parents=True,exist_ok=True)
    (out/'profile.json').write_text(json.dumps(config,indent=2)+'\n')
    (out/'parameters.json').write_text(json.dumps(settings['compact_turning_study'],indent=2)+'\n')
    np.savez_compressed(out/'control-comparison.npz',before=before,after=after)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'),compress=True)
    print('COMPACT_TURNING_SAVED',args.variant,flush=True)
    if not args.build_only:
        render_views(scene,out,args.samples)
    assert sha(source)==args.expected_source
    print('COMPACT_TURNING_COMPLETE',args.variant,flush=True)

if __name__=='__main__':
    main()
