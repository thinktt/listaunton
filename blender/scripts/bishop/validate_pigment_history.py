"""Audit each saved atlas-only checkpoint back to the strict receiver source.

Archived scenes may name the public atlas path. Once the public atlas changes,
resolve that historical asset beside its archived model, by its declared hash.
Every scene transition is still independently reopened and scope-checked.
"""
import argparse, hashlib, json, sys
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from validate_atlas_trial import audit as audit_atlas
from validate_render_receivers import audit as audit_receivers
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()

def checked_path(relative, expected):
    path=ROOT/relative
    assert path.resolve().is_relative_to(ROOT.resolve()),relative
    assert path.is_file() and sha(path)==expected,(relative,'Missing or changed dependency')
    return path

def checked_atlas(declaration, model):
    named=ROOT/declaration['atlas']; expected=declaration['atlas_sha256']
    assert named.resolve().is_relative_to(ROOT.resolve())
    for path in [named,model.parent/named.name]:
        if path.is_file() and sha(path)==expected:return path
    raise AssertionError((declaration['atlas'],expected,'No hash-matching declared or adjacent archived atlas'))

def audit_chain(model, seen=None):
    model=model.resolve(); seen=set() if seen is None else set(seen)
    assert model.is_relative_to(ROOT.resolve()) and model not in seen,'Invalid or cyclic pigment history'
    seen.add(model)
    bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
    scene=bpy.context.scene
    receiver_cfg=json.loads(scene['bishop_receiver_trial']) if scene.get('bishop_receiver_trial') else None
    raw=scene.get('bishop_pigment_checkpoint')
    if not raw:
        root_audit=audit_receivers(model,receiver_cfg) if receiver_cfg else {'used':False}
        return dict(root_receiver_audit=root_audit,atlas_steps=[])
    declaration=json.loads(raw)
    source=checked_path(declaration['source'],declaration['source_sha256'])
    config=checked_path(declaration['config'],declaration['config_sha256'])
    atlas=checked_atlas(declaration,model)
    history=audit_chain(source,seen)
    step=audit_atlas(source,model,atlas)
    step['declaration']=declaration
    step['checked_config']=config.relative_to(ROOT).as_posix()
    step['historical_atlas_resolved_by_hash']=atlas.relative_to(ROOT).as_posix()!=declaration['atlas']
    history['atlas_steps'].append(step)
    return history

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',required=True);p.add_argument('--out',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);result=audit_chain(ROOT/a.model)
    out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    print('PIGMENT_HISTORY_PASSED',len(result['atlas_steps']),flush=True)
