# Round 16 · The carved edge of the mane

**Candidate A wins.** Above the swept ear, A has one sharp edge with a broad, quiet face underneath. The edge turns down where the mane meets the forehead. That shape reads in profile, under a moving softbox and on the opposite flank. B moves the glint closest to the two black references, but adds a second band across the underside. It makes the mane look layered as the knight turns. [Fixed reference and three models](head.png) · [The same three profiles](side-face.png) · [Both black references and the carved forms](poll-views.png)

| Model | Reference · 45% | Profile · 35% | All-around form · 15% | Finish · 5% | Weighted |
| --- | ---: | ---: | ---: | ---: | ---: |
| Parent 15A | 96.9 | 96.7 | 94.5 | 93.4 | 96.30 |
| **16A** | **97.0** | **97.3** | **95.0** | **93.6** | **96.64** |
| 16B | 97.7 | 96.2 | 94.3 | 93.9 | 96.48 |

These scores record the artistic decision for the whole piece. The camera holds at 54° for the reference and 7° for the registered side. Both candidates preserve the accepted eye. The whole-piece views show how much of the difference survives at playing size. [Whole reference view](fixed.png) · [Registered side](side.png) · [Board-size detail](poll-native-grid.png)

## Why the edge matters

In black candidate 2, the curved line of light separates the top of the mane from a dark plane. The original sprite shows the same single division. We traced that line onto the actual exported surfaces. In the middle section, 80% of the measured turn in surface normals spans 22.45 pixels on the parent, 17.41 on A and 29.36 on B. The wood directly below the edge grows brighter again by 0.28 luminance levels in black candidate 2, 1.21 in the parent, 0.21 in A and 23.05 in B. That second band on B also appears on a grey polished surface and in the near and far profiles under a light moving across the horse. A preserves one cleaner carved face. [Physical bevel sections](bevel-sections.png) · [Walnut, pigment and polish](crest-finish.png) · [Near flank](raking-poll-near.png) · [Far flank](raking-poll-far.png)

B gives the most accurate placement of the separate reflection on top. Its center is at x435, against x435 in the original, x438 in black candidate 2, x380 on the parent and x405 on A. With its own lamps B also gives the closest average color across the fixed crest crop. A improves the warmth and forward bend, but still has a bright patch at the forehead joint. Under the common studio neither challenger improves the parent’s mean RGB error across this crop. A wins on the shape of the cut and its appearance through a turn. [Glint positions](front-cap-glint.png) · [Controlled studio](poll-studio-comparison.png) · [Reference curve in profile](upper-mane-side.png)

A changes the mane and its seat in the skull. Measured across five paired sections, the two sides agree to within 0.0000015 model units. The fixed and side outline overlaps against the parent are 99.994% and 99.978%. The eyes, ears and pedestal retain their geometry. The verified viewer mesh has seven parts and 288,430 triangles. The same atlas runs from the front through the back, and the back-quarter views show where the wood reflects the new cut. [Native geometry](A/native-proof.json) · [Back in walnut](back-walnut.png) · [Frozen scenes and export checks](judge-verification.json)

## Reproducing this round

Use a working copy at `eeb1016`. For each candidate, place its lettered evidence files under `build/knight-mission/improvement-016-A` or `improvement-016-B`. Copy the parent model from `models/knight/knight-rebuilt.blend` to `parent.blend` in both folders. Use `assets/knight/render.png` for `parent-wood.png` and `assets/knight/guide-render.png` for `parent-side.png`. Copy the released `wood-atlas-improvement-014-B.png` from the same asset folder to `pigment.png` for A and `parent-pigment.png` for B. B’s additional grain seed and recipe are in its lettered folder. A documents its Blender commands and B supplies a PowerShell replay script. [A’s assessment](A/assessment.md) · [B’s replay](B/reproduce.ps1) · [B’s source digests](B/support.json)
