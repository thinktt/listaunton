# King mission log

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
