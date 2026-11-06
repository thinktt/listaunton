# Knight reconstruction mission log

## Checkpoint 001 | Fixed-view pose and walnut, November 5, 2026

The source was the accepted clay carving from `0794bf0`, SHA-256
`2c0c11c5d29bdb417ec415723f9aadf825acbf4a6bc769922dce953c288de333`. Its seven visible parts and two hidden
construction lofts are preserved in `history/knight/mission-start`. The
original Lichess sprites govern geometry. Selected black candidate 2 supplies
the detailed finish target. Its SHA-256 is
`1699927b5c260ef2ccccb2b4daba22d1f4947bb4819ea7b39426474a8450baa0`. The saved camera stays at 54 degrees elevation,
12 degrees yaw, with its original framing and image registration.

The starting clay had 88.26% selected outline overlap and
88.61% original overlap under the mission mask. Initial
form 67, color 0, grain 0, lighting 22. A neutral study has no wood finish to
score. The side profile was already recognizable, while the entire head sat
right of the original and its muzzle projected too low.

A small rigid movement of the upper head, smoothly distributed through the
neck, brings the eye and muzzle into closer registration. X/Y shift is
(-0.313, -0.045) and the upper twist is 10.3 degrees. The fit gives the
original contour 80% weight and the candidate 20%, plus a separately observed
eye landmark. All Z coordinates, the pedestal, camera, floor and reference
transforms are held fixed. The head sits farther back in the side comparison.
The level and 7-degree side images retain its broad cheek, conical muzzle and
curved neck. The exact former side overlay is an explicit tradeoff.

The first surface trial used volume noise and growth rings. A quiet section of
the selected pedestal then supplied small-scale luminance variation for a
continuous wood volume. Black and gray BSDF response passes measured reflected
light and approximate diffuse response. Inverse AgX and bounded wood hues
provide an inferred pigment field. Low-confidence glare is softened and
high-frequency detail is bounded. A visibility test attaches this color to
the mesh. Unseen areas retain continuous wood. Lights, roughness, varnish and
pore relief act on the actual three-dimensional surface from any view.

| Trial | Outline | Form | Wood color | Grain | Lighting | Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 001-carving-pose | 94.33 | 72 | 0 | 0 | 22 | 37.67 |
| 002-walnut-studio | 94.33 | 72 | 59 | 38 | 37 | 60.07 |
| 003-continuous-grain | 94.33 | 72 | 64 | 49 | 34 | 62.67 |
| 004-measured-pigment | 94.33 | 72 | 76 | 61 | 39 | 68.47 |
| 005-softened-pigment | 94.33 | 72 | 78 | 67 | 39 | 70.07 |
| 006-pigment-atlas | 94.33 | 72 | 49 | 42 | 33 | 58.07 |
| 007-complete-atlas | 94.33 | 72 | 49 | 42 | 33 | 58.07 |
| 008-packed-walnut | 94.33 | 72 | 78 | 67 | 39 | 70.07 |

The current working mean is **70.07%**, with a holistic
assessment around 65-72%. Only outline overlap is measured. Original outline
IoU is 95.08% and mirrored white is 94.60%.
The older raw-boundary QA script uses a different mask and remains identified
separately. Its mean black boundary error fell from 6.20 to 2.55 original pixels.

The first multi-object atlas missed the pedestal. A separate pedestal bake
corrected the disk image, but the reopened file still held stale packed bytes.
A fresh image loaded and packed from the exact PNG fixes it. The selected
fixed render differs from the pre-bake material by 0.186/255 mean foreground
RGB, and the side render by 0.126/255, both with identical alpha. The delivered
render differs from the selected reopened trial by 0.000038/255.
The 3072-pixel atlas contains pigment only. Its packed bytes match
`assets/knight/wood-atlas-v1.png`.

All nine mesh components remain closed, connected and positive-volume. Both
eyes pass socket-intersection checks. The WebGL export retains 203,602 triangles
and every evaluated position, corner normal and atlas UV; exact duplicates are
shared. The Node DOM/WebGL harness tested orbit, zoom, pan, reference reset,
horse front/side presets, wood/neutral, and registered side comparison.
Maximum sampled camera discrepancy was below 0.000025 pixels. A native
browser GPU inspection has not been performed for this checkpoint.

Current model SHA-256: `d10b2b09377981b915ac8fd418c7c654fdec6e6b6f9f631d8971276dcbcf67b7`. The reference images, gallery defaults
and historical camera studies are preserved. The goal is active. Next examine
the eye and socket, the thin swept ear, and the lower mane: these remain
visibly different in the elevated image. The chest needs a stronger carved
ridge and corresponding broken reflection, the poll highlight is too broad,
and some pigment follows residual shading on the side. The fixed image is
visibly short of completion.

See [the comparisons and all trial decisions](knight-mission/iteration-001/scores.json).


## Checkpoint 002 | Eye socket, brow and lower mane

The first walnut model at `ab58349` is archived in `history/knight/mission-001`.
Its fixed-view eye was visible at only 18 samples on a two-pixel grid. The reference shows a long inset eye below a swept brow. The lower mane also disappears sooner in the old carving than in both registered originals.

Two bilateral recesses now join the continuous skull, and the closed convex eyes sit into their floors. The forward end of each swept ear sits closer to the forehead. A height-dependent change fills the lower mane and brings its termination forward. Two small area lights reflect off the eyes. The wood pigment stays fixed and the highlight moves with the viewing direction. Selected black candidate 2 supplied the detailed target and the original black sprite guided the mane fit.

| Trial | Outline | Form | Wood color | Grain | Lighting | Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 009-carved-eye | 94.33 | 73 | 78 | 67 | 39 | 70.27 |
| 010-convex-eye | 94.33 | 75 | 78 | 67 | 39 | 70.67 |
| 011-seated-brow | 94.24 | 75 | 78 | 67 | 38 | 70.45 |
| 012-lower-carving | 95.29 | 77 | 78 | 67 | 40 | 71.46 |
| 013-eye-reflection | 95.29 | 77 | 78 | 67 | 43 | 72.06 |

The working mean rose from 70.07% to **72.06%**. The measured silhouette overlap rose from 95.08% to 95.81% on original black, from 94.33% to 95.29% on the selected reference and from 94.60% to 95.09% on mirrored white. The other four scores are visual judgments. The five-category mean includes the silhouette once. Independently, the unfilled-boundary check measures 2.05 original pixels of mean error.

The visible eye now spans 52 by 20 pixels and 223 two-pixel grid samples. Its iris still reads too orange and too uniformly lit. The original has a darker tapered socket, a stronger compact glint and a bright lower rim. The body retains its earlier grain and chest reflection discrepancy. The side view retains a recognizable broad jaw, tapering muzzle and arched neck.

The reopened Blender model rendered at 96 Cycles samples at the existing 54-degree camera and the registered 7-degree side camera. Both delivered images have the selected trial's exact alpha. Their foreground mean RGB changes are 0.000044/255 and 0.000048/255. The pedestal vertices, normals and pigment UVs are byte-identical to checkpoint 001. The maximum height, floor and camera matrices also match. All nine connected shells passed manifold and positive-volume checks. Both eyes intersect their sockets. The packed atlas matches the external PNG. The Node viewer harness passed all controls and sampled the camera within 0.000030 pixels.

Accepted model SHA-256 `68e2e1a41f06bf19ff843bc0c0d2d042f1f846bef4f1447c00048b2cb96fb07f`. The review uses the fixed and side renders and the exported mesh from that scene. Next compare the two chest highlights, the broad mane reflection and the collar against the original. [Trial decisions and scores](knight-mission/iteration-002/scores.json) and [enlarged eye comparison](knight-mission/iteration-002/eye-comparison.png).


## Checkpoint 003 | Reflections on the carved chest

The second checkpoint at `d91c807` supplied the geometry and baseline finish. At 54 degrees, both originals and selected black candidate 2 show a pair of diagonal reflections on the chest. The accepted carving had a faint tonal streak there. The wider shoulder, thin chest ridge and lower portion of the mane are distinct surfaces in the reference.

The first trial traced the original camera rays through the exported triangles, interpolated their surface normals and placed finite area lights along the corresponding mirror directions. Actual Cycles response passes determined their powers. The initial panels exposed the chest carving but added smooth stripes and light across the jaw. Narrower beams improve the placement. Relief taken from fine local changes in the walnut pigment breaks up the highlights. The deeper experiment looked leathery. The retained relief distance is 0.0028 model units.

Two more response passes measured a satin finish and a burnished finish on the same walnut. A bounded scalar at each camera-visible control vertex selects the local mixture. The far side uses the baseline finish where the picture provides no evidence. The renderer recomputes reflections as the camera or lights move. Pigment, surface relief, varnish and light remain separate in the editable scene.

| Trial | Outline | Form | Wood color | Grain | Lighting | Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 014-chest-panels | 95.29 | 77 | 77 | 67 | 47 | 72.66 |
| 015-grain-polish | 95.30 | 77 | 77 | 56 | 45 | 70.06 |
| 016-burnished-grain | 95.30 | 77 | 78 | 69 | 50 | 73.86 |
| 017-fitted-varnish | 95.30 | 77 | 80 | 71 | 56 | 75.86 |

The working mean rose from 72.06% to **75.86%**. Original, selected and mirrored-white silhouette overlap are 95.81%, 95.30% and 95.09% respectively. The fixed camera and complete position/normal/UV/index buffer are byte-identical to checkpoint 002. Form remains at 77. Wood color, grain and lighting remain visual estimates.

Mean absolute RGB error over the common opaque foreground fell from 16.64 to 14.19 on a 0–255 scale. The chest went from 21.31 to 19.48. The first smooth-light trial increased the full error to 18.22 even as the ridges became visible, which is why it was rejected. The final chest streak remains broader and cooler than the source, with too little light on the outer shoulder. The real nose and eye still lack carving detail.

The actual reopened scene rendered both registered views at 144 Cycles samples. The delivered fixed and side alpha match the selected trial exactly, with foreground mean RGB deltas of 0.000051/255 and 0.000036/255. Both eyes and all nine connected mesh shells passed validation. The browser now loads the evaluated varnish coverage for every exported vertex and uses the same pigment and grain relief distance. Its preview lighting is approximate. Headless Microsoft Edge with ANGLE SwiftShader compiled and drew the shader, switched wood and neutral, changed camera presets, orbited on drag and opened both comparisons.

Accepted model SHA-256 `bfe004b7e1653b52fc6f577e68b27b9da88421babf639883e84441318a48416f`. [Four-view comparison](knight-mission/iteration-003/comparison.png), [registered side comparison](knight-mission/iteration-003/side-study.png), [trial scores](knight-mission/iteration-003/scores.json) and [browser views](knight-mission/iteration-003/browser-views.png). Next examine the carved nostril, mouth opening and dark lower eye against both originals.


## Checkpoint 004 | Conical muzzle, nostrils and inset eyes

Recorded 2026-11-05 from local commit `786501b`.

The previous muzzle was too blunt at the front and its lower jaw receded too soon. Both original colors show a curved nostril near the end of the snout. The chosen high-resolution image also resolves a shallow crease extending back from that cut. A fit weighted 83% toward the black original advanced the tip by 0.028 model units, raised it by 0.092 and lowered the rear underside by up to 0.098. The second cut reduced the nostril depth to 0.054 and the mouth depth to 0.014. Both flanks of the editable skull and the continuous outer carving received the same change.

The eyes and the deepest carved surfaces received a restrained walnut tone. For the reshaped face, two actual Cycles renders measured the response to a known change in diffuse pigment. A neutral reflection term separates glare from a bounded wood-color estimate. Camera depth and the surface normals determine which existing pigment texels can receive that estimate. This adjustment is attached to the three-dimensional surface. All other components retain their former tone from trial 020.

| Trial | Outline | Form | Wood color | Grain | Lighting | Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 017-fitted-varnish | 95.30 | 77 | 80 | 71 | 56 | 75.86 |
| 018-carved-muzzle | 95.57 | 78 | 79 | 71 | 55 | 75.71 |
| 019-fine-nostril | 95.57 | 80 | 79 | 71 | 56 | 76.31 |
| 020-dark-carved-wood | 95.57 | 80 | 81 | 71 | 56 | 76.71 |
| 021-registered-muzzle | 95.57 | 80 | 83 | 73 | 56 | 77.51 |

The working mean is **77.51%**. Original black outline overlap is 96.22%, selected black is 95.57% and mirrored white is 95.44%. The other four categories are visual assessments. The independent holistic estimate is 73–79%.

On the common opaque area, selected-reference RGB error fell from 10.36 to 8.91 on the muzzle, 17.51 to 16.14 around the nostril and 26.90 to 21.46 around the eye. The whole foreground improved from 14.19 to 13.92 on a 0–255 scale. The later grading pass changed sampled triangle centers only on the continuous head and neck. The outer silhouette now follows the original more closely, though the modeled eye remains short and the nostril still has pinpoints of reflected light where the source shows a lower crescent. The large forehead and swept ear still miss the original glints.

The delivered 144-sample fixed and side renders reproduce the selected reopened trial with identical alpha and mean foreground RGB differences of 0.000038 and 0.000032 on the 0–255 scale. All nine closed shells passed validation and both eyes meet their sockets. The camera, maximum height and floor match checkpoint 003. The live viewer contains the actual pigment UVs, atlas and varnish coverage. Its lights are approximate. The Node interaction checks and headless Edge/ANGLE SwiftShader tests passed. Accepted scene SHA-256 `2a661dbd11c46d1929d4e7a901924213e1ecf3683aff001fde523a6073833c88`.

Next, trace the forehead and swept ear reflections on the actual carving and compare the deep cheek crease with the black and mirrored white originals. [Trial decisions](knight-mission/iteration-004/scores.json) and [registered comparisons](knight-mission/iteration-004/comparison.png).


## Checkpoint 005 | Swept ear, brow reflection and forehead

Recorded 2026-11-05 from local commit `1b952e4`.

Ray intersections showed that the bright patch on the reference ear landed on the mane in the prior model. Eleven approximate image landmarks put the model's upper ear edge an average of 17.36 pixels below the intended contour. The first trial enlarged the paired blades vertically and exposed the patch. Its far-side ear protruded above the original skyline, so the trial was rejected. The second trial put more width toward the inside of each swept blade, with a smaller rise. The upper-edge discrepancy fell to 3.09 pixels on those same landmarks. The near ear's lower edge retained the same sampled rows. These are interpreted internal feature measurements, separate from the measured outside silhouette.

The revised wood responds to real area lights. One scene with a satin finish and another with a burnished finish measured the available reflection range. Updated coverage is limited to the swept ears and nearby face. Two diffuse response passes guided the restrained wood-tone correction on the visible ear and forehead, with the existing pigment providing the underlying hue and hidden wood. Finally, four compact light placements were compared against the prior broad ear light. A 0.15-unit disk at 2.67 watts gave the best measured crop match. The final scene retains one replacement.

| Trial | Outline | Form | Wood color | Grain | Lighting | Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 021-registered-muzzle | 95.57 | 80 | 83 | 73 | 56 | 77.51 |
| 022-broad-swept-ear | 95.16 | 78 | 81 | 72 | 55 | 76.23 |
| 023-flat-swept-ear | 95.67 | 82 | 81 | 72 | 55 | 77.13 |
| 024-brow-reflections | 95.67 | 82 | 81 | 72 | 57 | 77.53 |
| 025-brow-polish | 95.67 | 82 | 82 | 72 | 58 | 77.93 |
| 026-registered-brow | 95.67 | 82 | 84 | 74 | 58 | 78.73 |
| 027-focused-brow | 95.67 | 82 | 84 | 74 | 59 | 78.93 |

The working mean is **78.93%**. Original black outline overlap is 96.37%, selected black is 95.67% and mirrored white is 95.60%. The other four categories are visual assessments. The independent holistic estimate is 74–80%.

The strongest ear patch remains broader and more forward than the reference. Its mean absolute RGB error nevertheless fell from 45.90 to 34.29 on a 0–255 scale. Error on the forehead fell from 12.22 to 8.97 and around the lower lid from 23.07 to 19.46. The complete brow region changed only from 16.71 to 16.54. This limits the lighting score. The broad glint on the poll, the shape of the lower eyelid and the thin front collar reflection remain visibly different. The side guide is an independent anatomy check, and its more continuous brow still guides future carving.

The delivered 144-sample fixed and side renders reproduce the selected reopened trial with identical alpha and mean foreground RGB differences of 0.000051 and 0.000035 on the 0–255 scale. All nine closed shells passed validation and both eyes meet their sockets. The camera, maximum height and floor match checkpoint 004. The live viewer contains the actual pigment UVs, atlas and varnish coverage. Its lights are approximate. The Node interaction checks and headless Edge/ANGLE SwiftShader tests passed. Accepted scene SHA-256 `95e938f47b58c7fd48de6fd0b2158092d0cf1490b57ab505ddc8f356120b4cd1`.

Next, fit the foot groove and upper collar against the original's curved edges, then verify the wood and lighting on those surfaces. At 54 degrees the front foot glint measures near row 1010 in the original and near row 1000 in the model. [Trial decisions](knight-mission/iteration-005/scores.json) and [registered comparisons](knight-mission/iteration-005/comparison.png).
