# Checkpoint 33 — a continuous curve into the foot

Accepted on November 11, 2026, from checkpoint 32 (`8d92adb`). The previous
lower flare had an inward inflection followed by another outward turn. It
created an extra band above the intended single base groove, most clearly
visible in the neutral side render. The accepted change replaces it with one
continuous convex turn and makes the groove slightly shallower.

![Side before and after](side-before-after.png)

![Base detail with the existing wood and neutral material](base-before-after.png)

## Shape and scope

Only radial controls 9–21 change. A cubic Bezier meridian defines the outer
turn at the existing control heights; the groove gains up to 0.006 units in
radius. The maximum radial edit is about 0.0148 units. Every height and every
control outside that range remains bit-identical to checkpoint 32.

The foot wall, compact socket shelf and steep drop, stem, rounded collars,
inverted crown and seated egg are preserved. The accepted whole-base 6%
compression remains. Height/base diameter is still **2.102978**. The actual
orthographic camera is **54.0000007°**, with unchanged reference registration.
No material, texture pixel, light, camera, gallery default or source image was
edited. This is a geometry change; existing reflections move as surface
normals change.

The [meridian diagnostic](accepted-meridians.png) finds two curvature-sign
reversals in the previous outer turn and none in the new one. It uses a cubic
B-spline approximation; actual level-2 Blender renders and evaluated-mesh
validation remain authoritative.

## Comparison and decision

Three neutral candidates tested a continuous turn, the same turn with a
shallower groove, and a lower round-over. The lower turn improves the
generated-reference outline more, but loses more agreement with the original.
The middle candidate was taken through the unchanged wood/light rig as
`266-continuous-base-turn` and accepted for its visibly cleaner side curve.
The fixed-view original loss is **0.0129 percentage points**, an explicit
tradeoff rather than a claim of better outline fit.

| Metric | Checkpoint 32 | Checkpoint 33 |
| --- | ---: | ---: |
| Original black silhouette IoU | 97.7916% | 97.7787% |
| Selected high-res silhouette IoU | 97.9975% | 97.9770% |
| Interior shape / side form, subjective | 89 | 90 |
| Wood color, subjective | 85 | 85 |
| Grain and texture, subjective | 79 | 79 |
| Lighting, subjective | 76 | 76 |
| Five-category working mean | 85.3583% | 85.5557% |

The holistic visual estimate remains **80–85%**. The original-white image was
also inspected for the lower curve and single groove. Its finish and slightly
different registration prevent treating its black-registration IoU as a direct
finish score. The reference images are untouched.

Evidence: [neutral bracket](neutral-roll-comparison.png),
[black/white/high-res and wood comparison](wood-roll-source-comparison.png),
[trial scores](neutral-roll-scores.json), [final scores](scores.json),
[exact geometry changes](geometry-delta.json), and [source hashes](source-hashes.json).

## Validation and synchronization

The saved closed mesh has no boundary or nonmanifold edges and positive
volume **4.407529**. Six regenerated render receivers contain 715,776 exact
evaluated triangles with matching UVs; custom-normal maximum component error
is 0.000146. All 82 receiver/light links and 85 light objects are preserved.
The material graph, packed image bytes, camera and object transform compare
equal to checkpoint 32. Viewer camera regression error is under 0.000039 pixels.

The accepted model is
`243844939937d0b753df253810f0e60d67b86a664f14b86dd678e7e22d348a68`.
The staged trial is
`5d00bbeea2bc51ddeff75f7abbd9d60647ac45cab59371145929dc718211db9e`.
Checkpoint 32 is archived at `history/queen-mission-032` with its four renders.
The publish operation saves the fixed camera before temporary side rendering.
All fixed/side images and the embedded viewer are rebuilt from this accepted
file. The browser retains approximate real-time lighting; fixed and side
images are actual Cycles renders. Final delivery checks are recorded in
`checks.json` after local-browser verification.

## Reproduction

Run from the repository root using Blender and Python with NumPy, Pillow and
SciPy. The first command creates a separate trial; it does not replace the
accepted model. The neutral-render helper can reproduce all three proposals
from `flare-roll-studies.json` and the archived checkpoint 32.

```sh
blender -b --python scripts/queen/study_compact_turning.py -- --source history/queen-mission-032/queen-rebuilt.blend --expected-source d58316454daad02fafaacbe7ff50215f042911cbd2e1609fbc8431f1c52ab0b4 --variant 266-continuous-base-turn --base-profile docs/queen-mission/iteration-033/264-shallow-groove-roll.json --samples 64
blender -b --python scripts/queen/validate_side_shape_iteration.py -- --blend build/queen-mission/266-continuous-base-turn/queen.blend --config build/queen-mission/266-continuous-base-turn/profile.json --report docs/queen-mission/iteration-033/side-shape-validation.json
blender -b --python scripts/queen/validate_profile_preservation.py -- build/queen-mission/266-continuous-base-turn/queen.blend --baseline history/queen-mission-032/queen-rebuilt.blend --out docs/queen-mission/iteration-033
```

After reviewing and validating a fresh trial, promote with
`publish_side_shape_checkpoint.py -- 266-continuous-base-turn --evidence docs/queen-mission/iteration-033`.
That helper renders the accepted scene at 256 samples, with the recorded light
tree setting disabled. Follow with `validate_finished_queen.py`,
`export_viewer_mesh.py`, `inspect_viewer_camera.py`, the viewer and side builders,
`compare_finished_queen.py`, and `overlay_qa.py --reference-mask max-channel`.
`record_base_turn_checkpoint.py` regenerates this checkpoint's measurements,
source preservation assertions, scorecard and accepted before/after images.
Run the camera, review interaction and affected site checks before delivery.

The raw proposal-generation code and controls are included here in
`propose_flare_roll.py`, `analyze_flare_roll.py` and `controls-032.npy`.
They generate analytic diagnostics, not replacement model renders.

## Remaining issues

The socket crescent still does not trace the original exactly. Separate its
geometric seat from its reflected highlight before editing the protected shelf.
The imagined side remains a guide rather than recovered geometry. Crown/finial
shading, coarse relief, pigment variation and the base highlight retain visible
differences. No texture or lighting completion is claimed. The shape mission
continues from this accepted checkpoint without watchers or subagents.
