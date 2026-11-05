# Bishop reconstruction

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
