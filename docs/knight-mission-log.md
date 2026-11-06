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
