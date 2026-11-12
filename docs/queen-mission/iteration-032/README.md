# Queen checkpoint 32 — compact base with the stem retained

Accepted on November 11, 2026. This is a moderate shape improvement, not a
claim that the original geometry has been recovered perfectly.

The foot, flare and socket are compressed vertically by 6%. The socket's
straight wall is 6.2% narrower, while the inner flare grows outward. The
horizontal shelf and steep wall remain distinct. Every stem radius from
control 38 upward is preserved; every control from 48 upward is exact. That
preserves the accepted collar join, three collars, inverted crown and egg.
The lower stem's height adjustment returns smoothly to the unchanged join.

| Measurement | Checkpoint 31 | Checkpoint 32 |
| --- | ---: | ---: |
| Socket seat height | 1.309390 | 1.230827 |
| Socket wall height, controls 29–33 | 0.250000 | 0.235000 |
| Socket wall radius | 0.564500 | 0.529500 |
| Shelf radial span, controls 33–38 | 0.112239 | 0.077239 |
| Inner flare radius, control 25 | 0.680000 | 0.727392 |

The total piece height and maximum base diameter are unchanged: 4.393650
and 2.089251, with height/base ratio 2.102978. The foot stays grounded. The
camera remains orthographic at 54 degrees. Source images, their registration,
and approved whole-set gallery defaults remain unchanged.

`side-before-after.png` uses identical physical scale and framing. The new
base is broader through its middle and shallower overall; the socket is less
heavy. `compact-shelf-source-comparison.png` shows both original colors, the
selected high-res source, the accepted predecessor and the two material trials
at identical pixel coordinates. This comparison is from the 64-sample trial;
the accepted fixed and side images are rendered again at 256 samples.

## Scores and tradeoff

| Metric | Checkpoint 31 | Checkpoint 32 |
| --- | ---: | ---: |
| Original black silhouette IoU | 97.8523% | 97.7916% |
| Selected high-res silhouette IoU | 97.9622% | 97.9975% |
| Interior/side shape, subjective | 88% | 89% |
| Wood color, subjective | 85% | 85% |
| Grain/texture, subjective | 79% | 79% |
| Lighting/reflections, subjective | 76% | 76% |
| Equal-weight working mean | 85.1705% | 85.3583% |

The original outline loses 0.0607 percentage points. The more compact base
and narrower socket justify this small tradeoff; an improved generated-image
score alone would not. The holistic estimate remains 80–85%. All material
percentages are visual assessments, not image-similarity measurements.

The socket's front reflection remains imperfect, with local bright segments
roughly 5–10 pixels away from the original on the 1254-pixel comparison canvas.
Highlight peaks are lighting evidence, not exact geometric landmarks. The
front shelf remains visible; this does not solve every internal contour. The
base's bottom rounding, socket crescent, crown highlights and overall grain
still need refinement. The side guide remains an imagined interpretation.
White was inspected as a secondary shape reference; its finish is not matched.

## Rejected studies

The first bracket adds projected socket arcs to the exterior fit. Those arcs
come from checkpoint 31 and are explicitly constraints, not fresh measurements
of unknown original geometry. The recorded profiles in `neutral-studies.json`
are the actual proposals, and `side-sheet.png` / `fixed-sheet.png` show real
production-subdivision renders using one neutral diagnostic light rig.

| Neutral proposal | Original IoU | Selected IoU | Decision |
| --- | ---: | ---: | --- |
| 54 degrees, 6% base compression | 97.7811% | 97.9816% | Fitted lower stem is too straight |
| 54 degrees, 10% base compression | 97.7762% | 97.9894% | Socket arc/radius compromise too large |
| 52-degree camera/profile | 97.5588% | 97.4332% | Collar/crown fit regresses |
| 50-degree camera/profile | 96.7319% | 96.5650% | Increasing outline and collar distortion |
| 48-degree camera/profile | 95.5232% | 95.6136% | Clear source-view regression |

The 52–48-degree experiments shorten the side view but do not establish a
better source explanation. Their optimized collar radii are less plausible;
these particular fits do not rule out every possible lower-angle hypothesis.
Neutral-only trials do not receive invented color/grain/light scores.

Trial 261 takes the first 6% proposal through the real wood rig. Its outline
scores are 97.7824% original / 97.9824% selected; shape 87, color 85, grain 79,
lighting 75. The fitted stem becomes too straight and the socket reflections
fragment. It is rejected. Trial 262 restores the accepted stem radii, preserves
controls 48 onward, and narrows the socket less aggressively. That is the
accepted version. Failed models are not added to the public review controls.

## Reproduction

Checkpoint 31 is archived in `history/queen-mission-031/queen-rebuilt.blend`:
`f6cbac79d43ce1e894f498340da4ebb0700c87dd44d0845cf0bab56e13310442`.

```sh
blender -b --python scripts/queen/study_compact_turning.py -- \
  --source history/queen-mission-031/queen-rebuilt.blend \
  --expected-source f6cbac79d43ce1e894f498340da4ebb0700c87dd44d0845cf0bab56e13310442 \
  --variant 262-compact-shelf-retain-stem \
  --base-profile docs/queen-mission/iteration-032/base-input.json --samples 64
```

Run `validate_side_shape_iteration.py` with the generated `profile.json`, and
`validate_profile_preservation.py` against checkpoint 31. Only then use
`publish_side_shape_checkpoint.py` with this evidence directory. The cumulative
profile is relative to protected checkpoint 22; `geometry-delta.json` separately
records the local changes from checkpoint 31.

The staged candidate digest is
`7cedabd2e3242b1282f114b8b193c26498a3ab40a1afeeadb9ff504128a90d6a`.
The active saved model digest is
`d58316454daad02fafaacbe7ff50215f042911cbd2e1609fbc8431f1c52ab0b4`.

To reproduce the neutral bracket, use `render_neutral_shape_studies.py` with
`--source history/queen-mission-031/queen-rebuilt.blend`,
`--manifest docs/queen-mission/iteration-032/neutral-studies.json`, and an
ignored `--output build/queen-mission/032-neutral-studies` directory. It never
saves or promotes a model. It preserves production subdivision but uses three
neutral inspection lights; material acceptance uses the original 85-light rig.

## Validation and next work

The scoped and delivered-model checks pass. The editable mesh is closed;
the six exact render receivers retain 715,776 triangles, atlas UVs and custom
normals. All 82 declared receiver links, all 85 lights, shader nodes and packed
image bytes are preserved. The viewer exports the same accepted editable
control surface at 44,924 triangles; Cycles uses its subdivision surface.
Camera regression, reference/tab interactions and site checks are recorded
in the adjacent reports. Browser illumination remains an approximation.

The review overlay, orbit model, side comparison and download are rebuilt
from the same saved checkpoint. The goal remains active. Next, inspect the
remaining socket crescent and the flare's turn into the foot, without losing
the shelf/drop or quietly changing the original reference alignment.
