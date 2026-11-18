# Bishop 025 · The shared Staunton base

The bishop now uses the complete turning from queen 033 and king 017. Its foot measures 2.04274 model units across, up **1.48%** from bishop 024. Its height from the same floor is 4.55005 units, down **0.91%**. The original white Lichess sprite guided the bishop's upper geometry at the saved orthographic camera, 54° above the board. The selected, ungraded white candidate 3 supplies finer visual detail. [Bishop review](../../../bishop-review.html) · [Whole-set models](../../../set-comparison.html#models)

![Level base comparison, from left to right: queen 033, king 017, bishop 024, bishop 025](equal-foot-bases.png)

Each foot spans 220 pixels in this comparison. All four images come from level renders of the evaluated models under the same neutral lighting. The bishop takes all 39 rings from the sole to the top of the socket, plus the first stem support, at 97.8% of the queen's native size in all three dimensions. Its 128 angular segments carry the same radial cross-sections. At equal foot diameter, the maximum sampled distance between the queen and bishop base profiles fell from **0.21277 to 0.00106** queen units. The king measures 0.00121 units against the queen using the same method. The socket seats into the bishop's own tapered stem.

## Choosing the proportions

| Saved variant | Foot diameter | Height | Original white outline overlap |
| --- | ---: | ---: | ---: |
| Previous bishop 024 | 2.01302 | 4.59201 | 98.774% |
| Shared wider base, original height | 2.05527 | 4.59201 | 97.169% |
| Same wide base, stronger shortening | 2.05527 | 4.50903 | 96.368% |
| Moderate width and shortening | 2.04274 | 4.55402 | 97.197% |
| Upper refit | 2.04274 | 4.55005 | 97.395% |
| **Accepted bishop 025** | **2.04274** | **4.55005** | **97.387%** |

![All six saved versions in true level view, at one scale and a common floor](level-trials.png)

At the stronger shortening the side profile is more compact, but the top of the button drops too far in the fixed view. The accepted version lowers the mitre and its saw together by 0.020 units. It takes a further 0.022 units from the button's dome, preserving the underside that seats on the head. The collars move down 0.013 units, with small radial corrections. On the reopened mesh the button contacts the head across about **85% of its width**. Rays pass through the diagonal slit, strike the material immediately beside it and find a solid floor underneath.

## What lines up in the original

![Original Lichess sprite, selected enlargement, previous bishop, wider trial, shorter trial and accepted bishop at fixed registration](fixed-comparison.png)

Mean absolute left/right edge error across the mitre falls from **2.04 to 0.97 px**, across the collars from **1.51 to 1.11 px**, and across the exposed stem from **1.09 to 0.98 px** versus bishop 024. The actual front collar rims project to rows **512.4, 566.1 and 609.4**. The original has dark troughs around 513, 568 and 612. These troughs are optical landmarks just under the edges and have some width.

The first upper refit used several rows where the sprite starts to show the back of the base. Including them made the exposed stem too wide. Restricting that correction to rows 595–613 lowered the measured stem error from **2.09 to 0.98 px** across rows 594–615, at a cost of 0.008 percentage points of whole-silhouette overlap. The final comparison uses the same camera, floor, image registration and mask conventions for every trial. [Neutral overlay comparisons](neutral-comparison.png) · [Head and collar detail](head-comparison.png)

## Where the shared base differs

The original white silhouette still fits the old bishop better overall. The new base sits lower behind the stem. Across rows 630–789 its mean edge discrepancy grows from **2.03 to 13.62 px**, and across the outer foot region from **1.57 to 3.46 px**. The groove's physical center projects to row **1074.7**. The dark groove at the front of the original centers on row **1052**, and on **1053** in the selected enlargement. Pigment and shading also affect the dark band's location. The same difference is apparent in the neutral geometry. The new button edge is about 0.58 px farther from the original on average. [Base outline detail, gold original and blue model](base-contours.png)

The accepted silhouette overlap is **97.39%** against the original white, **96.84%** against white candidate 3 and **96.47%** against the original black. The shared-base shape and refined upper fit were the reasons for accepting this checkpoint. The inherited boxwood retains photographic shading and bright reflections. The original finish and the full visual match remain unfinished. [Measurements for all variants](measurements.json)

## Reproducing the checkpoint

The archived bishop 024, original donor file paths and SHA-256 hashes are in [turning.json](turning.json). If the queen advances, use its archived 033 Blender file with the listed digest. The king file is archived at 017. The staged cases are named `wide`, `short`, `moderate`, `refit` and `registered`. In Blender 5.2, pass a case after `--` to `scripts/bishop/shared_turning.py`. Use `--samples 384` for the last two cases. The builder saves and reopens the editable bishop before rendering the two fixed materials. The declared case values reproduce the geometry directly. The fitting script documents how the last two profiles were proposed.

`scripts/bishop/inspect_shared_turning.py` takes the donor and case names to produce level renders, sampled meridians and projected interior landmarks. `scripts/bishop/mission_compare.py` compares the fixed render with the registered sources. `scripts/bishop/compare_shared_turning.py` draws the comparison sheets and measures the normalized profiles.

The current mesh has two closed editable components and a live Boolean saw. The lower mesh interpolates the bishop's original UVs and pigment coverage through the extra rings. The original upper UVs, packed images, material graphs and lights are preserved. The two render surfaces are regenerated from the evaluated mesh, with the socket's light region following its new height. The fixed review and exported rotating mesh use the same saved camera. [Geometry and material audit](validation/mission-validation.json) · [Delivered HTTP assets](validation/served.json)
