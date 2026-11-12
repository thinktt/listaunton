"""Record reproducible inputs and protected pixels for bishop pigment trial 125."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
out=ROOT/'docs/bishop-mission/iteration-015';out.mkdir(parents=True,exist_ok=True)
config=ROOT/'scripts/bishop/pigment-125.json';cfg=json.loads(config.read_text())
folder=ROOT/'build/bishop-mission/125-turned-body-pigment'
source=ROOT/'history/bishop-mission-013/bishop-rebuilt.blend'
assert sha(source)=='df30b53e02c46d75342d6adc88c3fd4ca5889c8f9d7e336bb28a0ca2f40552fb'
record=json.loads((folder/'pigment.json').read_text())
assert record['config_sha256']==sha(config) and record['parameters']==cfg
before=np.array(Image.open(ROOT/cfg['source']).convert('RGBA'))
after=np.array(Image.open(folder/'albedo.png').convert('RGBA'))
meta=json.loads((ROOT/cfg['capture']/'manifest.json').read_text())
encoded=np.load(ROOT/cfg['capture']/'position.npy');valid=np.load(ROOT/cfg['capture']/'valid.npy')
z=(encoded[:,:,2]-meta['encode_offset'])/meta['encode_scale']*meta['encode_extent'][2]+meta['encode_min'][2]
protected=(~valid)|(z<=0)|(z>=3.43)
assert np.array_equal(before[protected],after[protected])
assert np.array_equal(before[:,:,3],after[:,:,3])
scope=dict(passed=True,source_atlas_sha256=sha(ROOT/cfg['source']),atlas_sha256=sha(folder/'albedo.png'),
    protected_and_alpha_pixels_exact=True,protected_height_intervals=[[-.1,0],[3.43,4.7]],
    protected_texels=int(protected.sum()),changed_texels=int(np.any(before!=after,axis=2).sum()),
    note='Direct saved-PNG comparison protects the upper head, button, caps, alpha and unused atlas regions. The independent saved-scene atlas audit checks all geometry, relief, lights and camera.')
(out/'band-scope.json').write_text(json.dumps(scope,indent=2)+'\n',newline='\n')
commands=[
 'blender --background --python-exit-code 1 --python scripts/bishop/capture_atlas_surface.py -- --source history/bishop-mission-012/bishop-rebuilt.blend --out build/bishop-mission/099-atlas-surface',
 'python scripts/bishop/analyze_atlas_visibility.py --capture build/bishop-mission/099-atlas-surface --atlas history/bishop-mission-012/bishop-boxwood-albedo.png',
 'python scripts/bishop/height_continuous_pigment.py --angular --clean-boundary-detail --out build/bishop-mission/118-harmonic-pigment',
 'blender --background --python-exit-code 1 --python scripts/bishop/capture_material_response.py -- --source history/bishop-mission-013/bishop-rebuilt.blend --out build/bishop-mission/119-current-response --samples 128',
 'python scripts/bishop/infer_visible_pigment.py --preserve-uncertain-visible --retain-visible-range --out build/bishop-mission/124-visible-range',
 'python scripts/bishop/blend_pigment_band.py --config scripts/bishop/pigment-125.json',
 'python scripts/bishop/prepare_continuous_checkpoint.py',
 'blender --background --python-exit-code 1 --python scripts/bishop/apply_atlas_trial.py -- --source history/bishop-mission-013/bishop-rebuilt.blend --atlas build/bishop-mission/125-turned-body-pigment/albedo.png --variant 125-turned-body-pigment --samples 512 --no-render',
 'blender --background --python-exit-code 1 --python scripts/bishop/finalize_render.py -- --source build/bishop-mission/125-turned-body-pigment/bishop.blend --out build/bishop-mission/125-final --atlas build/bishop-mission/125-turned-body-pigment/albedo.png --pigment-checkpoint docs/bishop-mission/iteration-015/pigment-checkpoint.json --samples 512 --fixed-samples'
]
reproduction=dict(source=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),
    config=config.relative_to(ROOT).as_posix(),config_sha256=sha(config),
    expected_atlas_sha256=sha(folder/'albedo.png'),commands=commands,
    environment='Blender 5.2.2 Cycles/OPTIX; Python with NumPy and Pillow. Preserve archived bytes and run in an isolated copy.',
    subsequent_checks='Inspect fixed/original/cropped/side BSDF views. After acceptance, stage only this model/render/atlas; run validate_checkpoint.py, render_diagnostics.py, render_clay.py, compare_export_checkpoint.py, compare.py, mission_compare.py, refresh_review.py and both bishop interaction checks before synchronization.',
    limitations='Pigment inversion is approximate under inferred lights. Actual visibility replaces the old projection mask; retained existing highlight pigment and inferred hidden wood can still contain illumination and discontinuities. No exact intrinsic-albedo claim.')
(out/'reproduction.json').write_text(json.dumps(reproduction,indent=2)+'\n',newline='\n')
declaration=dict(source=reproduction['source'],source_sha256=sha(source),
    atlas='assets/bishop/bishop-boxwood-albedo.png',atlas_sha256=sha(folder/'albedo.png'),
    config='docs/bishop-mission/iteration-015/reproduction.json',config_sha256=sha(out/'reproduction.json'),
    description='Measured visible-surface pigment on the turned lower body, with smooth inferred continuation. Upper head/button pixels, all geometry, relief, lamps and the 54-degree camera are preserved.',
    residual_limitation=reproduction['limitations'])
(out/'pigment-checkpoint.json').write_text(json.dumps(declaration,indent=2)+'\n',newline='\n')
print('CONTINUOUS_PIGMENT_CHECKPOINT_PREPARED',json.dumps(scope),flush=True)
