# Pawn checkpoint 011

Trial 062 refines the grain inside the collar highlight, with the same pawn
geometry, 54-degree camera and 44-light rig as checkpoint 010. The fixed view
is closer, but the visual-match mission remains incomplete.

## Changes and evidence

A collar-only finish calibration varies real roughness and polish. A second
set of measured tangent-normal responses refines the small surface slopes.
The finish and normal maps are byte-identical to the preceding maps outside
the collar band. They change 0.184% and 0.234% of their respective atlases.
The original pigment-driven relief is preserved. Replacing its collar input
with the newer color texture shifted and over-brightened the reflections;
trial 061 is rejected.

Sampling tests showed that denoising at 128 samples obscured some fine collar
detail. At 768 samples, disabling the light tree reduced the difference
between seeds from 2.52 to 1.99 RGB levels in the tested crop. The accepted
scene uses 512 samples, seed 0 and the light tree disabled. Pigment was then
measured again at that same quality, including both live wood BSDFs.

| Collar reflection | Pattern correlation, 010 | Pattern correlation, 011 |
| --- | ---: | ---: |
| Left | 0.657 | 0.815 |
| Right | 0.758 | 0.824 |
| Front | 0.813 | 0.870 |

The upper-head fine-pattern correlation also improves from 0.826 to 0.904.
The narrow flare line regresses from 0.735 to 0.663, and the foot line from
0.898 to 0.861. Foot-line fine contrast changes from 22.9 to 21.4 against
30.4 in the selected reference. These are accepted tradeoffs for clearer
collar and head grain, not evidence of uniform improvement. The lower
reflections remain a useful next target under the more stable sampling.

Common-foreground RGB errors fall from 2.99 / 2.98 / 3.46 to
2.67 / 2.45 / 3.14 for head / collar-stem / base-foot. Native original RGB
error rises slightly from 16.50 to 16.60; the chosen enlargement measures
15.74 against the original. Contact-profile error changes from 3.03 to 3.44.
Its dark core is 6.53 against 4.19 in the selected reference. All three head
glints remain within 0.93 original sprite pixels.

## Assessment

| Category | Checkpoint 010 | Checkpoint 011 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 92 | 93 |
| Lighting | 92 | 92 |
| Equal-weight working mean | 92.96% | 93.16% |

The four visual ratings are judgments. The holistic range remains 90–95%.
Original black and white IoU are 98.499% and 98.135%. Small alpha-edge
changes come from sampling; exported geometry, normals and UVs are identical
to checkpoint 010. The model continues to follow the original sprites where
the generated detail reference disagrees about rear-flare width.

The collar still has coarse patches, the lower-head reflected line remains
visible, and the stem/socket highlights differ. The finest flare and foot
texture is weaker than the selected reference. Hidden wood is inferred and
uses broader grain; four-angle studio and neutral-light views check that the
material remains usable away from the fitted camera.

## Reproduction and checks

`scorecard.json` records all five categories for trials 058–062. The final
model and render hashes are in `checkpoint.json`. Rebuild from the repository
root with Blender 5.2.2:

```sh
blender -b --python-exit-code 1 --python scripts/pawn/rebuild_collar_finish.py -- docs/pawn-mission/iteration-011/reproduction.json
blender -b --python-exit-code 1 --python scripts/pawn/validate_collar_finish.py -- docs/pawn-mission/iteration-011/reproduction.json models/pawn/pawn-rebuilt.blend docs/pawn-mission/iteration-011/collar-material-validation.json
blender -b --python-exit-code 1 --python scripts/pawn/validate.py -- .
```

The first command reconstructs trial 063 from archived checkpoint 010 and
tracked maps, without replacing the accepted model. The scope check verifies
unchanged geometry, normals, UVs, lights, world, ray depths, shader structure
and the matte band. It also verifies packed map pixels, collar-only map edits,
explicit sampling settings and absence of the rejected relief change.

The reopened render and independent reconstruction agree with the reviewed
trial within one RGB level. Fixed wood/clay, side comparison and rotating
mesh are generated from the same saved scene. The browser uses the matching
maps and approximate lighting. Code-based checks cover its camera, controls
and embedded data. Native browser GPU verification remains unavailable after
the earlier local-file URL policy rejection; no alternate browser route was
attempted. See `site-checks.json` for current repository checks and the last
recorded separate whole-set metadata issue.
