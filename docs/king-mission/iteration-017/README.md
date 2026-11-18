# King 017 · A shared queen and king base

The king uses the queen’s entire editable turning from the floor, through the single groove and flare, to the top of the socket. Both bases use one model unit at the same scale in all three axes. The first row of the stem supports the join to the king. The stem above that join, the collars, the flared head and the cross come from king 016. [Current reconstruction](../../../king-review.html)

![Queen, previous king and revised king, with a common floor and real-world display scale](base-comparison.png)

The previous king sampled 28 of the queen’s base rings and adjusted their radii and heights separately. This version includes all 39 rings plus the adjoining stem support. It preserves all the queen’s coordinates at the king’s 96 angular divisions. Subdivision accounts for the small residual difference in the final surface.

| Evaluated dimension in model units | Queen | Previous king | Revised king |
| --- | ---: | ---: | ---: |
| Foot diameter | 2.0893 | 2.0609 | 2.0880 |
| Height of the groove center | 0.2315 | 0.3039 | 0.2345 |
| Height of the flare’s outer crest | 0.3339 | 0.3785 | 0.3390 |
| Socket diameter at height 1.0 | 1.0587 | 1.0967 | 1.0581 |

The largest measured distance between the subdivided side profiles fell from 0.05365 to 0.00135 model units over heights 0.006–1.225. That is about 0.20 pixels at the king side camera’s native 150 pixels per unit. The comparison image uses known camera scales and a shared floor. [Mesh measurements](profile-measurements.json)

## Finish

The lower turning takes the queen’s actual roughness of 0.19, coat roughness of 0.075 and specular IOR level of 0.5. The finish fades into the king’s stem. The king retains its own wood atlas and grain. Four glossy area lights place small reflections on the flare, the two bevel edges and the socket. Their positions and powers were fitted to corresponding highlights in the saved queen side render.

The first geometry-only trial had a flat-looking foot. Matching the varnish alone still left the flare without the queen’s highlight. The first reflectors were too bright. A calibrated version matched the peaks, but its main glint was small. Moving the reflector closer broadened the glint and reduced its spill in the overhead view. In the final side render, the four measured peak luminances fall within two 8-bit levels of the queen. The queen’s grain and the widths of individual reflected bands still differ. [Side highlight measurements](base-light-comparison.json)

## Fit to the king references

![Black Lichess sprite, selected black candidate 1 and revised king under the same 54-degree registration](fixed-comparison.png)

| Silhouette intersection over union | King 016 | King 017 |
| --- | ---: | ---: |
| Original black Lichess sprite | 96.89% | 95.21% |
| Selected black candidate 1 | 97.56% | 96.45% |

The shared base extends farther at the lower flanks in this camera. The original sprite remains the reference for evaluating that discrepancy. The absolute width and shape of the queen base were the owner's priority for this revision. The upper-face reflection and lower-right flare glint are still broader and brighter in parts of the model than in the selected photograph.

The visual estimates are 87/100 for interior form, 82 for wood color, 80 for grain and surface, and 69 for fixed-view lighting. Only silhouette overlap and the reported dimensional and luminance checks are measurements.

## Reproduction

Pass [reproduction.json](reproduction.json) to `scripts/king/match_queen_base.py` in Blender 5.2. The configuration pins the archived king 016 and current queen 033 by SHA-256. If the queen has advanced, point a copy of the configuration at its archived 033 Blender file. The builder interpolates the king’s UVs and finish fields onto the extra loops. Its stored profile-ring coordinates preserve the existing nine light regions when the surface is regenerated.

Run `scripts/king/validate_queen_base.py` with the configuration and an output JSON path. The test reopens the donor and staged scene, checks the geometry, old UV samples, packed wood, cross, lights, camera and material scope, and measures the two subdivided meridians. The two closed components export with positive volume and exact position, normal and UV round trips. Independent fixed beauty renders agree to one RGB level with identical alpha. [Checkpoint evidence](checkpoint.json)

Regenerate the two comparison images and highlight measurements with `scripts/king/build_base_comparison.py`, passing the same configuration and an output directory. The local review, Windows preview and whole-set view use the revised king. The historical sizing audit still flags three older knight hashes. [Delivery checks](delivery.json)
