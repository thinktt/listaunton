# Reproducing the surface investigation

Run from the repository root using Python with NumPy/Pillow and Blender 5.2.2
with Cycles. The captured machine used OPTIX. The source is the immutable
checkpoint-013 archive, not a rebuild from the original bishop script.
All outputs below are isolated under `build/bishop-mission`; none of these
commands promotes a public model. `collect_surface_study.py` copies evidence
only after the independent audits pass and verifies the accepted hashes.

For brevity `blender` denotes the installed executable and `python` the project
Python. Use `--background --python-exit-code 1 --python` before each Blender
script, followed by `--` and the script arguments.

1. Run `inspect_light_rig.py --source history/bishop-mission-013/bishop-rebuilt.blend --out build/bishop-mission/107-collar-light-rig.json`
   in Blender. Run `probe_collar_reflections.py --samples 128`, then
   `python scripts/bishop/assess_collar_isolation.py`.
2. In Blender run `shading_reflection_landmarks.py scripts/bishop/collar-landmarks-108.json --source history/bishop-mission-013/bishop-rebuilt.blend --out build/bishop-mission/108-collar-normals/geometry.json`.
   Run `capture_shading_normals.py --source history/bishop-mission-013/bishop-rebuilt.blend --out build/bishop-mission/108-collar-normals --points scripts/bishop/collar-landmarks-108.json --border 390 470 590 605 --mean-radius 2`.
3. Run `capture_collar_basis.py --samples 96` in Blender, then
   `python scripts/bishop/fit_collar_basis.py`. The optional cooler-tint repeat
   is `python scripts/bishop/fit_collar_basis.py --out build/bishop-mission/113-cool-collar-fit --allow-cool`.
4. Run `capture_collar_spots.py --samples 128` in Blender, then
   `python scripts/bishop/fit_collar_spots.py`. This recreates
   `scripts/bishop/lighting-112.json`. Run `lighting_trial.py scripts/bishop/lighting-112.json`
   in Blender. Independently run `validate_collar_lights.py --source history/bishop-mission-013/bishop-rebuilt.blend --model build/bishop-mission/112-collar-spots/bishop.blend --config scripts/bishop/lighting-112.json --out build/bishop-mission/112-collar-spots/light-scope.json`.
5. Run `python scripts/bishop/prepare_fine_relief.py`, then
   `fine_relief_trial.py build/bishop-mission/114-fine-relief/config.json`
   in Blender. Run `validate_fine_relief.py --config build/bishop-mission/114-fine-relief/config.json --model build/bishop-mission/114-fine-relief/bishop.blend --out build/bishop-mission/114-fine-relief/material-scope.json`.
6. Repeat step 5 with `python scripts/bishop/prepare_fine_relief.py --gain 4 --out build/bishop-mission/115-fine-relief-stronger`
   and replace the folder name in the Blender trial and independent audit.
7. For each full trial run `mission_compare.py` with its `wood.png`,
   `--previous assets/bishop/render.png` and its `comparison` output directory.
   Run `material_statistics.py assets/bishop/render.png <trial>/wood.png --out <trial>/statistics.json`.
   Use the saved 114/115 models with `render_diagnostics.py --model <trial>/bishop.blend --out <trial>/views`.
8. Run `python scripts/bishop/compare_fine_relief_details.py` to regenerate
   the enlarged fixed-coordinate finish comparison.

The archived evidence includes the input configurations, hashes, predictions,
actual renders and independent audit reports. Large EXR/NumPy response fields
and rejected `.blend` files remain reproducible working data rather than public
viewer assets. Each script records the distinction between response predictions
and actual shaded renders. Sampling/denoising can change pixels slightly across
runs; tiny metric changes are not acceptance criteria.
