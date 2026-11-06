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

Checkpoint 004 uses the scene and mesh from `786501b`. Run
`fit_muzzle_profile.py` with ordinary Python to generate the nose fit. In
Blender, `carve_muzzle.py` applies that envelope and the paired nostrils.
The retained trial uses depth 0.054, mouth depth 0.014, width 0.024, lip
size 0.013 and cut slope 0.84. Run `grade_muzzle_atlas.py` and
`render_pigment_grade.py` for the dark eyes and recesses. Measure this
scene with `capture_surface_response.py` in Blender. Then use
`refit_face_pigment.py` and `render_pigment_grade.py` to produce the
registered finish. Exact parameters, input hashes and the trial sequence
are in `docs/knight-mission/iteration-004`.

Checkpoint 005 starts from the model at `1b952e4`. In Blender,
`fit_swept_ear.py -- --preserve-profile` fits the upper blade while checking
the skyline. Use `locate_head_glints.py` on its exported trial mesh, then
`fit_head_reflections.py` in Blender. Run `fit_surface_polish.py` with
`--region head` and reuse the diffuse measurement and UV fitting steps with
`refit_face_pigment.py --region brow`. The last light adjustment is
`fit_brow_key.py`. The log records the rejected tall ear, retained settings,
source images and actual comparison renders.

Checkpoint 006 starts from `0cf7b33`. Use `turn_pedestal.py --collar` in
Blender for the turned rings. With ordinary Python, `measure_pedestal_arcs.py`
reads the registered front arcs and `fit_pedestal_center.py` estimates the
physical axis. Apply it with `seat_pedestal.py`. The 7-degree side camera
follows the new axis horizontally to retain the foot registration.
Run the arc measurement with `--mesh` and `--landmarks` on that export to
locate the target mirror rays for `fit_pedestal_lights.py --focused`.
Use `fit_surface_polish.py --region pedestal` and the diffuse measurement and
UV fitting steps with the same region. Finally run `fit_card_color.py` on
the registered walnut. `verify_pedestal_seat.py` checks the original
diameter, floor, mesh intersection, seat-relative coordinates and protected
upper carving. The per-trial parameters are in `docs/knight-mission/iteration-006`.

The standalone viewer embeds the actual pigment, UVs and local polish. Its real-time
lighting is an approximation. Its Front and Side presets retain the horse
orientation, and the side comparison uses the saved 7-degree camera and
shared foot registration. Update the existing local review at each accepted
checkpoint. Detailed trial evidence and remaining discrepancies are in the
mission log. The prior guide-first clay workflow is archived alongside its
model in `history/knight/mission-start`.
