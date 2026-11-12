# Queen checkpoint 28 — seat the egg deeper

## Result

Starting from checkpoint 27 (`8aa9492357a703f656189ad479294c5882da3c129cfb99a120b5ee1b7a85e3b3`), this checkpoint makes the queen's exposed finial read as a smaller, more deeply seated egg. The owner had identified this relationship to the inverted crown bowl as a remaining high-value mismatch.

Only cap controls 108–116 change. They are anchored at ring 107, compacted to 90% of their prior height above that seat, and reduced to 97% of their prior radius. The uppermost point is 0.034182 Blender units lower. The bowl, rim, eight tips, collars, stem, raised socket's horizontal shelf and steep drop, flare, foot, UVs, pigment, relief, light rig, source registration, and 54-degree orthographic camera remain fixed.

The accepted active model is `dc29132cdf38208d09452185a16065bc94ee7d6be20b03f11efad193e81b8906`.

## Controlled bracket

- `239-compact-seated-egg` tested a stronger 84% height / 94% radial cap. It was rejected: the side and crown crop made the egg read too much like a flattened button.
- `240-seated-egg-mid` tested 90% height / 97% radius. It keeps an egg-like upper curve while visibly reducing the exposed hemisphere and making the finial sit more convincingly in the shallow bowl. It is accepted.
- The stronger post-checkpoint-27 lower-foot bracket (`236-foot-lip-012`) was rejected because it harmed the selected-high-res rim fit. Upper-collar brackets `237` and `238` were also rejected because their normal-size visual change was too small to justify a new public shape.

The reproducible accepted command is:

```sh
blender -b --python scripts/queen/study_finial_seating.py -- \
  --variant 240-seated-egg-mid --height-factor 0.90 --radial-factor 0.97 --samples 64
```

## Reference fit and scorecard

The finial is inside the crown's hole-filled silhouette, so neither source's outline IoU moves. That is expected rather than evidence of no geometric change. The crown crop and neutral side/profile render are the relevant visual checks.

| Metric | Checkpoint 27 | Checkpoint 28 | Change |
| --- | ---: | ---: | ---: |
| Original Lichess black outline IoU | 97.8523% | 97.8523% | unchanged |
| Selected high-res outline IoU | 97.9622% | 97.9622% | unchanged |
| Interior shape | 86.0% | 86.5% | compact egg fits the bowl better |
| Wood color | 85.0% | 85.0% | regression check unchanged |
| Grain / texture | 79.0% | 79.0% | regression check unchanged |
| Lighting / reflections | 76.0% | 76.0% | regression check unchanged |
| Equal-weight working mean | 84.7705% | 84.8705% | +0.1000 points |

The height/base-diameter ratio changes from 2.109511 to 2.093150 solely through the smaller finial. The whole-set gallery preset remains unchanged. The original black sprite remains the authority; the selected high-res candidate makes the egg/bowl relationship easier to inspect.

## Validation and synchronization

`side-shape-validation.json` validates the staged candidate against the checkpoint-22 source archive and its complete recorded control configuration. It finds a closed positive-volume mesh, zero boundary and non-manifold edges, all undeclared rings identical, six exact receiver regions, exact evaluated faces/atlas UVs, 715,776 receiver triangles, and 82 receiver-light links.

The active delivered-model validator passes at 54.00000066 degrees. The viewer export contains the closed editable control, 44,924 triangles, and the active model hash. The camera/viewer and reference/review interaction harnesses pass; those browser checks use the repository's simulated DOM/WebGL harness, while fixed and side images are actual Blender renders. Fixed wood/clay, registered side images, comparison crops, and the embedded `review.html` viewer were rebuilt from the accepted file.

Useful current visual evidence remains in `assets/queen/comparison-crown.png`, `assets/queen/comparison-full.png`, `assets/queen/queen-finished-profile.png`, and `assets/queen/side-aligned-neutral.png`.

## Next

The finial relationship is improved but not claimed perfect. Continue the shape mission with the original Lichess sprite as arbiter, protecting the restored socket shelf/drop and accepted foot support. The remaining broader question is the side plausibility of the collar/base assembly; texture and lighting finishing remain deferred by this phase.
