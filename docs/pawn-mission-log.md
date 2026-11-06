# Pawn reconstruction log

## Checkpoint 001 Â· 2026-11-05

The first walnut checkpoint lifts the round part of the head about 15 reference
pixels, keeps its broad contact with the collar, and flattens the bottom of the
foot. Overall height changes by less than 0.000003 model units. Base diameter
changes from 1.6500 to 1.6532. The camera stays at its saved orthographic 54Â°
view, and the gallery uses its approved 49.2%-of-king display height.

| Metric | Seated clay baseline | Checkpoint 001 |
| --- | ---: | ---: |
| Selected silhouette IoU | 94.21% | 95.65% |
| Interior form | 74 | 80 |
| Wood color | 0 | 78 |
| Grain and surface | 0 | 72 |
| Lighting | 23 | 48 |
| Equal-weight working mean | 38.24% | 74.73% |

Original black overlap improves from 96.54% to 97.82%. White improves from
95.90% to 97.91%. These values use the mission's filled foreground masks.
The earlier clay report used raw masks. The four visual ratings are estimates.
The selected-view holistic assessment is 70â€“79%. The clay baseline had no
wood pigment or grain to score.

The original sphere radius was already within a fraction of a pixel of the
black sprite's fitted radius. Its center sat roughly 17 output pixels low.
An egg-shaped trial and a trial with a raised pedestal were rejected after
side inspection. The retained upper sphere stays round. The lower flank blends
into the original seat at its original contact width.

The 2048-square atlas carries inferred diffuse wood. Actual black and gray
BSDF renders measure reflections and diffuse response. Reliable wood samples
supply the visible pattern. Surface-space interpolation and the existing
unlit walnut source carry grain through highlight gaps and onto hidden faces.
One closed editable control drives both the Cycles render and UV-mapped viewer.

The base needs a stronger dark groove and broader textured highlights.
The current base reflector adds an unwanted fourth head glint, and the three
intended glints are weak and too smooth. The neck/socket reflection and a
yellowish pigment patch also differ. The hidden wood is an interpretation.
Next isolate and fit the three head glints, then reassess base and collar spill.

The reopened and independently rebuilt renders have identical alpha to the
selected trial and differ by at most 1/255 in RGB. The mesh is one closed,
positive-volume component with 57,984 triangles. Camera regression error is
below 0.000011 pixels in the DOM/WebGL interaction check. See the full trial
scorecard, views, checks, and rebuild instructions under
[iteration 001](pawn-mission/iteration-001/README.md). Mission in progress.

## Checkpoint 002 · 2026-11-05

Grain relief and real shaped reflectors give the head three textured glints.
The unwanted fourth glint is gone. The base and socket now catch light in
more of the intended places. The base still has broad highlights, the stem
has an unwanted narrow streak, and the deep foot groove remains too light.
The left base reflection is also too square. These limit the current result.

| Metric | Checkpoint 001 | Checkpoint 002 |
| --- | ---: | ---: |
| Selected silhouette IoU | 95.653% | 95.651% |
| Interior form | 80 | 80 |
| Wood color | 78 | 79 |
| Grain and surface | 72 | 76 |
| Lighting | 48 | 66 |
| Working mean | 74.73% | 79.33% |

Original black IoU is 97.816% and white is 97.911%. Geometry, UVs, pigment
and camera are preserved. The exported geometry binary is identical to the
previous checkpoint. Only IoU is measured. Holistic assessment is 75–83%.
Saved/reopened and independent replay renders agree with the chosen trial
within 1/255, with identical alpha. The site and existing local preview are
refreshed at this checkpoint. For all trials, actual settings and remaining
issues, see [iteration 002](pawn-mission/iteration-002/README.md).
Next inspect the flare curvature and actual groove geometry against both
originals. The mission remains active.
