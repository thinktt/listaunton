# Bishop reconstruction mission log

This mission was activated by the owner on 2026-11-05 under `MISSION-BISHOP.md`.
The owner explicitly excluded quota checks, usage watchers and polling agents.
Only the bishop is assigned here. Concurrent work on other pieces is preserved.

The original white Lichess sprite is authoritative; ungraded white candidate 3
is the selected detail reference. The camera is orthographic at 54° above the
board, with the existing image registration. Generated side and pigment images
are interpretations, not recovered originals.

## Initial examination

Baseline model: `3db345fb65a1d9579344456a717f7960f0a3894dc3a95b209cb0fe1ad52f6a3f`.
Preserved under `history/bishop-mission-000/`. See
[`iteration-000/assessment.md`](bishop-mission/iteration-000/assessment.md).

| Stage | Silhouette | Interior shape | Wood color | Grain/texture | Lighting | Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Initial clay | 94.88 | 78 | 0 | 0 | 30 | 40.58 |
| First boxwood checkpoint | 94.88 | 78 | 70 | 64 | 54 | 72.18 |
| Wider button, flatter foot | 96.20 | 81 | 70 | 64 | 54 | 73.04 |
| Measured boxwood color, warm reflections | 96.20 | 81 | 84 | 77 | 64 | 80.44 |
| Rounder button reflections | 96.20 | 81 | 84 | 77 | 66 | 80.84 |
| Confined lower reflections and restored color | 96.20 | 81 | 85 | 77 | 72 | 82.24 |
| Rounded slit termination | 96.20 | 83 | 85 | 77 | 72 | 82.64 |

Silhouette is selected-reference IoU; other scores are visual estimates.
The separate original-white IoU is 96.58%. Initial holistic appearance was
about 30–40%, with wood entirely absent.

## Iteration 001 — first boxwood material

The first iteration preserves the control geometry, evaluated geometry within
0.000005 model units, and the exact camera.
It introduces inferred pigment, continuous procedural wood on unseen surfaces,
varnish with fine relief, and separately controlled diffuse and reflection
lights. It also exports pigment UVs for the rotating viewer.

The generated pigment source and exact prompt are recorded in
`assets/bishop/pigment-generation.json`. The authoritative references are
unchanged. Neither an emission image nor a composited reference is used as a
beauty render: the accepted render must come from actual Principled BSDFs.

Trial and validation details are in
[`iteration-001/assessment.md`](bishop-mission/iteration-001/assessment.md).
Original-white silhouette IoU remains 96.58%; estimated holistic appearance is
65–75%. Geometry, finer grain and reflection shapes remain unfinished. Next:
measure and refine the button, base and foot against both image sources.
No claim of completion is made. The
mission remains active until the owner/authorized alerter stops it or its
visual-match criteria are met.

### Checkpoint delivery — main bishop page

The owner requested visible updates at each accepted major iteration.
`bishop-review.html` now opens the current reconstruction overlay and provides
three direct tabs: Reference overlay, Rotate model, and Reference candidates.
The model iframe and its orbit persist between tabs; original/selected/black
reference controls remain inside the overlay. The sidebar-free workspace
suppresses the embedded viewer's duplicate heading and tabs. No model,
material, camera or score changed in this delivery update.

`scripts/bishop/refresh_review.py` rebuilds both pages and can sync the
existing local preview. The iframe revision is derived from the complete
embedded viewer, including the rendered checkpoint. DOM/WebGL harnesses cover
tab commands, parent/source guards, retained orbit and comparison state,
all candidate pairs, and a usable static overlay without WebGL. This is
scripted UI verification, not native browser inspection. The shared candidate
runtime and the other pieces' main pages are left to their existing writers.

## Iteration 002 — wider button and flatter foot

The button is 8% wider while retaining its shallow height and direct head
contact. Ten lower-foot rings give the foot a flatter wall and a tighter
underside turn. The head, slit, flare, socket, stem, collars, global height
and fixed 54-degree camera are preserved. The small detail edits improve
original-white IoU to 97.88%, selected-white IoU to 96.20%, and original-black
IoU to 96.75% under the same mask convention.

The wood projection is rebuilt for the new surfaces, packed, reopened, rendered
and validated. The main bishop page and local preview show the accepted
checkpoint. The gallery keeps the owner's sizes and order, citing the archived
first wood model as its sizing baseline. See
[`iteration-002/assessment.md`](bishop-mission/iteration-002/assessment.md)
for comparisons, all five scores, dimensions, validation and remaining defects.
The next target is lighting contrast and the placement/shape of reflections;
the mission remains incomplete.

## Iteration 003 — measured boxwood color and warmer reflections

The geometry and 54-degree camera remain fixed. Interpolated shading normals
improve reflection placement; warm glossy lights replace the cool glints.
Measured BSDF response fitting brings the collar shadows, stem, amber color
and grain closer to selected white candidate 3. Standard sRGB avoids the
unreliable inverse mapping of some saturated gold tones in the previous AgX
setup. Diffuse energy and pigment are rebalanced to avoid capped red albedo.

The final atlas is pigment only, packed, reopened and rendered with actual
Principled BSDFs. A failed bake exposed an input-atlas overwrite through the
cut material; isolated targets and input-pixel preservation checks now catch
that failure. The failed version was never published to the local page.
Checkpoint 002 is preserved in `history/bishop-mission-002`.

The fixed-view working mean rises from 73.04 to 80.44; holistic appearance is
approximately 75–85%. Geometry scores remain unchanged. See
[`iteration-003/assessment.md`](bishop-mission/iteration-003/assessment.md)
for all five scores, rejected trials, hashes, comparisons and validation.
The bishop workspace and local preview show the same accepted model, mesh,
render and atlas. Gallery sizes/order and other pieces are unchanged.

The next priority is extending compatible pigment around the side/rear to
reduce the visible projected-to-procedural boundary while preserving the
fixed-view fit. Button/foot reflections and fine relief remain unfinished.

## Iteration 004 — rounder button reflections

Two hidden-surface pigment fills were rejected: regional color created bands,
and a uniform amber continuation left the main boundary visible. The accepted
atlas remains unchanged. A no-bump diagnostic identifies residual pigment
shading as the main continuity problem.

Only the two button reflectors change. Their elliptical shapes follow measured
surface-reflection directions; actual BSDF response passes guide their power
and warm white color. The new glints are rounder and brighter, closer to the
selected image and original sprite. A power-only fit and an unconstrained red
prediction were rejected. Fine highlight breakup still needs work.

The working mean rises modestly from 80.44 to 80.84; holistic fixed-view
appearance remains approximately 75–85%. The shape, camera, pigment, relief,
gallery proportions and other lighting stay fixed. Checkpoint 003 is preserved
in `history/bishop-mission-003`. See
[`iteration-004/assessment.md`](bishop-mission/iteration-004/assessment.md)
for all five scores, rejected trials, reproducible settings and validation.
The bishop review and existing local preview show the same accepted checkpoint.
The mission remains incomplete; lower-head glare and rear pigment continuity
are the next priorities.

## Iteration 005 — less reflection spill and restored wood color

Measured light passes show that the socket and base reflectors contribute to
the unwanted glare below the slit. Their spread is narrowed and their powers
normalized to retain the intended lower glints. The uniform gray environment
reflection is removed while preserving diffuse illumination. A bounded
measured-pigment fit restores the wood color under this lighting.

Geometry, proportions, camera and accepted button reflectors stay unchanged.
The atlas is baked with protected input images, packed, reopened and rendered
with an actual Principled BSDF. The working mean rises from 80.84 to 82.24;
holistic fixed-view appearance is still approximately 75–85%. The side/rear
material boundary remains unresolved. Conservative and grazing-angle harmonic
color extensions were tested and rejected for insufficient improvement.

Checkpoint 004 is preserved in `history/bishop-mission-004`. See
[`iteration-005/assessment.md`](bishop-mission/iteration-005/assessment.md)
for the five-category scores, actual evidence, rejected trials and validation.
The main bishop review and existing local preview are synchronized at acceptance.
Next, examine the squared slit termination against clay and both originals;
continue pursuing the material and reflection mismatches as well.

## Iteration 006 — a rounded slit termination

The flat cutter floor produced a triangular facet visible in both wood and
neutral renders. It is replaced with a semicircular termination while retaining
the original slit width, angle, through opening and edge bevel. The surrounding
head surface, button and lower piece are unchanged. A deeper rounded floor and
a doubled bevel were examined; the simpler shallow rounding was chosen.

The local shape improvement raises the interior score from 81 to 83 and the
working mean from 82.24 to 82.64. All other scores remain unchanged. At the
same 96-sample render quality all three silhouette IoUs equal checkpoint 005.
Holistic fixed-view appearance is still approximately 75–85%, not a perfect
match. The cut-edge glint, collar and foot reflections, fine relief and rear
pigment continuity remain unfinished.

Checkpoint 005 is preserved in `history/bishop-mission-005`. See
[`iteration-006/assessment.md`](bishop-mission/iteration-006/assessment.md)
for the trials, full scorecard and checks. The declared cutter is audited
separately so the existing geometry safeguards remain effective. Accepted
model, neutral/side renders, exported viewer and local review are synchronized
before the checkpoint commit. Next, examine the slit-tip reflection under the
accepted geometry without reintroducing head glare.
