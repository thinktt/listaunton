# Bishop reconstruction mission log

## Mission-statement cleanup — 2026-11-12

The owner requested static goals with progress recorded separately. The
piece mission now preserves the original full visual-match objective and
five-category standard. This is a documentation migration, not a new model
iteration, fresh assessment, or change to the accepted model. The complete
pre-cleanup statement is available in Git at `fb75902169d17a993280dbd593f8d5163204e592:MISSION-BISHOP.md`.

### Information moved out of the mission

Former drafting snapshot (historical, not the current accepted hash):

- Model SHA-256 at drafting: `3db345fb65a1d9579344456a717f7960f0a3894dc3a95b209cb0fe1ad52f6a3f`.

The former statement said full-material scores were unassessed. That was a
historical drafting statement, not a new assessment; use this log's actual
iteration evidence to establish the accepted state and current scores.

The statement also carried a snapshot saying the queen goal was paused.
Activation and pause state belong to the relevant goal, not this piece's mission.

Future checkpoints, scores, defect lists and phase completion belong in this
log and the iteration evidence. Change the static goal only at the owner's
direction. Apply [the shared mission standards](../MISSION-SET.md).


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

## Iteration 007 — a localized slit-tip reflection

A glossy-only soft spot restores the small cream glint at the slit termination.
The earlier area-light trials were rejected after their brightness changed
drastically with sampling. The accepted source is positioned from measured
surface normals and checked in actual full and higher-sample cropped renders.
Fine highlight noise remains; this is a local improvement, not convergence
to a perfect reference match.

Geometry, camera, pigment, material nodes, the original lighting rig and gallery
proportions are preserved. The final scene is saved, reopened and rendered at
512 fixed samples; an equally sampled baseline isolates the added reflection.
The tip-region RGB error decreases from 20.68 to 16.40 /255. The lighting score
rises from 72 to 73, and the working mean from 82.64 to 82.84. Holistic fixed-view
appearance remains approximately 75–85%.

A separate rear-pigment continuation is rejected because its main boundary
remains visible. Checkpoint 006 is preserved in `history/bishop-mission-006`.
See [`iteration-007/assessment.md`](bishop-mission/iteration-007/assessment.md)
for the full scorecard, sampling limitations, rejected trials and validation.
The bishop review and existing local preview are refreshed together at
acceptance. The next material trial must address residual shading inside the
projected pigment, rather than repeating a protected hidden-only fill.

## Iteration 008 — pigment continuity and base-reflection research

Checkpoint 007 remains the accepted model and the page's visible result.
Five material trials and four lower-reflection trials were rendered, compared
and rejected. A pigment-only diagnostic and constant-color control identify
the rear patch as primarily embedded color. Keeping its fine residual preserves
the boundary; wrapping whole front strips produces false bands. Generated
grain gives a cleaner inferred source, but smoothing the combined material
weakens important front contrast. It is not installed on the accepted model.

The base reflection's measured bright center is roughly 16 pixels left and
20 pixels above the selected reference. Cream-colored lights, measured normal
placement, a flatter emitter and a bounded positional interpolation were
tested. They either retain the tall misplaced glint, add foot spill, or remove
the intended reflection. The next experiment should inspect base curvature
and its normal distribution before continuing to move the light.

All five accepted scores remain 96.20 / 83 / 85 / 77 / 73, with a working mean
of 82.84 and a holistic fixed-view range of 75–85%. See
[`iteration-008/assessment.md`](bishop-mission/iteration-008/assessment.md)
for every trial's scorecard, generated-texture provenance and diagnostic
evidence. Research scripts and records are checkpointed; failed models are
not offered in the review controls. The mission remains incomplete.

## Iteration 009 — smoother base and a better placed reflection

Two lower-flare radii remove a measured curvature reversal while preserving
every height, overall size and the upper piece. The existing base reflector
is moved to the measured reference core; a small disk and narrow beam remove
the foot glare introduced by broader lighting trials. The final scene is
saved, reopened and rendered with 512 fixed samples.

This is a small accepted improvement with a recorded tradeoff. The core's
placement/color improve and foot spill decreases, but broader base tone is
slightly worse and silhouette overlap falls about 0.09 percentage points.
Scores are 96.11 / 84 / 84 / 77 / 75; working mean 83.22, holistic range 75–85%.
See [`iteration-009/assessment.md`](bishop-mission/iteration-009/assessment.md)
for all trials, measurements, limitations and checks. Checkpoint 007 remains
archived. At acceptance, the bishop review and existing preview are refreshed
with the matching model, render, export and side views. The mission is still
incomplete. The owner requested a pause after finishing this checkpoint; the
socket crescent and unwanted lower glint are the next target on resumption.

## Iteration 010 — a brighter socket lip with less reflection spill

Work resumed at the owner's direction on November 12, 2026. The old socket
reflector is disabled and replaced by localized glossy-only spots. Surface
normal measurements and actual BSDF response passes guide their placement and
power. Moving them closer narrows their footprint without requesting a cone
smaller than Blender's one-degree minimum. Earlier wider, clamped-cone and
zero-secondary-bounce trials are rejected.

The saved/reopened 512-sample render improves the intended cream lip and reduces
the lower streak without the false upper-stem arc seen in intermediate trials.
Geometry, UVs, pigment, the 54-degree camera, other lights and four glossy bounces
remain unchanged. The reflection is still too thin and speckled, and broader
image color has a small recorded regression. This is a local improvement.

Scores are 96.11 / 84 / 84 / 77 / 76; the working mean rises from 83.22 to 83.42,
with a holistic fixed-view estimate of 75–85%. Checkpoint 009 is archived in
`history/bishop-mission-009`. See
[`iteration-010/assessment.md`](bishop-mission/iteration-010/assessment.md)
for the trials, original-reference checks, quantitative tradeoffs and limitations.
At acceptance the bishop review, exported mesh, fixed/side renders and existing
Windows preview are synchronized from the same validated model.

The mission remains incomplete. Next inspect socket roughness/normal response
to broaden and smooth the crescent while preserving this result. Fine grain,
collar/base reflections, slit-edge finish and the side/rear pigment boundary
remain unresolved. No quota monitoring was performed.

## Iteration 011 — finish studies without replacing checkpoint 010

The owner resumed work on November 12, 2026 and confirmed that no pause was
requested. The goal is active. Four cropped material isolations and four emitter
studies investigate the thin socket reflection; five saved/reopened full trials
investigate pore scale and pigment-related relief. All thirteen experiments are
rejected for promotion. The accepted model, review and preview remain checkpoint
010, now preserved under `history/bishop-mission-010` as well.

Removing or smoothing bump does not recover the broad socket band. Wider beams
produce a false upper arc, despite slightly better crop error. Coarser pores
either smooth the finish or make it pebbled. Driving relief from the refined
color atlas makes little difference at modest strength; stronger settings turn
pigment markings into exaggerated raised texture, particularly at the foot.
The matching atlas is therefore a useful investigation path, not an accepted
surface solution by itself.

Accepted scores stay 96.11 / 84 / 84 / 77 / 76, mean 83.42%, holistic 75–85%.
Every full trial has a five-category assessment, fixed original/reference
comparisons and an independent reopened material-scope audit. See
[`iteration-011/assessment.md`](bishop-mission/iteration-011/assessment.md).

Next investigate confined socket illumination with the measured normal field,
potentially using an exact derived socket light receiver with full preservation
and exporter checks. Texture needs relief separated from broad pigment and
illumination; simply multiplying color-derived bump is not sufficient. The
side/rear material boundary remains unresolved. This is an incomplete research
checkpoint, not a pause or a completed reconstruction.

## Iteration 012 — wider socket reflections without the upper arc

The owner has not requested a pause. Exact derived render regions let the
17 socket reflectors use wider beams without illuminating the upper stem.
Their power, color and placement stay unchanged. Excluding the collar reflector
from the socket reduces the stray lower glint. The original closed editable
body, button, slit, packed wood, UV controls and fixed 54-degree camera remain
preserved; the viewer still exports the two closed components.

The saved/reopened 512-sample result is a small accepted improvement with a
tradeoff: the cream band is broader and its reference-core error decreases
45.20 → 35.03 /255, but the lower socket becomes slightly too dark. Whole-piece
foreground RGB error improves 7.72 → 7.69. The reference's broader, irregular
band is still not reproduced. Scores are 96.11 / 84 / 84 / 77 / 77, working mean
83.62%, holistic 75–85%. See
[`iteration-012/assessment.md`](bishop-mission/iteration-012/assessment.md).

An invalid initial save lost temporary evaluated-material links. That render
is rejected; the corrected builder uses persistent material slots, with a
reopened scope audit. All render-region faces, materials and surface data are
checked against the unchanged closed control. Evaluated UV rounding of at
most 5.96e-8 is reported explicitly; geometry and control UVs are exact.
The bishop pages, fixed/side/neutral renders and local preview are synchronized
from the accepted model after validation. Checkpoint 010 remains archived.

The major side/rear pigment boundary, fine grain, collar/base highlights,
slit-edge finish and residual socket mismatch remain unresolved. Next inspect
pigment continuity separately from illumination, consulting the previous
rejected studies while preserving this accepted fixed-view result. The full
mission remains active and incomplete. No quota monitoring was performed.

## Iteration 013 — closer middle-body wood color

The owner confirmed that no pause is requested. Work continues at the fixed
54-degree camera. A conservative color grade lifts only the socket, stem and
collars, preserving the accepted grain layout, relief, lamps and all geometry.
Foot, lower-base, head and button atlas pixels remain exact. The saved/reopened
512-sample render reduces foreground RGB error from 7.6908 to 7.1865 /255, with
the clearest improvements in the socket and stem. This is a local color gain.

The broader grade is rejected because it worsens the foot. Four other material
and lighting studies are also rejected. Measured visibility shows that about
88.65% of the old pigment transition is on visible surfaces: a hidden-only fill
does not repair the side/rear patch. A continuous flat pigment plus fitted
diffuse lights improves the rear but loses too much fixed-view fidelity.
See [`iteration-013/assessment.md`](bishop-mission/iteration-013/assessment.md)
for the complete evidence, tradeoffs and five-category trial ratings.

Accepted scores are 96.11 / 84 / 85 / 77 / 77, working mean 83.82%, holistic
fixed-view range 75–85%. Geometry, UV controls, camera and material/light scope
pass independent reopened checks. Exported geometry is exact; evaluated UVs
vary by at most one float32 ULP within the existing tolerance. Checkpoint 012
is archived. The bishop fixed/side/clay views, exported mesh and both review
pages are refreshed together before the next iteration; checkpoint.json records
the canonical and preview verification.

The mission remains active and incomplete. The side/rear pigment discontinuity,
fine grain, collar/socket reflection shapes, base/button glints and slit-edge
finish still need work. Next target the collar reflection and surface detail
while preserving this color result. No quota monitoring or publishing occurred.

## Iteration 014 — collar and fine-grain studies preserve checkpoint 013

Work remains active; the owner explicitly confirmed no pause is requested.
Six collar isolations, five measured area-light placements with warm/neutral
and cooler spectral fits, and twelve localized reflector responses do not
produce a convincing collar improvement. A full trial with three fitted
additional lamps is rejected. Its reopened scope audit passes, but the added
complexity does not recover the reference's cream arcs.

Two saved/reopened fine-relief trials separate small pigment variations from
broad shading in the bump input. The gentler version marginally improves the
base glint while worsening other regions; the stronger version exaggerates
finish detail. Both retain the broad side/rear pigment patch, so both are
rejected. Independent audits prove the declared node/link and packed-height
scope, with geometry, UVs, color pixels, lights and camera unchanged.
See [`iteration-014/assessment.md`](bishop-mission/iteration-014/assessment.md)
for all five scores, raw comparisons, decisions and the next hypothesis.

The accepted score remains 96.11 / 84 / 85 / 77 / 77, mean 83.82%, holistic
75–85%. Model, review, fixed/side/clay renders and export remain the checked
checkpoint 013; no failed trial is promoted. That model is archived under
`history/bishop-mission-013`. The next pass will investigate continuous
height-dependent pigment around the turned body, preserving regional wood
tone rather than repeating the rejected flat-color or hidden-only fills.
The mission remains incomplete. No quota monitoring, publication or push.

## Iteration 015 — measured lower-body pigment and smoother continuation

The goal remains active; no pause is requested. Eight full material candidates
separate broad wood color, visible pigment, inferred continuation and fine
contrast. Height-only and angular-average fields lose too much reference
detail. Measured visibility and BSDF response improve the base, but early
versions replace uncertain highlights and flatten the rings. Preserving that
pigment and removing a log-detail clamp restores the lower-body contrast.
The clamp had affected about 17% of reliably observed texels.

The accepted version applies the improved pigment only below the upper head.
Head/button pixels above the smooth transition remain exact from checkpoint
013. Geometry, relief, lights, receivers and the 54-degree camera are unchanged.
The saved/reopened 512-sample render reduces shared foreground RGB error from
7.1865 to 5.9816 /255. Collars, stem, socket, base and foot all improve in that
diagnostic, supported by the fixed-view comparisons. The lower-body rear patch
is less abrupt, although grain direction and inherited tonal boundaries remain
visible. See [`iteration-015/assessment.md`](bishop-mission/iteration-015/assessment.md).

Scores are 96.11 / 84 / 86 / 78 / 77, mean 84.22%, holistic 75–85%.
Silhouette overlap is measured; the other ratings are visual estimates.
Original-white and original-black overlaps stay 97.786% and 96.661%.
The preserved upper head still needs texture continuity work. Fine grain is
soft, base/button glints are too concentrated, and the collar/socket and
slit-edge reflections remain imperfect. The full reconstruction is incomplete.

The new history audit verifies both successive atlas changes back to the strict
receiver/light source. Actual geometry, packed pixels, source registration and
camera remain checked. Export positions, normals, topology and dimensions are
exact; evaluated Boolean UV differences stay within the established one-ULP
tolerance. The bishop review and local preview are refreshed from the same
validated model; delivery hashes and checks are in iteration-015/checkpoint.json.
Checkpoint 013 remains archived. Next investigate fine grain and spatial
polish variation while preserving this color result. No quota monitoring,
subagents, publication or push occurred.

## Iteration 016 — base finish research; retain 015 and pause

The current iteration is finished. Grain-dependent polish barely changes the
base glint. Exact-surface light-receiver probes allow a broader reflector
without foot spill after correcting the receiver band, but still do not match
the reference pattern. A pigment-only diagnostic identifies a dark color-map
patch beneath the glare. Two localized per-channel pigment repairs lower RGB
error while retaining a visibly wrong yellow-green patch; both are rejected.
See [`iteration-016/assessment.md`](bishop-mission/iteration-016/assessment.md).

The public checkpoint remains **015**, including the checked Blender model,
atlas, fixed/side/clay renders, rotating export and HTML/local preview. Its
scores remain 96.11 / 84 / 86 / 78 / 77, working mean 84.22%, holistic 75–85%.
The 54-degree camera, original references, selected white candidate 3 and
gallery proportions are preserved. No failed experiment becomes a public
model choice. Source and public delivery hashes are recorded in iteration 016.

Toby directed the project manager to have current workers finish their ongoing
iteration and then pause because these pieces have plateaued. No further
modeling or render batch is pending; the goal is to be paused after this checked
record is committed. The full visual-match mission is incomplete. Resume only
on the owner's direction. No quota monitoring, subagents, publication or push.

## Iteration 017 — geometry phase: shoulder, stem and upper collar

On November 12 the owner started a new goal focusing on geometry. This supersedes
the earlier pause. The mission files remain unchanged. Work resumes from the
archived accepted checkpoint 015, with neutral renders and actual mesh
measurements separating shape from the inherited reference-derived pigment.

The accepted profile narrows the rear base shoulder without changing its
heights, retains a rounded lower turn, conservatively narrows the stem, and
lowers the small upper collar. Stronger base, stem and collar trials are
rejected: they respectively made the side angular, introduced a stem bulge,
and mistook the photographic shadow trough for the physical collar rim.
The remaining controls, button, slit, overall bounds and 54-degree camera stay
fixed. Exact receivers are rebuilt; UVs, packed pigments and lights are retained.

Original-white overlap improves from 97.786% to 98.590%; selected-white-3
overlap improves from 96.109% to 96.814%. Regional shoulder half-width error
falls from 9.559 to 2.167 native pixels. These measurements describe outline,
not internal shape. The actual upper-collar boundary moves from y=505.929 to
y=510.914; the larger trial's y=515.899 was too far into the reference shadow.

Scores are 96.81 / 86 / 83 / 77 / 72, working mean 82.96%, holistic 75–85%.
The mean declines because the retained pigment and lights fit the changed
surfaces less well. This is explicitly a geometry checkpoint, not a claim of
improved final finish. See [iteration-017/assessment.md](bishop-mission/iteration-017/assessment.md)
for side, neutral and enlarged comparisons, rejected trials and limitations.

Saved/reopened anatomy, independent geometry/material/light/camera scope,
render receivers, exported mesh and both bishop review interaction checks pass.
The current rotating mesh has 136,664 triangles. Fixed wood, neutral and side
views are regenerated from the same model. The overlay adds a Neutral/Boxwood
selector and opens neutral so shape can be judged without misleading pigment.
Delivery hashes are in iteration-017/checkpoint.json; checkpoint 015 remains
the rollback baseline. No native browser visual QA is claimed.

The geometry goal remains active and incomplete. Next examine the socket lip,
middle/lower collar cross-sections and slit edge/floor using actual projected
surface positions, not just brightness. Retained finish issues remain a later
phase. No mission, other piece, shared gallery setting or source is changed.
No quota monitoring, subagents, publication or push.

## Iteration 018 — correct the middle collar behind the head

The geometry goal continues from accepted 017. The apparent head-to-collar
bulge is identified by actual surface rays as the middle collar behind the
head, near control ring 54. An upper-collar-only proposal selected zero
displacement and is not accepted as an improvement. The middle collar is
narrowed and lowered together, changing only controls 49–56 while preserving
its projected front meridian. The measured front extent changes by less than
0.05 pixel. In the affected image region, original-white mean edge discrepancy
falls from 2.992 to about 1.585 pixels, with maximum error reduced from 12 to 5.

The saved/reopened final render overlaps the original white by 98.694% and
selected white 3 by 96.897%. The actual slit-interior boundary is separately
ray-projected: it already follows the white sources more closely than its
shading suggested, so the head, slit and button remain unchanged. The level
side view keeps a smooth collar form. Overall bounds, 54-degree camera,
references, registration and gallery proportions are preserved. See
[iteration-018/assessment.md](bishop-mission/iteration-018/assessment.md).

Scores are 96.90 / 87 / 83 / 77 / 72, mean 83.18%, holistic 75–85%.
Silhouette is measured; other ratings are subjective. The retained material
and lights are not refitted and remain unfinished. In particular, a saved
metadata flag claiming that albedo excludes lighting is not proof that the
inherited pigment is illumination-free; the scope report now says this clearly.

Independent geometry and receiver scope, actual closed-component/slit/button
anatomy, saved camera and export checks pass. Both bishop interaction harnesses
pass. The exported current mesh has 139,736 triangles. Wood/neutral fixed
renders, rotating mesh and side/rear views are rebuilt from the same saved
model. Checkpoint 017 is archived and the delivery hashes are recorded in
iteration-018/checkpoint.json. No native browser visual QA is claimed.

The geometry goal remains active and incomplete. Next examine the socket
lip-to-stem transition, lower-collar underside and residual button/foot edges,
separating source sampling from a real shape mismatch. Mission files, other
pieces, source images and shared sizing remain unchanged. No quota monitoring,
subagents, publication or push.

## Iteration 019 — recording audit; straighter foot wall

The owner supplied a blink recording showing the model still appearing swollen
against white candidate 3. It exposes the limitation of the earlier interior
assessment. The overall outlines are close and the selected reference's base
is slightly wider, so a global shrink is not supported. Ring-placement tracing
also tempers the first impression that the entire head descends too far: the
front junction positions are close, while perceived curvature and volume remain
unresolved. Outline agreement does not settle those internal forms.

Two collar-roll compression tests and a flatter inner-deck test are not
accepted. They sharpen the rims or change the level view without a convincing
improvement at the reference angle. Broad white studio diagnostics remove the
inherited pigment, relief and fitted reflectors without changing the saved
scene. See [iteration-019/assessment.md](bishop-mission/iteration-019/assessment.md)
for the owner's artwork-only recording crops, trials and remaining concerns.

The accepted local correction tightens the foot's upper rollover and extends
its straight wall, changing only controls 6-9 from checkpoint 018. All upper
anatomy, the groove, foot underside, camera, UVs, pigment and lights remain
unchanged. Evaluated diameter increases by approximately 0.036%, with height
unchanged; this is documented, not hidden by a camera or gallery scale change.
Original-white overlap is about 98.726% and selected-white overlap 96.928%.
The small improvement is not a solution to the broader appearance complaint.

Interior form is reassessed downward to approximately 80%, rather than raising
the old 87% simply because another iteration was completed. Scores are about
96.93 / 80 / 83 / 77 / 72, mean 81.79%, with overall resemblance roughly 70-80%.
Only silhouette is measured; other ratings are subjective and uncertain. The
wood and lighting remain unfinished. Remaining geometry concerns include
collar faces/undersides, apparent head fullness, socket/flare transitions and
the button's front rim. Examine actual surfaces separately from image shading.

The saved/reopened final model and exact receiver surfaces are checked, along
with closed anatomy, cut opening, direct button contact, UVs, unchanged packed
pigment/lights/camera and synchronized exported mesh. Fixed wood/neutral and
side/head/rear views, viewer and review are regenerated together. Native browser
QA is not claimed; Node interaction checks and the owner's recording are the
available page evidence. Checkpoint 018 remains the rollback source.

The geometry goal remains active and incomplete. No mission file, original,
source registration, other piece or shared gallery default is changed. No quota
monitoring, subagent, push or external publication.

## Iteration 020 — fit the button rim and preserve direct contact

First-hit surface labels reveal that the button's front boundary was at row
278, below the approximately 270 edge in white candidate 3. The original white
also supports the shallower boundary. The accepted shallow lens reaches row
270 without changing the button radii, overall height, camera or registration.
Only the upper half of the head meridian extends smoothly into its underside;
all body controls through ring 85, including the widest head and lower anatomy,
remain exact. See [iteration-020/assessment.md](bishop-mission/iteration-020/assessment.md).

The first rim lift is rejected: its cup underside contacts too narrowly and
fails the unchanged broad-contact criterion. A full head-tip extension passes
anatomy but perturbs the outline unnecessarily. The chosen localized extension
retains the original-head outline while seating the shallow button directly.
Actual contact width is about 85.15% of button width, with one gap-free external
transition and no cylindrical neck. Button height/width is about 0.259, down
from 0.413. The deep slit, solid floor and original cutter are preserved.

The final render overlaps original white by 98.744%, selected white by 97.005%
and original black by 97.785%. Internal front-arc landmarks are separately
checked against the reference, with a stated interpretation uncertainty of
about +/-3 comparison pixels. Scores are approximately 97.01 / 81 / 83 / 77 / 72,
mean 82.00%, overall 70-80%. This is a local button improvement; the larger
swollen-form concerns and inherited material/lighting defects remain unresolved.

Saved/reopened controls, actual anatomy, combined-surface neck regression,
render receivers, UVs, packed pixels, fixed camera and export are checked.
The junction checks now extend to its actual height and still detect the
historical bad seat. Current fixed/neutral and head/side/rear renders, rotating
mesh and review are rebuilt together. Checkpoint 019 is archived. Node page
checks are used; native browser inspection is not claimed.

The geometry goal stays active and incomplete. Mission files, source images,
registration, shared gallery defaults and other pieces are unchanged. No quota
watcher, subagent, push or external publication.

## Iteration 021 — a continuous stem/socket join

Actual surface rays expose a small outward height reversal at the socket top:
the profile dips from the stem, then rises into an extra inner ridge. The
accepted correction lowers three crest controls (28-30), removing that trough
while preserving the stem seating control, every radius and all other anatomy.
The measured reversal decreases from about 0.567 original profile units to zero.
The originals and selected white 3 support a simpler rolled join, but their
cross-section is not precisely recoverable. See
[iteration-021/assessment.md](bishop-mission/iteration-021/assessment.md).

A raised-root test is rejected because it moves the seating point. Lifting
the lower-collar underside also fails the comparison: its original-white
row-edge error increases from about 2.90 to 4.74 comparison pixels. Neither
experiment replaces current geometry. The collar stack, head, shallow button,
slit, stem, outer socket wall, flare and foot retain checkpoint 020 controls.

Final outline overlaps are about 98.7425% original white, 97.0048% selected white
and 97.7850% original black, essentially unchanged. This acceptance concerns
the internal socket curvature. Scores remain about 97.00 / 81 / 83 / 77 / 72,
mean 82.00%, holistic 70-80%. The uncertain interior rating is not increased
for a small local correction. Apparent head fullness, collar faces/undersides
and socket/flare relationships remain under investigation; inherited wood and
lighting remain unfinished.

Saved/reopened scope, anatomy, direct button contact, historical neck regression,
receiver surfaces, UVs, pigment, lights, unchanged bounds and 54-degree camera
are checked before delivery. Fixed/neutral, side/head/rear, rotating mesh and
review are synchronized. Broad unfitted neutral side views and measured socket
meridians accompany the ordinary fixed-view evidence. Checkpoint 020 is archived.

The geometry goal remains active and incomplete. Mission files, references,
registration, other pieces and gallery settings are untouched. Native browser
inspection is not claimed; page-code interaction checks are used. No watcher,
subagent, push or external publication.

## Iteration 022 — a distinct middle-collar underside

The middle rim barely overhung its neck at the reference view: evaluated
front-meridian rays measured only 0.197 comparison pixels. Narrowing only neck
controls 49 and 50 increases this to 2.435 pixels while moving the foremost
edge up just 0.352 pixels. Every height, the outer rim and upper-deck controls,
other collar crests and all remaining controls stay exact. The inner joining
surface toward the lower collar follows the changed controls through subdivision.
The rounded lip now separates more clearly in fixed and true-level views.
See [iteration-022/assessment.md](bishop-mission/iteration-022/assessment.md).

Three fuller lower-head interpretations are rejected. They preserve the front
projection and nearly identical outline scores, but introduce an unsupported
band or ridge in level views. Even a convex control polygon does not guarantee
that the evaluated surface has the right curvature. The accepted head, shallow
button and slit remain unchanged. The white-source slit boundary remains close;
diagnostic opposite-color rotations do not establish a different source pose.
The dark black-source bands are not treated as reliable cut edges.

Final outline overlaps are 98.7425% original white, 97.0048% selected white and
97.7850% original black, unchanged from checkpoint 021. The interior-form
working estimate rises modestly to 82% for the distinct middle lip. Scores are
about 97.00 / 82 / 83 / 77 / 72, mean 82.20%, holistic 70-80%. Only outline overlap
is measured; the other ratings remain subjective and uncertain. Pigment, grain
and lighting are inherited and unfinished. The wider apparent-volume concern
is not declared solved by this local correction.

Saved/reopened scope, actual anatomy, direct button contact, deep slit,
historical neck regression, exact render receivers, UVs, packed pixels, fixed
camera and export are checked. Bounds are unchanged. Current wood/neutral,
head/side/rear, rotating mesh and review are rebuilt from the same model; an
unfitted neutral level comparison supplements the fixed view. Checkpoint 021
is archived, and the trial evidence records both accepted and rejected findings.

The geometry goal remains active and incomplete. Mission files, source images,
registration, candidate choices, other pieces and shared gallery settings are
untouched. Native browser inspection is not claimed; Node page-code checks are
used. No quota watcher, subagent, push or external publication.

## Study 023 — reject base and stem fits that worsen the physical form

Checkpoint 022 remains public and accepted. Five saved/reopened geometry trials
are rejected; see [study 023](bishop-mission/iteration-023/assessment.md). Two
rounded base profiles remove a measured inward flex but worsen the original
outline. A height-refitted version improves original-white overlap to 98.7567%
while introducing a worse bend. A smoother height family offers no convincing
fixed-view gain. None justifies replacing the accepted base.

A local stem fit improves all three outline overlaps, including 98.7733% for
the original white. Its true-level and fixed-view crops reveal an unwanted
lower-stem bulge, so it is also rejected. An earlier proxy-only check confirmed
that the physically uppermost stem controls do not generate this particular
elevated contour. The next fit must constrain a smooth meridian and identify
the actual contour-generating surface, rather than optimizing isolated radii.

The public model, render, neutral view, mesh, pages and 54-degree camera remain
byte-identical to checkpoint 022. Its working scores remain unchanged at
approximately 97.00 / 82 / 83 / 77 / 72. Geometry and finish remain incomplete;
the owner's apparent-fullness concern is not dismissed by high outline scores.
Original source registration, mission statements, other pieces and side-gallery
choices are preserved. Rejected trial evidence and reproduction scripts are
recorded, without publishing those alternatives or claiming native browser QA.

## Checkpoint 024 — a narrower stem with the root and base preserved

Actual contour rays distinguish the stem from the rear base behind it. This
explains why fitting the entire exposed region as stem in study 023 produced
an unwanted lower swelling. The accepted change narrows only radii 34–36;
all heights and other controls remain exact from checkpoint 022. A subpixel
rear-shoulder proposal is omitted. See the [024 assessment](bishop-mission/iteration-024/assessment.md).

Average original-white edge error in the exposed-stem rows falls from 3.646
to 1.229 comparison pixels. The stem/base crossover worsens slightly, 2.375
to 2.625 pixels; the rear-base region is unchanged. Plain level views show a
slimmer taper without the rejected lower-stem bulge. The base becomes visible
two sampled rows earlier because the stem is narrower, not because it moved.

Final outline overlaps are 98.7742% original white, 97.0347% selected white 3
and 97.8272% original black. Working scores are approximately
97.03 / 82 / 83 / 77 / 72, mean 82.21, holistic 70–80%. Only outline is measured.
The local improvement does not justify increasing the broad interior-form
estimate or claiming the whole-image fullness concern is solved. Material,
grain and lighting remain inherited and unfinished.

The final saved/reopened model passes scoped control, actual anatomy, slit,
button contact, receiver, UV, packed-pixel, camera and export checks. Its fixed
wood/neutral, head/side/rear, rotating mesh and bishop review are synchronized;
Node viewer/review checks pass. Bounds are unchanged. Rollback checkpoint 022,
mission statements, originals, registration, other pieces and gallery settings
are preserved. No native browser QA, quota watcher, workers, push or publication
is claimed. The geometry goal remains active and incomplete.

## 025 · Shared queen and king base

The bishop uses all 39 base rings and the first stem support from queen 033
and king 017 at one uniform scale. Compared with 024, its foot is 1.48%
wider and its height 0.91% shorter. Five editable trials separate the effect
of the new turning from the upper refit at the saved 54-degree camera.
The final stem, collars and mitre fit the original more closely in their
respective outline regions. The lower groove and rear flare fit less closely.
Original-white silhouette overlap falls from 98.77% to 97.39%. The
equal-diameter side profiles, fixed comparisons, trial measurements and
reproduction settings are in [iteration 025](bishop-mission/iteration-025/assessment.md).
The wood and lighting remain unfinished. Bishop 024 is archived for rollback.

## 026 · Bishop height in the owner's lineup

On checkpoint 025's board ruler the bishop moved from 81.94% to 74.48%
of the king's height. The queen measures 83.29% on that same ruler.
The new foot measures 1.93652 model units and the total height is 4.13599.
All 40 base rows preserve the queen and king turning at one uniform scale.
Most of the remaining height reduction comes from the exposed stem.

Five saved variants were compared with the owner’s side screenshot and
both registered white references. The accepted version matches the side
outline at 98.16%, with a 0.48-pixel mean edge error. At the fixed 54°
camera its original-white overlap is 85.63%, down from 97.39%. The head
and front collar rims sit lower. The open slit, flush button, UVs, saved
camera and mesh export passed verification. Wood and lighting are inherited.
Bishop 025 is archived. [Lineup, measured tradeoffs and checkpoint](bishop-mission/iteration-026/assessment.md).

## 027. Refit at the shorter height

The bishop keeps its 026 height of 4.135986328125, the 025 lineup ruler and
the saved 54° camera. Original-white outline overlap rose from 85.63% to
95.72% after widening the shared lower turning, raising the three collars,
and reshaping the stem and mitre. The real saw now follows the original
stroke within 0.93 pixels over 14 sampled rows. A localized pigment repair
removes the stripe from the previous slit. The physical side height stays
at 74.48% of the king. The button still projects too low, the groove sits
too low and the level mitre is broader than the earlier side guide.
[Fixed-view images, level profiles and remaining errors](bishop-mission/iteration-027/assessment.md).

## 028. Restore the original-view reference fit

The owner rejected checkpoint 027 because its button and upper body missed the original at 54°. The active bishop returned to 024, commit `6d6944c`, including its original camera, wood, fixed renders and rotating mesh. This is the starting point for retrying the height. [Restored reference fit](bishop-mission/iteration-028/assessment.md).

## 029. Stockier bishop at the original camera

Compared with restored bishop 024, the waist is 9.8% wider, the socket-to-collar span is 12.5% shorter and overall height is 0.68% lower at the original foot width. The saved 54° view reaches 99.111% outline overlap with original white. The three collar arcs, through-slit and foot groove were checked independently. [Assessment and side profiles](bishop-mission/iteration-029/assessment.md).
