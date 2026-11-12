# Pawn checkpoint 014

The stem's reflected grain is closer after a broader normal-field and finish
fit. Trial 079 preserves the geometry, pigment, fixed 54-degree camera and
all 44 lights. The mission remains incomplete. The overall assessment stays
93.36%; this small local gain does not justify a whole-piece score increase.

## Investigation

Trial 076 disables each normal layer separately, then all three together.
Removing the measured fine slopes raises RGB error in the examined stem
patch from 10.83 to 19.37 levels. Removing every relief layer raises it to
22.63. Neither fixes the reflection's shape. The accepted material retains
the procedural relief, old pigment-driven bump and measured fine normals.
The diagnostic comparison headings name the disabled layer.

Trial 077 measures six physical controls of the existing upper stem
reflector: two position directions, major/minor dimensions, power and
rotation. Its best actual cropped render reduces weighted squared error
by only 1.3%. The visible mismatch remains. That light change is rejected;
the accepted checkpoint preserves the previous rig exactly.

Trial 078 measures seventeen actual tangent-normal responses at the saved
camera. Unlike the earlier fine-detail fit, it retains the broad error
signal in the small stem crop. Trial 079 then measures nine local
roughness/polish responses and an independent render seed. Confidence,
depth visibility and a smooth UV band constrain both updates. The checked
material is a real BSDF with static maps, not an image composite.

Only 0.241% of finish pixels and 0.286% of normal-map pixels change from
checkpoint 013. Both maps are byte-identical outside UV height 0.49-0.65;
the focus fades over 0.49-0.515 and 0.625-0.65. The head, collar, socket
and lower-base maps are preserved. Roughness/polish gain ranges remain
0.30-2.40 and 0.38-1.85. Normal slopes remain bounded at 0.135, or about
7.69 degrees. Fitted proposals are clamped when encoded.

## Comparison and assessment

Stem fine-pattern correlation rises from 0.735 to 0.830. Fine contrast
rises from 17.92 to 20.00 against 24.52 in the selected reference. The
collar/stem region's common-foreground RGB error falls from 2.325 to 2.303
levels. Head, socket, flare and foot measurements remain essentially
unchanged. Native original RGB error stays 16.61 at the reported precision;
the selected enlargement itself measures 15.74. See `stem-detail.png`,
`native-comparison.png` and the per-trial evidence.

| Category | Checkpoint 013 | Checkpoint 014 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 94 | 94 |
| Lighting | 92 | 92 |
| Equal-weight working mean | 93.36% | 93.36% |

The four visual ratings are judgments, not measured accuracy percentages.
The holistic range remains 90-95%. Original black/white silhouette IoU
remain 98.499%/98.135%. The original's broader rear flare still governs
the shape where the generated reference differs.

The stem's reflection is still too fragmented and soft. Row profiles show
that much of its centerline is already close; the shape of the bright core
and excess light immediately beneath the collar need further work. Other
remaining defects include coarse collar grain, the lower-head reflected
line, soft/cool highlight cores and inferred rear grain. Next examine the
larger collar residual around reference pixels x=437-469, y=606-638, using
source isolation before another local material change. Preserve this stem
improvement and the accepted head/base finish.

## Reproduction and validation

From the repository root with Blender 5.2.2:

```sh
blender -b --python-exit-code 1 --python scripts/pawn/rebuild_collar_finish.py -- docs/pawn-mission/iteration-014/reproduction.json
blender -b --python-exit-code 1 --python scripts/pawn/validate_local_surface.py -- docs/pawn-mission/iteration-014/reproduction.json models/pawn/pawn-rebuilt.blend docs/pawn-mission/iteration-014/surface-validation.json
blender -b --python-exit-code 1 --python scripts/pawn/validate.py -- .
```

The independent replay uses archived checkpoint 013 and the tracked v8
finish/normal maps. `checkpoint.json` records saved-file and replay pixel
comparisons and hashes. The scope validator checks mesh positions,
geometric normals, UVs, all lights, world, ray depths, sampling, full live
shader graph, prior bump, pigment and packed map pixels. Source images,
registration and gallery defaults remain unchanged.

Fixed wood/clay, profile and rotating assets are rebuilt from the same
saved model. Four-angle studio and neutral-light views are recorded in
`orbit-check.json`. Site and interaction checks are in `site-checks.json`.
Native browser GPU appearance remains unverified after the earlier
local-file policy rejection; no alternate browser route was attempted.
The interactive viewer uses the matching maps with approximate lighting,
not the complete Cycles rig. These checks do not establish a perfect match.
