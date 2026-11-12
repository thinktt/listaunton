# Queen checkpoint 29 — refine the slender seated egg

## Result

The compact midpoint egg from checkpoint 28 read slightly too squat when compared at normal size with the selected high-resolution crown crop. The reference shows a narrower, still egg-like finial whose top sits lower than checkpoint 27 but retains more vertical presence than the midpoint trial.

Starting from the preserved checkpoint-27 model, variant `241-slender-seated-egg` changes only cap controls 108–116, anchored at ring 107. It retains 96% of the checkpoint-27 exposed-cap height and 94% of its radius. The top is 0.013673 Blender units lower than checkpoint 27, so it remains seated in the shallow inverted bowl without becoming a button. Relative to checkpoint 28, it restores 0.020533 units of height while becoming visibly narrower.

The crown bowl, splash rim, eight tips, collars, stem, raised socket shelf and steep drop, flare, foot, UVs, pigment, light rig, source registration, and 54-degree orthographic camera are unchanged. The accepted active model is `441f40d2ef07e5bf6c5f14380c2d7ba71c94172add6c1891da9eb399907ecea0`.

## Controlled bracket

- `239-compact-seated-egg` (84% height / 94% radius) remains rejected: it reads as a flattened button.
- `240-seated-egg-mid` (90% / 97%) was useful but its crown crop read too squat and low.
- `241-slender-seated-egg` (96% / 94%) is accepted because it preserves the enclosed, egg-like vertical curve while reducing its exposed width. It is a deliberate interior-form decision rather than an outline-only optimization.

The reproducible accepted command is:

```sh
blender -b --python scripts/queen/study_finial_seating.py -- \
  --source build/queen-mission/235-foot-lip-half-strength/queen.blend \
  --variant 241-slender-seated-egg --height-factor 0.96 --radial-factor 0.94 --samples 64
```

## Reference fit and scorecard

The finial remains inside the crown’s hole-filled exterior silhouette. As expected, the fixed outline IoUs are unchanged; the enlarged crown crop and neutral profile decide this acceptance.

| Metric | Checkpoint 28 | Checkpoint 29 | Change |
| --- | ---: | ---: | ---: |
| Original Lichess black outline IoU | 97.8523% | 97.8523% | unchanged |
| Selected high-res outline IoU | 97.9622% | 97.9622% | unchanged |
| Interior shape | 86.5% | 87.0% | narrower, more egg-like seated cap |
| Wood color | 85.0% | 85.0% | geometry-only regression check |
| Grain / texture | 79.0% | 79.0% | geometry-only regression check |
| Lighting / reflections | 76.0% | 76.0% | geometry-only regression check |
| Equal-weight working mean | 84.8705% | 84.9705% | +0.1000 points |

The model now measures 4.393650 units tall on a 2.089251-unit base diameter, or 2.102978 height/base. The original black Lichess sprite remains the authority; the selected high-resolution candidate is used to inspect the bowl/egg relationship.

## Validation and synchronization

The scoped candidate validator records a closed positive-volume mesh with zero boundary and non-manifold edges, all undeclared rings identical to the composed baseline, six exact receiver regions, exact evaluated faces/atlas UVs, 715,776 receiver triangles, and 82 receiver-light links. The delivered-model validator independently passes at 54.00000066 degrees with the active model hash.

The closed editable-control viewer export contains 44,924 triangles. Its reference-camera harness passes with a maximum projected error of 0.00003865 pixels, and the reference/review interaction harness passes. Fixed wood/clay, registered side images, comparison crops, the viewer mesh, and embedded `review.html` were rebuilt from the active model. Static model/site checks also pass.

Useful evidence: `comparison-crown.png`, `comparison-full.png`, `queen-finished-profile.png`, and `side-aligned-neutral.png` in `assets/queen/`.

## Next

This accepts the improved crown interior without claiming the queen finished. Continue the shape mission with the original sprite as arbiter, retaining the restored socket shelf/drop and lower-foot support. The remaining main question is side plausibility of the collar/base assembly; texture and lighting finishing remain deferred.
