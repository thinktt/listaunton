# Queen reconstruction at 54 degrees

The current queen is a revised version of the earlier 54-degree study. The
saved orthographic reference camera is **54 degrees above the board**, an
assumption used for the reconstruction rather than a recovered camera fact.
The side-view target is the owner's saved queen height of **83.4% of the
king**. To translate that cross-piece preference into a physical model size,
we normalize the 54-degree king model by its base diameter and use the measured
original-sprite queen-to-king base-width ratio (132/139). This implies a queen
height/base-diameter ratio of 2.1793. The mission's compact-finial iteration
measures 2.1670, within the existing 0.015 validation tolerance (physical height
is 0.59% below the mission starting model). The gallery defaults are unchanged.
That translation depends on the king model and the assumption that the sprites
share a render scale; it is not an independently measured physical height.

The model uses a continuous eight-point crown and turned body. A bounded
projected-ring fit weighted the original black Lichess sprite 70% and the
selected generated reference 30%, followed by actual Blender renders. At the
saved camera, silhouette intersection-over-union improved from 93.38% to
97.90% against the original and from 93.17% to 97.91% against the selected
reference. These scores measure the outline only, using a brightness threshold
for the dark references. They do not establish a perfect fit of the interior
contours, wood, lighting, or hidden surfaces. The collars, finial, and lighting
still have visible differences from the selected image.

The first mission checkpoint improves the upper/middle collars and finial
seating and uses reference-derived pigment with continuous generated grain on
hidden surfaces. ImageGen made a separate de-lit material source; the original
reference remains unchanged. Its pigment is projected into fixed mesh UVs and
baked into `assets/queen/queen-pigment-albedo.png`, with no scene lighting in the
bake. Some inferred pigment still contains residual recess shading and invented
grain. Prompts are recorded in `reference-delit-generation.json` and
`walnut-fine-generation.json` alongside those images.

The Blender file contains the packed editable material and studio lights. The
viewer embeds the same pigment atlas and exports the same UVs, with seam vertices
split without simplifying geometry. Its real-time shading remains an
approximation of Cycles. Mission evidence and honest scores are recorded in
`docs/queen-mission-log.md`; this is still an unfinished reconstruction.

The second mission checkpoint darkens the crown body, stem, socket and foot,
and corrects their excessive orange cast through smooth pigment grades. The
visible grain now also drives surface relief, mixed with fine pores. A fuller
finial upper curve and raised lower shoulder preserve the same maximum height.
That checkpoint's color atlas is `assets/queen/queen-pigment-albedo-v2.png`; the first
atlas remains the ungraded relief source. The second bake reuses the exact
existing UVs and bakes color only. The lighting setup remains the earlier
accepted one: tested alternatives did not improve the image overall.

The review opens on the original Lichess image and includes a Side comparison tab. The side guide is an imagined view; the model render is uniformly registered to its foot width and floor, with extra room above to prevent clipping. Its neutral and wood images are rendered from the same side camera.

The previous canonical model and all 39 inputs of the earlier projection
study are archived in `history/queen-before-54-finish`. The existing projection
pages still show those historical alternatives, not the new current queen.
Their build and validation scripts use the archived baseline.

Do not run `build_finished_queen.py` to rebuild the current material: it describes
the older mission starting point. Reproduce the first mission checkpoint from the
repository root with Blender, Python with NumPy and Pillow, and Node.js:

```sh
blender -b --python scripts/queen/refine_mission.py -- --variant 008-compact --samples 32 --config docs/queen-mission/iteration-001/008-compact-config.json
blender -b --python scripts/queen/material_from_config.py -- docs/queen-mission/iteration-001/011-directional-config.json
blender -b --python scripts/queen/project_reference_material.py
blender -b --python scripts/queen/bake_pigment_atlas.py
blender -b --python scripts/queen/validate_finished_queen.py -- --blend build/queen-mission/013-pigment-atlas/queen.blend --report-dir build/queen-mission/013-pigment-atlas
python scripts/queen/audit_mission.py 013-pigment-atlas
blender -b --python scripts/queen/publish_mission_trial.py -- 013-pigment-atlas
blender -b --python scripts/queen/validate_finished_queen.py
blender -b --python scripts/queen/export_viewer_mesh.py
blender -b --python scripts/queen/inspect_viewer_camera.py
python scripts/queen/build_viewer.py
python scripts/queen/overlay_qa.py --reference-mask max-channel
python scripts/queen/compare_finished_queen.py
python scripts/queen/build_side_comparison.py
node scripts/queen/check_viewer_camera.cjs
node scripts/queen/check_review_reference.cjs
python scripts/queen/check_projection_variants.py
python scripts/check_site.py
```

The first checkpoint is preserved in `history/queen-mission-001`. To reproduce
the second checkpoint from that saved source, use the following instead of
the first checkpoint's modeling steps; then run the same publish/validation,
export, viewer, image-comparison and site checks above with trial
`026-graded-atlas`:

```sh
blender -b --python scripts/queen/grade_pigment.py -- --config docs/queen-mission/iteration-002/021-warm-pigment-config.json
blender -b --python scripts/queen/relief_from_pigment.py -- docs/queen-mission/iteration-002/022-relief-config.json
blender -b --python scripts/queen/geometry_trial.py -- docs/queen-mission/iteration-002/024-finial-config.json
blender -b --python scripts/queen/bake_pigment_atlas.py -- --source build/queen-mission/024-rounded-finial/queen.blend --variant 026-graded-atlas --texture assets/queen/queen-pigment-albedo-v2.png --reuse-uv
blender -b --python scripts/queen/validate_finished_queen.py -- --blend build/queen-mission/026-graded-atlas/queen.blend --report-dir build/queen-mission/026-graded-atlas
python scripts/queen/audit_mission.py 026-graded-atlas
```

The runtime checks execute the viewer code with a simulated DOM and WebGL
interface; they do not replace a native browser GPU inspection.

The third checkpoint changes only the lowest collar's geometry. Its upper
quadrant is rounded into a rolled edge and drawn inward to retain the elevated
view's back outline. Both original and high-res silhouette overlap improve
slightly. The second checkpoint's pigment, relief and lights remain in use;
the subsequent texture and light trials were rejected after actual renders.
The second accepted model is preserved in `history/queen-mission-002`.

Reproduce the third geometry checkpoint, then use the existing export,
viewer/comparison and validation sequence above:

```sh
blender -b --python scripts/queen/geometry_trial.py -- docs/queen-mission/iteration-003/039-reproduction-config.json
blender -b --python scripts/queen/validate_finished_queen.py -- --blend build/queen-mission/039-rolled-collar-refit/queen.blend --report-dir build/queen-mission/039-rolled-collar-refit
python scripts/queen/audit_mission.py 039-rolled-collar-refit
blender -b --python scripts/queen/publish_mission_trial.py -- 039-rolled-collar-refit
```

The publishing helper retains renderer data between the four renders to avoid
repeating initialization. It still renders each view normally. Failed lighting
studies also established that the light data's diffuse/specular factors do not
provide the intended Cycles separation here; explicit object ray visibility
does. Their diagnostic results, full scores and rejected ImageGen texture
experiment are recorded under `docs/queen-mission/iteration-003`.

The fourth checkpoint retains that geometry and uses
`assets/queen/queen-pigment-albedo-v3.png`. Its pigment retains a broad color
field while replacing some invented detail with bounded fine grain inferred
from the unchanged reference. Hidden surfaces retain continuous prior wood.
The original atlas still supplies relief; consequently, some visible pores
and larger relief lines do not yet agree with the new pigment. The new atlas
bakes color only, with the existing UV layout.

The reference lighting now uses powers fitted through AgX to displayed colors,
with separate diffuse and glossy ray visibility. It improves the base highlight
and reduces stray glints. The thin collar/socket crescents and finial spots
remain imperfect. This is an art-directed reference rig, not a recovered
studio. The browser embeds the same mesh/camera/color atlas but continues to
use approximate real-time lighting.

The third model and four renders are preserved in `history/queen-mission-003`.
Reconstruct the fourth checkpoint from tracked inputs with:

```sh
blender -b --python scripts/queen/rebuild_material_checkpoint.py -- docs/queen-mission/iteration-004/reproduction.json
```

This creates `build/queen-mission/060-fourth-reproduced` and does not overwrite
the current model. Use the validation/export sequence above to promote any
future accepted trial. The reconstruction is checked against the actual
fourth-checkpoint render, including a save/reopen texture check. Diagnostic
reports and scores are under `docs/queen-mission/iteration-004`.

A float-image packaging defect was found before publication: repacking edited
linear values into a reopened sRGB-tagged EXR darkened them on reload. New
projection experiments use a fresh explicitly linear color image, save EXR
before packing, and keep confidence in a separate grayscale image. Validate
the saved pixel values, not only an in-memory render. The current v3 atlas is
a conventional sRGB PNG and has a separately verified rebuild path.

The fifth checkpoint uses `assets/queen/queen-pigment-albedo-v4.png` to correct
regional pigment color. The bowl is less orange, the base and collars are
darker, and the socket, stem and foot have small channel adjustments. It
preserves geometry, camera, UVs, relief and lighting. All eight sampled
non-highlight RGB medians are within one byte level per channel of the
reference; this limited statistic does not measure the whole tonal pattern
or establish a perfect color match. The working five-category score is 78.79%.

The fourth model and renders are preserved in `history/queen-mission-004`.
Rebuild the fifth material from tracked inputs with:

```sh
blender -b --python scripts/queen/rebuild_material_checkpoint.py -- docs/queen-mission/iteration-005/reproduction.json
```

This creates `build/queen-mission/069-fifth-reproduced`. To reconstruct the
color grading itself, use `grade_pigment.py` with the iteration's
`063-reproduction-config.json`, then `bake_pigment_atlas.py` with `--reuse-uv`.
The fifth iteration's relief and sharper-varnish experiments were rejected.
Emission passes in its evidence directory isolate color and projection
coverage for diagnosis; the delivered images are ordinary 3D BSDF renders.

The sixth checkpoint makes a small lighting-only change: the tall base
reflector uses a 36-degree spread and 10.6422 W instead of its unrestricted
219.036 W. Fitting its power preserves the base contribution while reducing
spill onto the finial. Other lights, geometry, v4 pigment and relief stay the
same. More extensive confinement and power refits were visually rejected.

The fifth model and renders are preserved in `history/queen-mission-005`.
Rebuild the sixth checkpoint with:

```sh
blender -b --python scripts/queen/rebuild_material_checkpoint.py -- docs/queen-mission/iteration-006/reproduction.json
```

This creates `build/queen-mission/076-sixth-reproduced`. The current working
score is 79.19%, with persistent curvature, grain and reflection mismatches.
See the iteration evidence before revisiting the rejected lighting fits.


The eighth checkpoint keeps the sixth geometry, v4 pigment, relief, camera
and light powers. It removes unwanted finial reflections by linking 25
non-finial glossy lights to the turned body only. Three finial spots retain
the compact glints. Larger regional lighting fits were rejected after actual
renders; the seventh checkpoint records earlier rejected trials.

The Blender scene retains one closed editable control mesh. Final renders
use two derived receiver meshes with exactly the same evaluated face positions
and atlas UVs, shared wood material, and copied smooth corner normals. They
are hidden in the viewport; the editable control is hidden from rendering.
The viewer still exports the closed control surface, not separate open parts.
`queen_scene.py` selects the correct objects for exporting and material changes.

Rebuild from the archived sixth checkpoint with:

```sh
blender -b --python scripts/queen/build_finial_receiver_checkpoint.py -- --variant 089-eighth-reproduced
```

This creates a separate trial, preserving the delivered model. Validate and
publish it through the usual pipeline. Geometry edits require regenerating
the derived receivers before rendering; otherwise they would still show the
old surface. Never edit a receiver directly. The geometry-trial helper stops
on receiver-bearing sources to prevent that mistake. The receiver validator
compares every evaluated face and atlas UV against the closed control,
checks normals within precision, shared material and intended light links.

The browser's lighting remains approximate. Fixed renders and side images
are actual Cycles BSDF renders. The working score is 79.79%, holistic 75–80%;
coarse relief, bowl/rim shaping and collar/socket highlights remain unfinished.


The tenth checkpoint follows the owner correction to seat a smaller finial
farther inside the crown. Rings 107-116 are compressed 10% vertically around
ring 106 and reduced 4% radially, with a blended root. Rings 0-106, the camera,
UVs, material and light powers remain unchanged. Because the egg is the highest
point, its 0.0467-unit lowering intentionally lowers total model height; the
height validator retains its tolerance around the correspondingly adjusted
target and checks the unchanged body vertices. Gallery defaults are untouched.
Reproduce with seat_finial_trial.py -- --variant 098-seated-finial-reproduced
--height .90 --radius .96 from the archived eighth checkpoint. Regenerated
receivers preserve the edited control exactly. See iteration-010 evidence.


The eleventh checkpoint preserves tenth geometry and material and replaces
three broad bowl reflectors with eight small, linked spot emitters shaped
along the two reference glints. Their powers are fitted from full-wood native
cropped responses through AgX, then judged in a real full-resolution render.
See iteration-011 for reproduction commands and actual-render caveats.
The public fixed and side renders use 64 samples; diagnostic fit responses
use 512 samples and the trial beauty uses 128. Sampling differences are
reported separately from geometric or texture improvements.


The twelfth checkpoint uses queen-pigment-albedo-v5.png. Native BSDF response
measurements and one bounded actual-render feedback step refine visible pigment;
strong highlights and uncertain regions are excluded. Hidden wood, geometry,
UVs, surface normals, roughness and lights remain unchanged. The atlas bake
now explicitly uses the closed editable control and restores the render
receivers afterwards. See iteration-012 for reproduction, rejected alternatives,
saved-pixel verification, all five scores and remaining defects. At each
accepted major checkpoint, synchronize the local review, viewer and side views.


The thirteenth checkpoint uses queen-pigment-albedo-v7.png with a localized
repair beneath the socket. Four radial control rings gain a smooth transition;
all heights and other controls stay exact. Only the base-key light is reshaped
and warmed. Side inspection rejected the first plain pigment fill; the accepted
material restores bounded medium grain. Reproduce from the archived twelfth
model with scripts/queen/rebuild_base_checkpoint.py and the iteration-013 config.
Use check_material_geometry.py with --allow-base-transition and the checkpoint-12
baseline; unchanged-geometry mode remains the default. Both saved/reopened and
independent reconstruction renders agree within one RGB byte. Current scores,
actual diagnostics, residual defects and full validation are in iteration-013.


The fourteenth checkpoint restores the socket crescent with exact regional
light control and fitted physical spot emitters, then repairs two small pigment
marks into the v8 atlas. The closed editable geometry and UVs are unchanged from
checkpoint 13. Render receivers are now turned-body, stem-socket and finial;
regenerate with partition(..., socket_band=True) after future geometry edits.
Receiver verification still requires exact faces, UVs, normals, material and links.
Rebuild with scripts/queen/rebuild_socket_checkpoint.py and the iteration-014
config. Compare unchanged geometry to history/queen-mission-013 without the
base-transition flag. Consult iteration-014 for scores, actual-render comparisons,
pixel reproduction checks and remaining problems.


The fifteenth checkpoint retains the v8 atlas, relief and geometry. It refines
collar reflections using a fourth exact receiver and omits secondary glossy
interreflection after a diagnostic identified the crown-body stripe. Direct
BSDF lighting remains active; the render approximation is explicit in iteration-015.
Reproduce with rebuild_collar_checkpoint.py from archived checkpoint 14.
Future receiver regeneration requires both socket_band=True and collar_band=True.
See iteration-015 for rejected trials, reproduction and all five scores.
