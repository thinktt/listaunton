# Knight reconstruction

The current knight uses a fixed 54-degree orthographic reference camera with
12-degree yaw. Compare the original black Lichess sprite first, black candidate
2 for detailed carving and finish, and the mirrored white sprite as a second
shape check. The imagined side study supplies style and plausible proportions.
The visible model has seven closed components and two hidden construction lofts.

Read [the knight mission](../../MISSION-KNIGHT.md) and
[the current checkpoint log](../../docs/knight-mission-log.md) before editing.
The historical clay builder and its profile describe the archived starting
model. Use the current mission pipeline for new iterations. Staged builds
protect the accepted outputs until validation passes.

## Reproduce checkpoint 001

Run Blender scripts in background mode with `--python-exit-code 1`, from
the repository root. Ordinary Python steps require NumPy and Pillow. Each
trial writes into `build/knight-mission`. Keep the fixed original placement
and candidate images intact.

1. Run `fit_mission_pose.py` with ordinary Python. In Blender run
   `apply_mission_pose.py` on the archived clay, then `build_wood_trial.py`.
2. Run `prepare_grain_tile.py` with ordinary Python, then
   `capture_material.py` in Blender to measure the material response.
   `infer_pigment.py` and `project_mission_pigment.py` document trial 004.
   The retained trial uses ordinary Python `regularize_pigment.py` and Blender
   `project_mission_pigment.py -- --variant 005-softened-pigment --estimate soft-pigment`.
3. In Blender run `bake_mission_atlas.py`, `complete_pedestal_bake.py`,
   then `pack_mission_texture.py`. The last stage verifies reopened packed PNG
   bytes and sampled color coverage on every visible component. Inspect its
   actual beauty and side renders against 005.
4. Compare a trial with `python scripts/knight/audit_mission.py VARIANT`.
   Use `--previous` to identify the prior accepted render if reproducing a
   historical comparison. Record all five scores and the separate original
   and mirrored-white IoUs.
5. Promote an inspected trial in staging using Blender
   `publish_mission.py -- VARIANT --checkpoint NNN --atlas-name NAME.png --previous-hash HASH`.
   The publisher exports the same evaluated mesh, camera, normals and pigment
   UVs used by the renderer, then renders the wood, clay, registered side and
   supplementary views. New geometry trials may reuse a verified existing
   atlas when its coordinates remain valid.
6. Run Blender `validate.py -- ROOT`; run ordinary Python `compare.py`,
   `compare_guide.py`, `build_qa_sheet.py` and `build_viewer.py`. Run
   `node scripts/knight/check_viewer.cjs` followed by affected site and review
   checks. The original source hashes, canvas registration and gallery
   defaults must match their accepted inputs.

## Later checkpoints

Checkpoint 002 starts with the saved scene in `history/knight/mission-001`.
The accepted eye uses `refine_eye.py` with a convex lens, followed by
`shape_brow.py`, the fit in `lower_carving_fit.py`, `apply_lower_carving.py`
and `fit_eye_reflection.py`. The trial parameters are recorded in the mission log.

For checkpoint 003, use the model and exported mesh from `d91c807` in a
staging copy. Run `probe_reflections.py build/knight-mission/chest-light-study/probes.json`
with ordinary Python. Run `fit_chest_reflections.py` in Blender with
`--variant 016-burnished-grain --grain-height 0.0028 --beam-degrees 48 --strip-width 0.5 --samples 144`.
Then run `fit_surface_polish.py` with
`--source build/knight-mission/016-burnished-grain/knight.blend --variant 017-fitted-varnish --radius 4 --samples 144`.
The scene stores the local polish on the surface as `Knight varnish coverage`.
The viewer export writes one coverage byte per vertex in `varnish.bin`.
For a native browser check, run `node scripts/knight/check_native_viewer.cjs`
with Playwright available. Set `LISTAUNTON_CHROMIUM_BINARY` to an installed
Chrome or Edge executable when using a system browser.

The standalone viewer embeds the actual pigment, UVs and local polish. Its real-time
lighting is an approximation. Its Front and Side presets retain the horse
orientation, and the side comparison uses the saved 7-degree camera and
shared foot registration. Update the existing local review at each accepted
checkpoint. Detailed trial evidence and remaining discrepancies are in the
mission log. The prior guide-first clay workflow is archived alongside its
model in `history/knight/mission-start`.
