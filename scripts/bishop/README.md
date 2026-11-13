# Bishop reconstruction

## Geometry phase after checkpoint 015

The owner started a new geometry-focused goal on November 12, 2026, without
changing the mission statements. Read `docs/bishop-mission-log.md` for current
acceptance. Checkpoint 015 remains the preserved wood baseline. Do not treat a
high exterior overlap, a photographic shadow, or pigment copied from the
reference as proof that an internal surface is correct.

`profile_shape_trial.py CONFIG` edits only explicitly listed controls from a
hashed preserved scene. It rebuilds both exact render receivers, restores their
light links, saves/reopens the model, and renders wood and neutral comparisons.
It does not rebake pigment or alter lamps. `validate_profile_shape.py` independently
checks the actual changed controls, all untouched geometry, topology, cutter,
UVs, packed pixels, lights and saved camera. Its audit replaces the obsolete
unchanged-geometry assertion for a declared geometry phase; the existing
closure, slit and head/button anatomy checks still run on the new model.

Reproduce checkpoint 017 with `docs/bishop-mission/iteration-017/profile-fit.json`.
The analytical fitter proposes profiles only. A fit that becomes angular in
side view or mistakes a shadow trough for a rim is rejected even if it reduces
outline error. The measured collar boundary comes from evaluated mesh positions,
separately from the photographic edge interpretation.

After acceptance, export and validate with `validate_checkpoint.py`, render
the same saved model with `render_diagnostics.py`, retain its neutral fixed
render, and rebuild via `refresh_review.py`. Run both bishop interaction checks.
The overlay now has a Surface control: Neutral is the geometry-phase default;
Boxwood preserves the unfinished material for comparison. Changing surfaces
does not change image placement, opacity, reference choice or orbit. The static
neutral overlay also works without WebGL. Browser verification is simulated;
no native browser inspection is claimed.

Checkpoint 018 corrects the middle collar behind the head with a coupled
radius/height edit. Use its tracked `profile-fit.json` with the same trial
builder, starting from `history/bishop-mission-017`. `capture_turning_edges.py`
identifies the actual surface behind outline pixels and measures front rim
extents; `capture_slit_boundary.py` projects visible cut faces independently
of shader brightness. These diagnostics do not fit photographic shadows as
if they were physical edges. See iteration-018 for reproduction and findings.
The collection/sync helpers accept checkpoint, prior/source checkpoint and
log-prefix arguments; they still guard bishop-only delivery and unchanged
missions, sources and shared settings. Do not rerun an old delivery command
against a newer public checkpoint.

Checkpoint 019 is a small foot-wall correction, not a resolution of the owner's
reported swollen appearance. Its `profile-fit.json` changes only rings 6-9
from `history/bishop-mission-018`. Collar compression and deck experiments are
recorded but unaccepted. `render_geometry_studio.py` makes unsaved neutral
views with broad, unfitted white lights; it helps separate geometry from the
inherited localized reflector rig. It does not change the saved scene.

`record_foot_checkpoint.py` records the 019 trials and crops only the artwork
from the owner's blink recording. The full recording and unrelated browser
chrome stay out of the repository. Collection explicitly permits at most
0.1% diameter drift from the local evaluated bevel change and records the
actual delta; model height, camera and gallery sizing stay unchanged. The
default collection bound tolerance remains exact for other checkpoints.

Checkpoint 020 fits the button's visible boundary with a shallower lens and a
localized continuous head-tip extension. `profile_shape_trial.py` and the
independent scope auditor now support declared `finial_rings` plus
`head_cap_axis_y`; unlisted controls in both components remain exact. The
explicit `profile` arrays and `mission_shape_refit` are authoritative after
these edits; `head_curve` retains the earlier construction seed. The anatomy
probe and rejected-neck regression cover the higher join without relaxing
their contact, taper or neck criteria. `validate_shape_trial.py` runs these
scope/anatomy checks on isolated candidates. See iteration-020 for the rejected
cup underside, localized-tip choice and first-hit boundary evidence.

Checkpoint 021 removes a small socket-top height reversal using only rings
28-30. Reproduce from `history/bishop-mission-020` with the ordinary trial
builder and `docs/bishop-mission/iteration-021/profile-fit.json`. The stem's
seating control, all radii and all surrounding anatomy remain exact. The
raised-root and shallower lower-collar tests are rejected. The latter worsens
the original outline; do not revive it as a general collar compression.
`measure_socket_join.py` samples the evaluated socket top with vertical rays
below the collars. It verifies the physical trough independently of pigment
or reflections; it does not prove that an unclear photographic boundary is a
crease. `record_socket_checkpoint.py` retains the trials, source crops and
unfitted neutral level views. Preserve the current material/lighting mismatch
in the assessment and keep the geometry goal separate from full completion.

## Current wood mission

The bishop refinement mission is `MISSION-BISHOP.md`; its score/evidence log is
`docs/bishop-mission-log.md`. The first material checkpoint preserves every
control vertex and face of the accepted continuous-head geometry (evaluated coordinates agree within 0.000005 units). Its wood
is inferred from selected white candidate 3 with a separately generated,
approximately de-lit pigment source. Hidden surfaces use continuous procedural
boxwood. This is reconstructed material, not a recovered original asset.

Reproduce the first material checkpoint from its recorded config under
`docs/bishop-mission/iteration-001/` with Blender `mission_material.py -- CONFIG`,
then `bake_mission.py -- --source TRIAL/bishop.blend --out BAKED_TRIAL`.
The bake captures pigment only and reopens the saved scene before its real
Principled-BSDF beauty render. References and registration stay unchanged.

After accepting a trial into `models/bishop/bishop-rebuilt.blend`, run Blender
`export_mission.py`, `render_diagnostics.py`, `render_clay.py`, `validate.py -- ROOT`,
`validate_mission.py`, and `check_join_regression.py -- ROOT`. Ordinary Python
`mission_compare.py --render assets/bishop/render.png --out EVIDENCE_DIRECTORY`
records the mission mask convention and cropped evidence. Run ordinary Python
`refresh_review.py`, then Node `check_viewer.cjs ROOT` and `check_review.cjs ROOT` for the actual page's
texture/hash, camera and interaction harness. The rotating Boxwood view embeds
the same pigment atlas and evaluated UVs; its lighting is approximate.

At every accepted major checkpoint, `refresh_review.py` rebuilds both
`bishop-model.html` and the main `bishop-review.html`. The main page opens the
current reference overlay, with direct tabs for rotation and reference
candidates. The same sandboxed model frame survives tab changes, preserving
the orbit and overlay controls. Its URL includes a hash of the embedded
checkpoint so a refresh gets the accepted render and mesh together.
Pass `--preview-dir PATH` to synchronize the existing local preview as well.
The general `scripts/build_candidate_pages.py` builder delegates the bishop
page to its workspace generator. Other pieces retain their shared runtime;
ordinary site rebuilds therefore preserve the bishop's checkpoint tabs.

`build_bishop.py` below reconstructs the original clay geometry. It is not the
new material pipeline and would replace the wood finish if run over accepted
outputs. `validate_mission.py` checks the declared foot-ring and button-radius
edits against the archived first boxwood model, rejecting other control-point
or topology changes. The separate anatomy validator still checks the deep
slit, continuous head, broad button contact and fixed camera.

The next geometry checkpoint widens the shallow button by 8% and flattens the
lower foot's ten outer rings. The head, slit, flare, socket, stem, collars and
camera retain their previous coordinates. Reproduce it with
`geometry_trial.py -- geometry-013.json`, then the `mission-014.json` material
config and `bake_mission.py`. Keep the resulting trial isolated until it has
passed comparison and validation. `history/bishop-mission-001/` preserves the
previous model, texture, render, exported mesh and profile.

The side gallery is pinned to that preserved sizing baseline by
`preserve_gallery_sizing.py`. Its source hashes remain checkable without moving
the owner's chosen sizes or order whenever a small model detail changes.

The third checkpoint preserves the second geometry and replaces the visible
pigment with a bounded fit to measured black/white BSDF responses. It uses
Standard sRGB, warmer reflection lamps, and a balanced diffuse-light/pigment
exposure. `docs/bishop-mission/iteration-003/reproduction.json` records the
sequence from `history/bishop-mission-002`; run it in an isolated working copy.
The reference remains unchanged. Strong reflections and uncertain pixels are
excluded from fitting, and hidden surfaces retain procedural wood. This is
an approximation; the side/rear pigment boundary and highlight shapes still
need refinement.

`probe_color_pipeline.py` checks the display transform against Blender's own
PNG export. `capture_material_response.py` and `capture_pigment_feedback.py`
write diagnostic EXRs/arrays without changing the source model. `refine_pigment.py`
changes only base color. `bake_mission.py` now isolates cut-material bake targets
and verifies all input image pixels remain unchanged before saving its atlas;
it also checks packed pixels after reopening and renders the actual BSDF.
`validate_checkpoint.py` runs the existing exporter, anatomy, material/camera
and button-join checks together in Blender. Side and neutral renders remain
separate steps. The rotating viewer reads the exported diffuse-energy balance
and display response; it still uses approximate real-time lighting.

The sixth checkpoint rounds the bottom of the editable mitre cutter. The
original parallel sides, slit width and angle, bevel, visible control meshes,
UVs, material, lighting and fixed camera remain unchanged. Reproduce the
isolated trial with `slit_trial.py` and
`docs/bishop-mission/iteration-006/slit-044.json`. Its rounded floor is an
interpretation supported by the reference, not recovered original geometry.
`validate_slit_trial.py` checks the exact declared cutter, closed components,
through opening, solid floor and unchanged surface outside the cut region.
The current profile declares this revision so `validate_mission.py` checks it
in addition to the earlier foot/button edits. Keep that declaration with the
model. Do not revert to the old cube cutter in an ordinary material iteration.

Checkpoint 007 retains checkpoint 006's geometry and pigment and adds one
glossy-only soft spot at the slit tip. Reproduce it with `lighting_trial.py`
and `docs/bishop-mission/iteration-007/lighting-056.json`, then `finalize_render.py`
at 512 fixed samples. See that iteration's `reproduction.json` for exact commands.
`validate_added_reflector.py` verifies the sole declared light addition against
the archived source, preserving all materials, camera controls, UVs and prior
lights. Use the existing geometry and site pipeline afterward. The failed
needle-like area lights must not replace the accepted spot: their preview
response was strongly sample dependent. Higher-sample evidence for the accepted
spot still shows fine noise, documented in the assessment.

`capture_added_reflection.py`, `fit_added_reflection.py`, and the reflection
convergence tools provide diagnostic measurements only. Their predictions do
not establish acceptance; render and inspect the saved real BSDF scene.
`bake_pigment_coverage.py` measures the original projection-blend confidence
without saving scene changes. The trial using that mask did not resolve the
rear material boundary and is not part of the accepted atlas.

Iteration 008 is a research checkpoint, not a new accepted model. Checkpoint
007 remains current. `docs/bishop-mission/iteration-008/assessment.md` records
five rejected pigment continuations and four rejected base-reflection trials.
`regularize_pigment.py`, `fold_hidden_pigment.py`, `continue_fine_grain.py` and
`generated_grain_trial.py` produce isolated atlases only. The generated source
under `assets/bishop/materials` is inferred and is not used by the accepted
material. `render_material_diagnostics.py` isolates pigment and bump without
saving the diagnostic scene; emission images are not beauty renders.

`capture_shading_normals.py` now accepts an explicit crop and averaging radius;
its old slit crop and single-pixel behavior remain the defaults.
`validate_light_patch.py` audits declared changes to existing lights after
reopening while preserving camera, controls, UVs, materials, world and other
light properties. It complements the existing added-light validator.

Checkpoint 009 smooths the measured base-normal reversal using only two radial
controls and repositions the confined base reflector. Its declaration remains
in the saved model/profile; `validate_base_curvature.py` checks it before the
older geometry safeguards. The rejected iteration 008 alternatives stay rejected.

Checkpoint 010 preserves that geometry and the material. Reproduce its socket
lighting from `history/bishop-mission-009` using the configuration and commands
in `docs/bishop-mission/iteration-010/reproduction.json`. The old socket lamp is
disabled, and 17 glossy-only spotlights follow measured lip normals. Run
`validate_added_reflector.py` with `--disabled-existing "socket reflection"`;
that permission allows only its energy to become zero, preserving every other
existing-light property. The validator also checks render-path settings.

`prepare_socket_lights.py`, `capture_socket_reflections.py` and
`fit_socket_reflections.py` support measured lighting studies. Blender 5.2 clamps
spot cones below one degree; keep that valid minimum and move an emitter closer
to narrow its surface footprint. Preparation/capture reject a silently clamped
cone. Response predictions guide fitting but cannot replace a fresh beauty
render. The accepted scene retains four glossy bounces; the zero-bounce trial
was rejected. Final verification uses 512 fixed samples after saving/reopening.

`assess_socket_reflection.py` records fixed crops and reference-core statistics.
`mission_compare.py` now explicitly applies largest-component/hole-fill cleanup
to model alpha as required by `MISSION-SET.md`, and reports the legacy-mask
comparison. The masks differ by zero pixels on checkpoints 009 and 010.
Follow the normal geometry/export, side/neutral render, review and preview
synchronization pipeline after any accepted lighting change.

Iteration 011 is a finish study; checkpoint 010 remains accepted. Its assessment
records rejected socket beam/roughness and grain-relief experiments. Use
`probe_socket_finish.py` and `probe_socket_emitters.py` only for unsaved cropped
diagnostics. `material_input_trial.py` saves and reopens a declared scalar/link
experiment in `build/bishop-mission`; `validate_material_input_trial.py` audits
its saved scope against the archived source, including packed pixels, geometry,
UVs, camera, lights and render-path preservation. The comparison helpers keep
the original registration and show actual BSDF renders. Failed trials are not
public model choices. See `docs/bishop-mission/iteration-011/reproduction.json`.

Checkpoint 012 confines the wider socket reflectors to two derived body render
regions. The closed turned body remains the editable control, tagged
`bishop_editable_control` and hidden only from rendering; the button stays a
separate closed component. `bishop_scene.editable_meshes` selects these controls
for export and anatomy checks. Derived objects carry `bishop_render_region`
and share the persistent control materials. Never use temporary evaluated
material pointers: they become empty slots after saving/reopening.

Reproduce with `socket_receiver_trial.py` and
`docs/bishop-mission/iteration-012/receiver-097.json`, starting from checkpoint
010, then the documented 512-sample finalization. `validate_render_receivers.py`
independently checks controls, topology, packed pixels, camera, world and the
declared light-only changes. It proves complete evaluated-face coverage, exact
positions/material indices, shared material slots, normals below .0002 error
and evaluated UVs within 1e-7 (observed one float32 ULP); control UVs stay exact.
The previous base/slit checks validate the archived closed source, connected
to the current model by this exact-control audit, while current anatomy is
still probed directly. Export retains the two closed controls.

Do not edit derived regions or render stale copies after a geometry/cutter
change. Both `geometry_trial.py` and `slit_trial.py` reject receiver-bearing
sources until receiver regeneration is implemented for the intended edit.
Material edits must preserve shared slots; light experiments must preserve
the explicit socket/body-rest receiver links unless deliberately changing them.
The 094/095 scripts are unsaved cropped diagnostics, not accepted substitutes
for the reopened full render. See iteration 012 for the residual lower-tone
tradeoff, side/rear texture defect and next work.

Checkpoint 013 retains checkpoint 012's geometry, relief and lighting, with a
bounded pigment lift only through the socket, stem and collars. Reproduce the
atlas using `capture_atlas_surface.py`, `analyze_atlas_visibility.py`, then
`grade_pigment_height.py --config scripts/bishop/pigment-106.json` from the
archived checkpoint 012. The commands and hashes are recorded in
`docs/bishop-mission/iteration-013/reproduction.json`. The old broad side/rear
pigment discontinuity remains unresolved; the continuity studies are rejected.

`apply_atlas_trial.py` and `validate_atlas_trial.py` save/reopen and independently
check a packed-atlas-only change. `finalize_render.py` accepts an explicit
`--atlas` and `--pigment-checkpoint` declaration for this revision. Finalize with
512 fixed samples, then stage the model, render and atlas in an isolated copy.
`validate_mission.py` keeps the earlier receiver/light audit strict on the
archived source and follows it with the current scene's atlas-only audit. It
also runs the existing geometry/anatomy chain and writes pigment-validation.json.
Do not pass the material-edited model directly to the older light-only audit
and weaken its comparisons to make it pass. Rebuild fixed/side/clay views and
both bishop pages; preserve all gallery defaults and source references.
The local `.gitattributes` preserves `pigment-106.json` bytes because the saved
checkpoint records its hash; Git must not change that input's line endings.

## Original geometry construction

The original Lichess white bishop is the proportion reference. The original black bishop is available as a second overlay. White candidate 3 supplies readable detail; candidate 4 was not used. Reference images remain byte-for-byte copies.

The model uses a continuous closed turned body, a separate shallow domed button with a rounded underside, and an editable Boolean saw cut through the full mitre thickness. The head's rounded Bezier meridian continues directly into the button underside, concealing the head cap. There is no exposed cylindrical seat, pedestal, neck ring or gap. The user-accepted [side guide](../../assets/bishop/concepts/side-01.png) directs this junction and the head/button appearance; the original remains the overall proportion check. The cut stops above the collars, leaving a solid floor. This is an editable visual reconstruction, not a manufacturing solid. The saved orthographic camera is 54 degrees above the board. The commands below describe the historical clay build; use the current wood mission pipeline above for accepted checkpoints.

Run from the repository root:

1. Blender: `--background --python scripts/bishop/build_bishop.py`
2. Blender level/profile/cavity views: `--background --python scripts/bishop/render_diagnostics.py`
3. Python with Pillow and NumPy: `scripts/bishop/compare.py`
4. Blender: `--background --python scripts/bishop/validate.py -- ROOT`
5. Blender junction regression: `--background --python scripts/bishop/check_join_regression.py -- ROOT`
6. Python: `scripts/bishop/build_viewer.py`
7. Node: `scripts/bishop/check_viewer.cjs`

`profile.json` stores radius and projected axis-center heights in the 300px original white image coordinates. The exporter maps those measurements into the selected-candidate frame using `original-alignment.json`. This registration is composed from candidate-to-black and original-white-to-black registrations, rather than applying the black registration directly to white. The browser uses the same inverse affine placement as the image comparisons. No reference pixels are warped or rewritten.

The historical clay revision was `09-continuous-button-join`. The preceding shallow-button revision still exposed a short cylindrical seat in a true level view; the next pass removed it, and the final pass narrowed the button toward the guide and concealed the head cap more deeply. That head curve remains exact in the wood mission; checkpoint 006 changes only the slit termination. The accepted guide is art direction, not evidence for a recovered source camera or absolute dimensions.

`assets/bishop/join-comparison.png` compares the previous and current head at the exact same level camera. `head-side.png`, `side-profile.png` and `rear-oblique.png` document the head contact, full proportions and open cut; `diagnostic-cameras.json` records those cameras. `overlay-original.png` blends the actual original with the current neutral render at the unchanged saved 54-degree reference camera. The historical `head-comparison.png` and `button-comparison.png` document earlier corrections and are not current-render comparisons.

The validator checks both closed components for positive volume, probes the deep slit and solid floor, compares saved and exported cameras, and verifies exact lower-profile preservation. It samples 100 evaluated head normals and 161 external junction sections. A single transition from tapering head to rounded button, broad contact, concealed cap and continuously present surface are required. `check_join_regression.py` also measures the rejected model's exposed cylinder and verifies its absence in the current model. The viewer test exercises actual page code, original/selected/black overlays, rotation, pan, zoom and camera reset.

The clay revision's original-white silhouette IoU was 0.96576 and selected-white IoU 0.94822 under its older mask convention. For current scores and the explicit mask definition, read `docs/bishop-mission-log.md` and its iteration records. Outline scores do not assess the formerly hidden neck. Hidden surfaces remain interpretations, and the two closed intersecting components are not boolean-fused for manufacture.
