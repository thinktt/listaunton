# Pawn checkpoint 017

Three thin physical reflectors partly restore the missing inner base-groove
highlight. They follow the curved reflected-ray field instead of lighting
the outer foot as well. Geometry, camera, all material settings and packed
textures, and the previous 44 lamps are unchanged. The rig now has 47 lamps.
This is an inferred studio arrangement, not recovered historical lighting.
The full visual-match mission remains incomplete.

## Investigation and decisions

Study 102 traces the actual meridian normals. The desired inner reflection
and the unwanted outer-foot glint have similar normal directions at different
positions. That explains why a broad low source illuminates both. Trials
103/104 tighten the outer bevel; their silhouettes remain close, but their
foot reflections deteriorate. Study 105 lowers the inner groove floor and
reduces the flare's underside radius. Neither restores the missing line.
These geometry changes are rejected; they do not replace the accepted mesh.

Studies 106/107 use much thinner area sources. Trial 108 fits one such source
with stronger polish inside the groove. It restores part of the line but also
brightens the left foot. Trial 110 restores the original material and fits
only that source; its line remains short, with a small stray outer glint.

Study 111 locates the curved groove in the fixed camera. Trial 112 places
three small reflectors along it, but leaves a gap near the brightest part
of the selected image. Trial 113 moves the third source into that gap.
All three are elliptical area lights, 0.22 by 0.004 model units, with a
four-degree spread. Their exact transforms and measured powers are recorded
in `reproduction.json`. No polish-mask or texture change is accepted.

## Comparison

| Measurement | Checkpoint 016 | Checkpoint 017 |
| --- | ---: | ---: |
| Inner-groove patch RGB error, 0-255 | 13.358 | 10.369 |
| Largest groove/foot patch RGB error | 12.524 | 10.421 |
| Right-foot patch RGB error | 7.011 | 6.464 |
| Left-foot patch RGB error | 6.642 | 6.754 |
| Front-foot patch RGB error | 1.485 | 1.523 |
| Base/foot common-foreground RGB error | 2.640 | 2.706 |
| Native original-black RGB error | 16.69 | 16.67 |
| Foot fine-pattern correlation | 0.9295 | 0.9258 |
| Foot fine contrast | 25.76 | 26.04 |

The groove patch improves about 22%; the line is more continuous but still
weaker and less detailed than the selected enlargement. The selected foot
contrast is 30.45. The extra edge immediately above the recess, fragmented
stem glint, collar residuals and inferred rear grain remain unresolved.

Adding lamps also changes Cycles' sample sequence. Study 114 renders a second
seed and isolates the three new sources together. The groove error improves
from 13.432 to 10.195 with that seed, and the local change correlates 0.939
between seeds. The isolated sources contribute zero measured radiance to
the head, collar/stem, left-foot and flare inspection patches. Upper-region
image differences have correlations near 0.02 between seeds, consistent with
sampling variation rather than newly placed highlights.

The broad RGB error is not a reliable improvement: it rises in the standard
seed, while the second-seed base/foot comparison improves slightly. Both are
retained. Study 114 uses black-composited RGB and a four-render common mask;
its whole-region numbers differ from the standard single-pair mission audit.
The small native-original change is not evidence of recovered hidden detail.
Acceptance rests on the repeatable local reflection improvement, original
consistency, preserved material and mesh, and visual inspection.

| Category | Checkpoint 016 | Checkpoint 017 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 94 | 94 |
| Lighting | 92 | 92 |
| Equal-weight working mean | 93.36% | 93.36% |

Only silhouette IoU is a measured percentage. The other ratings are visual
judgments; the holistic estimate remains 90-95%. Original black/white IoU
remain approximately 98.50%/98.14%. Tiny alpha-edge differences are sampling
effects; the exported geometry and UVs remain identical.

## Reproduction and validation

From the repository root with Blender 5.2.2:

```sh
blender -b --python-exit-code 1 --python scripts/pawn/fit_lighting.py -- docs/pawn-mission/iteration-017/reproduction.json
blender -b --python-exit-code 1 --python scripts/pawn/validate_groove_reflector.py -- docs/pawn-mission/iteration-017/reproduction.json models/pawn/pawn-rebuilt.blend docs/pawn-mission/iteration-017/scope-validation.json
blender -b --python-exit-code 1 --python scripts/pawn/validate.py -- .
```

The replay starts from archived checkpoint 016 and uses the explicitly
recorded light parameters. Scope validation checks every previous lamp,
geometry/normals/UVs, all packed maps, the full connected shader graph and
all color-ramp entries, the matte band, world, ray depth and sampling.
The saved model is reopened before export. `checkpoint.json` records the
actual fixed-render comparisons and mesh hash; `orbit-check.json` records
the four-angle studio and neutral-light inspection.

The fixed wood/clay views, side comparison and rotating mesh are synchronized
from that saved model. All site-link, whole-set model, candidate-interaction
and pawn-viewer checks pass; `site-checks.json` records their actual output.
Native browser GPU appearance remains unverified after the earlier local-file
policy rejection; no alternate route was attempted. The browser's rotating
lighting remains an approximation of the Cycles studio setup.

Next examine the left/front collar residual near x=425-457, y=606-638 against
both original sprites and the selected detail. Separate turning, finish and
lighting effects before changing geometry. Preserve this groove improvement,
the accepted proportions, source registration and fixed 54-degree camera.
