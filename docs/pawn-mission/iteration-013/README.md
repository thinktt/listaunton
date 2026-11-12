# Pawn checkpoint 013

Trial 074 improves fine grain inside the stem and socket reflections. Geometry,
pigment, the 54-degree camera and all 44 lights remain unchanged from checkpoint
012. The mission remains incomplete, and the overall assessment stays 93.36%.

## Investigation and changes

Three isolation studies cover every fixture, the world contribution and
secondary glossy rays. The upper and lower stem rim reflectors create the
left stem glint. Moving the upper reflector's target by about two image pixels
in trial 071 raises collar/stem RGB error from 2.44 to 2.49 and original-sprite
color error from 16.60 to 16.62. That light change is rejected.

The accepted refinement retains the rig and changes only local material
maps. Nine roughness/polish responses plus an independent seed guide trial
072. Two sets of seventeen tangent-normal responses guide trials 073 and
074, with smaller steps in the second pass. All use the accepted 512-sample,
seed-0, light-tree-disabled setup. The band was located using the saved
meridian, camera and depth; visibility and measured response constrain edits.

The finish map changes 0.481% of its pixels and the normal map 0.518%.
Both are byte-identical outside UV height 0.422–0.668, preserving the head,
collar and lower-base maps. Roughness/polish ranges stay 0.30–2.40 and
0.38–1.85; normal slopes remain bounded at 0.135 (about 7.69 degrees).
The fitted proposals in the recovery report are clamped to those ranges
when encoded. The existing pigment-driven relief and complete live BSDF
graph are preserved; no image composite or emission substitutes for shading.

| Measured patch | Pattern correlation, 012 | Pattern correlation, 013 |
| --- | ---: | ---: |
| Stem edge | 0.402 | 0.735 |
| Socket lip | 0.883 | 0.943 |

Stem fine contrast rises from 17.16 to 17.92 against 24.52 in the selected
reference. Socket contrast rises from 20.28 to 21.64 against 26.11. See
`stem-detail.png` and `socket-detail.png` for the enlarged comparison.
The stem highlight remains broader and rougher than the selected image;
the improved local correlation does not resolve its full shape.

Collar/stem common-foreground RGB error falls from 2.44 to 2.32 levels and
base/foot error from 2.76 to 2.72 (that region includes the socket). Head,
flare and foot reflection correlations remain steady. Native original RGB
error changes from 16.60 to 16.61; the chosen enlargement itself measures
15.74. The head/contact brightness-profile error remains 3.48, with a dark
core of 6.53 against the selected image's 4.19.

## Assessment and next step

| Category | Checkpoint 012 | Checkpoint 013 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 94 | 94 |
| Lighting | 92 | 92 |
| Equal-weight working mean | 93.36% | 93.36% |

The four visual ratings are judgments; the holistic range stays 90–95%.
This is a useful local improvement, insufficient to raise the whole-piece
ratings. Original black and white silhouette IoU remain 98.499% and
98.135%. The original's broader rear flare continues to take precedence
over the generated detail reference.

Remaining defects include the stem rim's broad broken reflection, coarse
collar patches, lower-head reflected line, soft or cool highlight cores and
inferred rear grain. Next isolate the older pigment-driven bump and fine
normal layers along the stem rim to determine their contribution before
another surface or curvature change. Preserve the accepted lighting and
improved head/base finish. The image under neutral inspection light and
from the rear remains an interpretation, not recovered historical evidence.

## Reproduction and validation

From the repository root with Blender 5.2.2:

```sh
blender -b --python-exit-code 1 --python scripts/pawn/rebuild_collar_finish.py -- docs/pawn-mission/iteration-013/reproduction.json
blender -b --python-exit-code 1 --python scripts/pawn/validate_local_surface.py -- docs/pawn-mission/iteration-013/reproduction.json models/pawn/pawn-rebuilt.blend docs/pawn-mission/iteration-013/surface-validation.json
blender -b --python-exit-code 1 --python scripts/pawn/validate.py -- .
```

The independent replay starts from archived checkpoint 012 and tracked maps.
`checkpoint.json` records the actual saved model and image comparisons.
The scope validator covers the full shader graph, old relief and pigment,
packed map pixels and permitted band, mesh/normals/UVs, all lights, world,
ray depths and sampling. Source pixels, registration and gallery defaults
are unchanged. `scorecard.json` records all five categories for every trial.

Fixed wood/clay, side comparison and rotating assets use the same saved
model. Four-angle studio and neutral-light inspections are recorded in
`orbit-check.json`; page and interaction checks are in `site-checks.json`.
Native browser GPU inspection remains unverified after the earlier local-file
URL policy rejection; no alternate browser route was attempted. The browser
uses the matching maps with approximate lighting, rather than the full
Cycles rig. None of these checks establishes a perfect visual match.
