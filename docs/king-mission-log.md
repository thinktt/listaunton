# King mission log

## Mission-statement cleanup — 2026-11-12

The owner requested static goals with progress recorded separately. The
piece mission now preserves the original full visual-match objective and
five-category standard. This is a documentation migration, not a new model
iteration, fresh assessment, or change to the accepted model. The complete
pre-cleanup statement is available in Git at `fb75902169d17a993280dbd593f8d5163204e592:MISSION-KING.md`.

### Information moved out of the mission

Former drafting snapshot (historical, not the current accepted hash):

- Model SHA-256 at drafting: `44f651f674dcfeab2b9837cf4640017e0d72aaeab4f024913601a07f674a5300`.

The former statement directed readers here for executed full-material scores.
The recorded construction was a turned body plus a separate intersecting
beveled cross, not a boolean-fused mesh. Preserve that construction unless a
later deliberate revision is validated.

The statement also carried a snapshot saying the queen goal was paused.
Activation and pause state belong to the relevant goal, not this piece's mission.

Future checkpoints, scores, defect lists and phase completion belong in this
log and the iteration evidence. Change the static goal only at the owner's
direction. Apply [the shared mission standards](../MISSION-SET.md).


## 2026-11-05 — checkpoint 001: 54-degree wood baseline

The owner activated MISSION-KING.md and explicitly removed the need for watchers
or subagents. Work is confined to the king. Another chat is working on the queen;
its edits and commits are independent.

The king started as the accepted 52-degree clay study. The existing 54-degree
projection is a documented refit of that same geometry, with the base diameter
preserved; it supplies the requested camera assumption. The old current king is
archived intact in history/king-before-54-mission. All six projection candidates,
their meshes, renders and sizing inputs remain historical alternatives.

The first accepted checkpoint adds a real wood BSDF, packed diffuse pigment,
fine reference grain, shallow surface relief, separated diffuse and reflection
lights, and a modest local correction to the broad platter. Four profile rings
rise by 0.01–0.07 model units; the outer silhouette and height/base ratio remain
essentially unchanged. The cross and body remain separate closed components.

### Current assessment

| Metric | Score |
| --- | ---: |
| High-resolution silhouette IoU | 97.851% |
| Interior shapes/details | 80% |
| Wood color | 68% |
| Grain and surface texture | 62% |
| Lighting/reflections | 45% |
| Equal-weight working mean | 70.570% |

Original-sprite IoU is 96.791%. A holistic visual assessment is approximately
60–70%, not a claim that the piece is almost finished. Only silhouette is a
measured percentage. The other scores are subjective and deliberately separate
from the outline metric. The fresh baseline uses the mission's fixed alpha/RGB,
largest-component, hole-filled mask; its scores differ from older reports that
did not fill holes. Original cross clipping remains missing evidence.

### Material and experiments

The built-in image generator produced a non-destructive diffuse pigment source
from selected black candidate 1. Its prompt, source hash and output are recorded
in assets/king/materials/derived-pigment-01-generation.json. It removed major
highlights but invented grain that was too coarse. A shader-space local average
reduces that invented detail; a bounded luminance ratio from the actual selected
reference supplies finer grain. This is surface pigment, not an emission beauty
render or a camera-facing image replacement. Broad reference lighting is excluded
from the fine transfer, though some high-frequency reflection edges can remain.

The portable atlas bakes pigment only. Cycles still calculates reflections,
shadows and surface response on actual geometry. The rotating viewer uses the
same atlas and evaluated mesh with approximate real-time lighting. Its neutral
mode remains available. Side, rear and reopened beauty renders were inspected.

Strong surface-directed lights and a weaker variant were both rejected because
they brightened the wrong regions. An initial atlas export was also rejected:
an edit-mode operation invalidated a UV-layer handle. Reacquiring the layer and
checking disjoint island bounds fixed the overlap before promotion. All trial
scores and useful visual evidence are in iteration-001; rejected models are not
offered in the public controls.

### Validation and reproduction

The accepted model has 68,492 triangles in two closed, positive-volume components.
The viewer export has 40,930 position/normal/UV vertices, with exact triangle-corner
round trips, finite attributes and unit normals. The saved orthographic camera is
54.0000008 degrees. Its browser camera regression differs by less than 0.000051
pixels across 506 sampled vertices, including viewport changes. Viewer controls
were checked with the actual page's DOM/WebGL harness; no native browser screenshot
validation is claimed.

Packed texture pixels survive saving/reopening exactly. A reopened beauty render
has a maximum 1/255 channel difference and mean 0.00000875/255 from the first render;
alpha is identical. Atlas versus pre-bake shader mean foreground RGB difference
is 0.525/255. Original and selected reference pixels and registration are unchanged.
The side gallery still uses its original 54-degree sizing study and owner defaults.

Rebuild the atlas from the tracked pre-atlas model using scripts/king/bake_pigment.py
and iteration-001/reproduction.json. Use scripts/king/export_mission.py for current
mesh/camera/closure validation, scripts/king/audit_mission.py for fixed-reference
evidence, and scripts/king/build_viewer.py plus check_viewer.cjs for the page.
The older build_king.py/profile.json remain the historical 52-degree clay builder;
do not run them over the current accepted king. Later geometry edits should preserve
the current model's materials, camera and UVs, then export and re-render all views.

### Review page checkpoint

The owner requested a visible page update at every accepted checkpoint. The king
main page now opens Reconstruction, which provides Reference overlay, Rotate
model and Side comparison tabs. The side guide is explicitly an imagined view;
the actual model profile is uniformly aligned at the foot and base width, with
no height stretching. Candidate and historical projection controls remain.

The current Blender validator, exact viewer camera/texture and interaction
harness, five candidate-page checks, whole-set controls, source integrity,
model-site checks and historical king projection preservation all pass. The
local Windows preview contains the same accepted king pages, material, geometry
and renders. The reference images and other pieces' pages remain unchanged.

### Remaining defects and next hypothesis

- Cross upper bevels and its recessed seat still differ. The clipped top limits certainty.
- Collar edges remain shelf-like; the socket transition and foot are too rounded.
- The platter is closer in clay, but its characteristic front reflection is absent.
- Wood is too uniform. Broad base grain marks and regional dark patches are weaker
  than in the selected reference; grain is still partly inferred.
- Highlights on the cross, collar lips, socket and foot are too weak or misplaced.
  Base highlights have the wrong shape and contrast.
- Hidden surfaces still transition to procedural horizontal grain. The material
  is usable around the piece, but side inspection reveals the finish change.

Next: make the hidden-surface grain continuous with the visible pigment, then
isolate single reflector responses and reconsider platter/cross curvature before
adding more lights. Keep the fixed camera and original silhouette priority.
The goal remains active and incomplete.

## 2026-11-05 — checkpoint 002: recovered wood figure and textured reflections

The accepted model keeps checkpoint 001 geometry and camera. It adds two
confined crown reflectors, an estimated diffuse pigment field from the actual
BSDF light response, and shallow grain relief in the varnish. The base's broad
wood marks and regional stem/collar tone now agree more closely with black 1.
The selected source and original Lichess sprite are unchanged.

| Metric | Checkpoint 001 | Checkpoint 002 |
| --- | ---: | ---: |
| High-resolution silhouette IoU | 97.851% | 97.849% |
| Interior shapes/details | 80% | 80% |
| Wood color | 68% | 80% |
| Grain and surface texture | 62% | 76% |
| Lighting/reflections | 45% | 54% |
| Equal-weight mean | 70.570% | 77.570% |

Original-sprite IoU is 96.795%; the tiny silhouette change is edge sampling and
subdivision roundoff, not a change to editable geometry. Holistic assessment is
70–80%. The silhouette metric is measured; the other values are subjective.
The model is still visibly short of the reference. Cross bevel curvature,
cross seating, collar edges, base reflections and hidden-surface finish remain.
The hidden finish transition is more visible after improving the front, and
is explicitly unresolved. White-piece material is not assessed here.

All trials, including failed mirrored grain and pigment input conversion, are
scored in iteration-002/scores.json. The first estimated pigment was rejected
because PNG pixels were decoded twice and an alpha threshold created mottling.
The corrected estimate is a real surface pigment under live BSDF lighting;
residual source shading and single-view ambiguity remain limitations.

Saved texture pixels, reopened render, exact editable controls/camera, closed
components, viewer projection and affected site controls passed. Native UI
inspection is not claimed; interactions use the actual page's DOM/WebGL harness.
The accepted renders, mesh, texture and side comparison are synchronized in the
king reconstruction page. Reproduction and the remaining issues are documented
in [iteration-002/README.md](king-mission/iteration-002/README.md).

The next geometry target is the cross's cap and upper bevel curvature. Preserve
this material and the 54-degree framing, and re-examine both original and selected
reference before editing. The goal remains active and incomplete.

## 2026-11-05 — checkpoint 003: rounded cross cap and localized finish

The cross cap now curves like the reference, with smoother carved bevels. The
initial lowered curve was rejected; the accepted revision preserves center and
overall height while lowering the ends. Body geometry, base diameter and the
54-degree camera stay fixed. Cross-only light and pigment adjustments remove
the broad pale roof patch and restore displaced wood figure. V4 preserves body
atlas pixels exactly.

| Metric | Checkpoint 002 | Checkpoint 003 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.849% | 97.826% |
| Interior form | 80% | 82% |
| Wood color | 80% | 81% |
| Grain and surface texture | 76% | 77% |
| Lighting and reflections | 54% | 55% |
| Equal-weight mean | 77.570% | 78.565% |

Original-sprite IoU is 96.824%, up from 96.795%. Only silhouette is measured;
the other scores are subjective, and the holistic range remains 70–80%.
Cap and arm glints remain too thin/regular, cross seating and collar profiles
differ, base highlights are misplaced, and side-view material transitions remain
conspicuous. This checkpoint is a modest improvement, not a finished match.

Saved/reopened texture and beauty checks, body/camera preservation, closed mesh,
exact viewer export and affected page controls pass. The king main page and
local preview are synchronized with this accepted model. See
[iteration-003/README.md](king-mission/iteration-003/README.md) for trial scores,
evidence, reproduction and limitations. No native browser inspection is claimed.
Next target: base reflection shape, without altering fixed registration or the
accepted cross. The goal remains active and incomplete.

## 2026-11-05 — checkpoint 004: base grain and a cleaner foot groove

The accepted base has clearer wood figure and a smaller, right-shifted reflection
instead of the previous broad central white wash. Five lower profile heights
narrow the foot groove and remove a discovered local profile self-intersection.
All radii, other controls, physical height/base width, atlas UVs and the fixed
54-degree camera are preserved. Exact derived receivers separate the base
lighting from the upper body; the closed control is exported to the viewer.

| Metric | Checkpoint 003 | Checkpoint 004 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.826% | 97.820% |
| Interior form | 82% | 83% |
| Wood color | 81% | 82% |
| Grain and surface texture | 77% | 78% |
| Lighting and reflections | 55% | 58% |
| Equal-weight mean | 78.565% | 79.764% |

Original-sprite IoU is 96.833%, previously 96.824%. Only IoU is measured; other
ratings are subjective. Holistic assessment is 73–82%. The remaining base glint
is too tall and the foot crescent is too weak and low. Cross/collar reflections,
cavity contrast and the obvious hidden-surface pigment transition remain.
These are accepted improvements, not a completed match.

Saved texture/reopened beauty, exact edit scope, derived receivers, closed
components, export and page controls pass. See
[iteration-004/README.md](king-mission/iteration-004/README.md) for trial scores,
reproduction, validation evidence and limitations. The king reconstruction and
local preview are synchronized at this checkpoint. No native UI inspection is
claimed. Next: foot crescent and remaining base glint shape. Mission incomplete.

## 2026-11-05 — checkpoint 005: isolate the lower base reflection

The lower glint is smaller and correctly centered after removing direct spill
from the upper-base reflector. Four exact derived receivers preserve the same
closed geometry. All UVs, pigment pixels, dimensions and the 54-degree camera
remain unchanged; the export is byte-identical to 004. The foot experiments
were rejected and the accepted foot geometry/lights retained.

| Metric | Checkpoint 004 | Checkpoint 005 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.820% | 97.820% |
| Interior form | 83% | 83% |
| Wood color | 82% | 82% |
| Grain and surface texture | 78% | 78% |
| Lighting and reflections | 58% | 60% |
| Equal-weight working mean | 79.764% | 80.164% |

Original IoU remains 96.833%; the holistic range remains 73–82%. Only IoU is
measured. The lower shine is now slightly undersized, the foot crescent and
upper glints still differ, and the side/rear pigment transition remains obvious.
A receiver illumination cutoff is visible in clay despite exact geometry.
This is a modest accepted refinement, not a finished match.

The saved/reopened and full reproduced renders differ by at most 1/255 with
identical alpha. Geometry/material scope, receiver fidelity and export pass.
All trial decisions, checks, reproduction and remaining issues are in
[iteration-005/README.md](king-mission/iteration-005/README.md). Site/model, candidate, whole-set and historical projection checks pass. The
repository and local-preview DOM/WebGL checks pass; native UI inspection is
not claimed. The synchronized king review and local preview expose the accepted checkpoint. Next: hidden
wood continuity, then the foot using isolated-light diagnostics. Goal incomplete.

## 2026-11-05 — checkpoint 006: continuous inferred wood

The hidden turned surfaces now use a generated unlit grain source, with a wider
blend on grazing surfaces. This replaces the smeared rear wood and softens the
side-base transition. Central front pigment and cross atlas remain retained;
side-facing collar/base texels change. Geometry, original UVs/attributes, relief,
lighting and the 54-degree camera are exact; the viewer mesh is byte-identical.

| Metric | Checkpoint 005 | Checkpoint 006 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.820% | 97.820% |
| Interior form | 83% | 83% |
| Wood color | 82% | 82% |
| Grain and surface texture | 78% | 79% |
| Lighting and reflections | 60% | 60% |
| Equal-weight working mean | 80.164% | 80.364% |

Original IoU remains 96.833%; the holistic range remains 73–82%. Only IoU is
measured. The small subjective grain gain reflects continuity and detail at
oblique angles; unseen grain is interpretation. Lighting and carved-form defects
remain, along with a warmer side patch, cross-side finish and projected relief.

Saved/reopened and fully reproduced beauty differ by at most 1/255; reproduced
atlas pixels match exactly. Geometry/material scope, exact receivers and export
pass. See [iteration-006/README.md](king-mission/iteration-006/README.md) for trial
scores, prompt, evidence, final checks and synchronization. All affected site,
model, candidate, set, projection and repository/local-preview interaction checks
pass. All 34 king preview files are hash-verified. Native UI inspection
is not claimed. Owner requested pause after the completed checkpoint; do not
begin another iteration until resumed.

## 2026-11-12 — checkpoint 007: broader, aligned foot crescent

The owner resumed the king mission after checkpoint 006. The accepted foot
shoulder slopes upward into its groove and catches a broader reflection.
The final height correction aligns the brighter crescent with the selected
reference. Local varnish and one fitted area source support the new shoulder.
See [iteration-007/README.md](king-mission/iteration-007/README.md).

| Metric | Checkpoint 006 | Checkpoint 007 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.8197% | 97.8171% |
| Interior form | 83% | 84% |
| Wood color | 82% | 82% |
| Grain and surface texture | 79% | 79% |
| Lighting and reflections | 60% | 62% |
| Equal-weight working mean | 80.3639% | 80.9634% |

Original IoU is 96.8335%. IoU is measured; other category scores are subjective.
The holistic range is 74–83%. Foot glints remain too smooth and the groove,
base glints, cross seating, collars, cavity contrast and hidden finish need
further work. Rejected pore/sharper-polish trials are retained as evidence.

Scope, receiver regeneration, closed components, packed textures and exact
export pass. Reopened and independently rebuilt renders have identical alpha
and maximum channel difference 1/255; rebuilt mesh bytes match exactly.
The king review and local preview are synchronized. King/candidate interaction,
site/model and historical-projection checks pass. A pre-existing knight sizing
metadata mismatch stops the whole-set check, documented against the task-start
commit in iteration-007. Native browser inspection is not claimed.

Next: isolate socket/collar glossy responses and improve their placement and
warmth. Preserve the current foot placement for a later grain-relief study.
The goal is active and incomplete. No watchers or subagents were started.


## 2026-11-12 — owner pause after diagnostic 096

Finished the current socket/collar illumination diagnostic and saved its
renders, source checks and findings in
[iteration-008/README.md](king-mission/iteration-008/README.md).
The broad front source is responsible for most of the socket's doubled white
streak; the upper source contributes repeated pale collar crescents. Residual
pigment shading remains visible when both are disabled.

No new model is accepted. Checkpoint 007, its scores, fixed 54-degree camera,
review page and local preview remain unchanged. Its nine principal assets are
archived exactly under `history/king-mission-007`. The proposed socket receiver
and targeted warmer reflections have not been implemented. No new render
batches or model trials will begin until the owner resumes the mission.

The owner has requested the active goal be paused. The mission remains
incomplete; no watchers or subagents were started.


## 2026-11-12 — checkpoint 009: separated socket reflections

The owner resumed the king mission. Trial 103 replaces the broad pale socket
streak with four local real reflectors forming warmer, separated left/right
glints. All closed geometry, UVs, float attributes, pigment/relief, physical
bounds and the 54-degree camera remain exact from checkpoint 007. The socket
is now a fifth exact receiver; regeneration preserves its routing.

| Metric | Checkpoint 007 | Checkpoint 009 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.8171% | 97.8174% |
| Interior form | 84% | 84% |
| Wood color | 82% | 82% |
| Grain and surface | 79% | 79% |
| Lighting / reflections | 62% | 63% |
| Equal-weight working mean | 80.9634% | 81.1635% |

Only IoU is measured; tiny outline changes are sampling, not geometry gains.
Original IoU is 96.8338%; the holistic estimate remains 74–83%. Socket crop
RGB MSE drops about 62%, but the inner seam, gray pigment band and patchy
glint shape remain. The upper collars and other previously listed defects
are unfinished. See [iteration-009/README.md](king-mission/iteration-009/README.md)
for trial decisions, all five scores, regional tradeoffs and reproduction.

Reopened and independently rebuilt renders agree within 1/255 with identical
alpha. Exported geometry and camera bytes match 007; scope, receiver
regeneration and closed-component checks pass. King review, side comparison,
viewer and all 34 local preview files are synchronized. King/candidate,
site/model and historical projection checks pass. The shared whole-set check
still has the documented pre-existing knight sizing mismatch; those shared
files are unchanged. Native browser screenshot inspection is not claimed.

Next: the inner socket seam and residual pigment band, then collar reflections.
Preserve the accepted outer glints and foot. The goal is active and incomplete;
no watchers or subagents were started.


## 2026-11-12 — checkpoint 010: inner socket reflection

Accepted trial 113 restores more of the inner socket line with two narrow,
warm area reflections confined to an exact sixth receiver. Closed geometry,
UVs, float attributes, v6 pigment, material and the 54-degree camera remain
exact from 009. Old lights retain their settings and coverage. Broad pigment
and unrestricted reflection experiments were rejected; a small center pigment
correction is deferred. See [iteration-010/README.md](king-mission/iteration-010/README.md).

| Metric | Checkpoint 009 | Checkpoint 010 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.8174% | 97.8174% |
| Interior form | 84% | 84% |
| Wood color | 82% | 82% |
| Grain and surface | 79% | 79% |
| Lighting / reflections | 63% | 64% |
| Equal-weight working mean | 81.1635% | 81.3635% |

Only IoU is measured; the other scores are subjective. Original IoU is
96.8338%, and the holistic range remains 74–83%. The inner-seam crop error
falls about 42%, with essentially unchanged color in its center. The full
image still has pale collar bands, patchy socket glints, imperfect base/foot
reflections and unresolved form/finish differences.

Saved/reopened and independently rebuilt renders agree within 1/255 with exact
alpha. Mesh and camera exports match 009 byte-for-byte. Scope, receiver and
regeneration checks pass. The king review and all 34 local preview files are
synchronized; king/candidate, site/model and historical projection checks pass.
The whole-set test retains its documented pre-existing knight sizing failure;
native browser screenshot inspection is not claimed.

Next: isolate the collar reflection sources. Preserve the accepted foot/socket
and the unchanged source art. The goal remains active and incomplete; no
watchers or subagents were started.


## 2026-11-12 — checkpoint 011: separate collar reflections

Accepted trial 117 using its verified fresh saved-file render. The regular pale
collar bands are reduced and the lower collar has warmer, separated glints.
Three exact collar receivers bring the total to nine; closed geometry, UVs,
float attributes, v6 pigment/material, physical bounds and the fixed 54-degree
camera remain exact from 010. All old light settings remain exact. No shadow
omission or near-field reflector experiment is accepted.

| Metric | Checkpoint 010 | Checkpoint 011 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.8174% | 97.8174% |
| Interior form | 84% | 84% |
| Wood color | 82% | 82% |
| Grain and surface | 79% | 79% |
| Lighting / reflections | 64% | 66% |
| Equal-weight working mean | 81.3635% | 81.7635% |

Only IoU is measured; other scores are visual judgments. Original IoU remains
96.8338%; holistic estimate is 75–84%. Collar foreground RGB error drops about
45%, but missing left highlights and gray pigment bands remain. Later close-light,
actual-normal and one-light shadow-omission trials were rejected visually.
See [iteration-011/README.md](king-mission/iteration-011/README.md).

A tiny socket glint made the initial partition-only and fitting-session images
fail the 1/255 maximum check. Untouched normals are byte-identical; fixed-sample
diagnostics agree to 2.15e-6 linear. The verified fresh saved-file render is used
for acceptance and agrees with the independent rebuild within 1/255. The failed
checks and original fitting image remain evidence; tolerances were not loosened.

Geometry/export, receiver scope/regeneration and source preservation pass.
The review, rotating viewer, fixed/side assets and all 34 existing preview files
are synchronized. King/candidate, site/model and historical projection checks
pass; the known whole-set knight sizing failure remains documented separately.
Native browser screenshot inspection is not claimed.

Next: separate collar pigment bands from local curvature mismatches at the
missing left glints, preserving this best result. The goal remains active and
incomplete. No watchers/subagents or push/publication were started.


## 2026-11-12 — checkpoint 012: middle collar and continuous join

Accepted trial 135 using standardized fresh render 140, repeat 141 and independent
rebuild 136. Six controls round the middle edge and repair a crossing that was
already present in checkpoint 011. Two existing middle-collar lights now produce
better placed, gentler glints. Wood pigment, relief, finish, overall dimensions and
the fixed 54-degree camera remain unchanged. See
[iteration-012/README.md](king-mission/iteration-012/README.md).

| Metric | Checkpoint 011 | Checkpoint 012 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.8174% | 97.8258% |
| Interior form | 84% | 85% |
| Wood color | 82% | 82% |
| Grain / surface | 79% | 79% |
| Lighting / reflections | 66% | 67% |
| Equal-weight working mean | 81.7635% | 82.1652% |

Original IoU is 96.8464%; only overlap is measured. Other
scores are subjective, with a holistic range of 75–85%. The broad/orange and
neutral-removal pigment experiments, stronger light fits and fixed-sampling
experiment are rejected. Upper highlights, pigment bands, uneven finish, base and
socket reflections, cross seating and inferred hidden wood remain unfinished.

The canonical fresh-render path repeats and matches the independent rebuild within
1/255 with exact alpha and mesh export. A different entry point still changes a
tiny socket glint; raw rendering also shows the discrepancy. Failed checks and
the unresolved context sensitivity are documented, not relabeled as passes.

Full evaluated-section inspection finds no crossings; closed components, exact
scope, receivers/regeneration and export pass. Review, side views, rotating viewer
and all 34 Windows preview files are synchronized. King/candidate, site/model
and historical-projection checks pass. The known whole-set knight metadata failure
remains separate. The goal is active and incomplete; no watcher, subagent, push or
publication was started.


## 2026-11-12 — checkpoint 013: upper collar curve and reflections

Accepted trial 151, independently reproduced as 152 from the archived checkpoint
012. Three upper-collar control heights and two existing local lights improve
the left patch and right glint placement. All radii, other geometry, wood
material, overall dimensions and the fixed 54-degree camera are preserved.
The brighter/doubled light studies and the obstructed larger curve are rejected.
See [iteration-013/README.md](king-mission/iteration-013/README.md) for evidence.

High-res IoU is 97.8258%; original IoU is
96.8464%, both unchanged. Subjective scores: interior 85,
color 82, grain 79, lighting 69; working mean 82.5652% and
holistic range 75–85%. The full mission remains active and incomplete.

Scope, receivers/regeneration, closed components, saved-file reproduction and
exact mesh export pass. Review and all 34
Windows preview files are synchronized, with canonical-model, king/candidate
interaction and site/model checks passed. The alternate entry point differs by at most 45/255 in this check. The earlier execution-context sensitivity remains documented; this result does not establish its cause or a universal fix.
The existing shared knight metadata failure is not rerun or reported as a pass.

Next: improve the remaining pigment bands and varnish/grain variation while
preserving the accepted collar shape; then revisit the broad base and upper-rim
reflections. No watcher, subagent, push or publication was started.


## 2026-11-12 — checkpoint 014: collar grain and stable light sampling

Accepted 162, independently reproduced as 163 from checkpoint 013. A bounded
varnish-relief field makes collar highlights less smooth, preserving all geometry,
v6 pigment, source art, dimensions, lights and the 54-degree camera. Chroma/inverse
pigment repairs, extra coat roughness and stronger relief were rejected. See
[iteration-014/README.md](king-mission/iteration-014/README.md).

The first selected finish passed independent identity but failed a repeat render
by 45/255 at the familiar small socket glint. Failed checks remain in the record.
Disabling only light-tree sampling restores the tested canonical repeat and
independent render agreement within 1/255, with exact alpha. Other sampling
settings remain 128 adaptive/denoised. No threshold was relaxed.

High-res IoU is 97.8260%; original IoU is
96.8466%. Subjective scores: interior 85, color 82, grain
80, lighting 69. Working mean 82.7652%; holistic range 75–85%.
This is a small grain improvement; the full match remains incomplete.

Scope, packed-image preservation, nine receivers/regeneration, closed geometry,
exact mesh/camera export, canonical validation and king/candidate/site checks
pass. All 34 Windows preview files
are synchronized. Browser lighting remains approximate; whole-set knight
metadata and unchanged historical projections were not re-tested here.

Next: broader base and upper-platter reflections, then remaining pigment bands.
The goal remains active. No watcher, subagent, push or publication was started.
