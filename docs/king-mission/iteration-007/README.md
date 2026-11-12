# King checkpoint 007 — broader foot shoulder

The foot now catches a broad crescent in the reference position. Its earlier
double hairline was too low. Eight lower profile controls, a local varnish
adjustment and one fitted area reflector produce this accepted refinement.
The 54-degree camera and existing image registration govern every comparison.

## Shape and finish

Controls 4–11 form a wider shoulder that slopes upward into the groove.
The final 0.025-unit lowering of controls 5–8 places the crescent closer to the
reference; control 4 blends that change into the wall. Reproduction records
each operation separately to retain the same float rounding. The evaluated
lathe section has no detected crossings. Total height and base bounds are exact
against checkpoint 006. The model has two closed, intersecting components and
70,364 exported triangles.

The `Foot shoulder satin` attribute increases local roughness to 0.32, coat
roughness to 0.28 and fine varnish-relief strength to 0.20. It fades in over
controls 2–3 and out over 7–8, with zero values on the cross. The packed v6
pigment atlas and all earlier UVs, attributes and material inputs pass scope
checks. Four derived light receivers reproduce the evaluated closed body.

The new 4 × 3 area source illuminates the foot through the real glossy BSDF.
Its fitted power is 523.8494. The previous foot spot is disabled. Cast shadows
remain enabled, and the other lights retain their settings and receiver routes.
The measured response fit used the same reference pixels through AgX.

## Comparison

| Metric | Checkpoint 006 | Checkpoint 007 |
| --- | ---: | ---: |
| Selected-reference silhouette IoU | 97.8197% | 97.8171% |
| Interior form | 83% | 84% |
| Wood color | 82% | 82% |
| Grain and surface texture | 79% | 79% |
| Lighting and reflections | 60% | 62% |
| Equal-weight working mean | 80.3639% | 80.9634% |

Original-sprite IoU is 96.8335%, versus 96.8331%. The selected silhouette
tradeoff is 0.0026 percentage points. Only IoU is a measured category score.
The four other ratings and the holistic 74–83% range are visual judgments.

In the fixed foot crop, RGB mean-square error on 0–255 values falls from
403.86 to 234.69. The three brighter reference columns at x=360, 400 and 440
have average peak-position error of 1 pixel, versus 7.33 pixels previously.
Dimmer columns can select adjacent features; the complete table and search
band are in `foot-measurements.json`. These limited measurements support the
placement improvement. Grain agreement requires visual inspection.

The crescent remains too smooth. Its broken white glints, darker separation,
and fine grain pattern still differ from the reference. The lower base glint
is undersized and the upper glint too small. Cross seating, shelf-like collars,
cavity contrast and upper reflections remain unfinished. Side/rear inspection
still shows residual pigment shading, a warmer base patch and an unfinished
cross-side texture. Neutral clay retains the existing receiver illumination
cutoff. The full visual mission remains active and incomplete.

## Experiments

`scores.json` records every full-model trial and its decision. Cropped light
and normal diagnostics are retained separately. Increasing light power,
removing cast shadows, and broadening the source did not repair the inward
shoulder normals. The sloping shoulder recovered a broad reflection. A fitted
local finish and the measured height correction gave the strongest result.

Sharper polish, a deeper altered flare and procedural pore experiments were
rejected. They produced smooth stripes or the wrong glint pattern. Their
configs and helper remain reproducible evidence. The accepted scene uses the
earlier grain pipeline with the local satin adjustment.

## Reproduction and validation

From the repository root, run with Blender 5.2:

```text
blender --background --python-exit-code 1 --python scripts/king/rebuild_foot_checkpoint.py -- docs/king-mission/iteration-007/reproduction.json --variant checkpoint-007-rebuild
```

This reads `history/king-mission-006/king-rebuilt.blend` and writes a separate
build directory. The source hash is checked. The complete independent rebuild
and reopened accepted scene each reproduce the fixed render with identical
alpha and maximum channel difference 1/255. The rebuilt exported mesh is
byte-identical. See `reproduction-checks.json`.

Use `check_foot_shoulder.py` with the archived sixth model, the current model,
`reproduction.json` and an output JSON path. It verifies the declared control
edits, all original UVs/attributes/packed images, local material scope, camera,
world, light settings and exact receivers. `check_region_regeneration.py`
verifies future receiver regeneration. Canonical `validate.py`, exact mesh
export, side registration and the historical projection checks pass.

The repository and existing Windows preview contain the same accepted model,
fixed and side renders, and rotating mesh. All 34 king preview files are
hash-verified. King viewer and candidate interactions pass the actual-page
DOM/WebGL harness. Native browser screenshot inspection was not performed.

One shared check fails. `check_set.cjs` rejects the knight's stored height-source
metadata hash. The same mismatch is present at the task-start commit
`f32177d9c8c2331e4071ed3df592bf65d09936d1`. The knight metadata, set page and
scale record match their task-start versions. See
`pre-existing-gallery-check.json`. Checks after that assertion remain
unexecuted. King/site/model/candidate and historical-projection checks pass.

Next, inspect the socket and collar reflector responses individually and
refine their placement and warmth. A later foot-grain study should use a
surface-coordinate relief source and retain this shoulder placement.
