# A rounder king crown

The shoulder slopes continuously from the broad rim to the lower seat ring. The two rings are 4.5% narrower and the cross sits 0.028 Blender units lower. The cross spans 2.2% less width and its tip is 0.044 units lower. The turned shoulder, both beads and the cross are physical features of the editable model. [King review](../../../king-review.html#crown-seat)

![The imagined side guide and both king models above, with the original Lichess sprite and both fixed renders below](crown-comparison.png)

## What the two views show

The previous shoulder flattened near the wide rim, then rose sharply near the seat. Across the visible shoulder of the current mesh, the slope eases steadily toward the center. The two ring crests sit at 4.195 and 4.299 above the floor. The profile beneath the head preserves the queen-derived base, the stout socket and the collar stack. [Mesh measurements](mesh-measurements.json)

In the level render, the shoulder's mean outline error against the imagined guide falls from 4.65 to 0.38 pixels. This measures the top silhouette at 60 columns with a level-camera scale of 150 pixels per Blender unit. The scale comes from matching foot widths. For this crown detail, the guide is centered on the wide shoulder. The full side comparison in the viewer still aligns both pieces at the floor. The guide leaves the cross's front-to-back thickness open to interpretation.

At the same 54° camera, the full silhouette overlaps the original by 95.21% and the selected enlargement by 96.39%. The earlier figures were 95.21% and 96.45%. The original sprite crops the cross tip. Its arm edges and both ring reflections remain visible. [Reference measurements](crown-fit.json)

## Cross trials

The first two versions shortened the cross uniformly and its arms fell too low in the original view. Giving the cross more depth improved the outer silhouette but widened the visible top faces. The final trials adjusted the arm heights separately. The selected model has a cross depth of 0.191 units, compared with 0.174 before. Its upper post is still taller in profile than the imagined one. The cross face and varnish highlights differ from black candidate 1. Its grain also looks softer than the high-resolution wood.

| Trial | Side shoulder error, px | Whole original overlap | Whole candidate overlap | Cross-face luma error against candidate, 0–255 |
| --- | ---: | ---: | ---: | ---: |
| Previous king | 4.65 | 95.21% | 96.45% | 4.71 |
| 191 | 1.38 | 94.78% | 95.89% | 15.30 |
| 192 | 1.45 | 94.23% | 95.32% | 19.98 |
| 193 | 0.38 | 95.25% | 96.49% | 19.76 |
| 194 | 0.38 | 95.24% | 96.40% | 16.73 |
| 195 · current | 0.38 | 95.21% | 96.39% | 8.20 |

Visual estimates are 90/100 for interior form, 82 for wood color, 80 for grain and surface, and 69 for lighting. The silhouette figures use intersection over union. They measure outline agreement only. [Configurations and full scores](checkpoint.json)

## Reproduction

Open Blender in background mode with `scripts/king/round_crown.py` and pass the [configuration](reproduction.json) after `--`. Add `--validate` to reopen the source and trial, check the exposed dome curvature and measure both ring crests. The source is the archived two-ring king from checkpoint 018. The standard export and saved-file render scripts produce the fixed, level and rear views. Run `scripts/king/compare_rounded_crown.py` with the configuration and an output folder to regenerate the comparison plate and measurements.

The checks cover both closed mesh components, the evaluated turning profile, exact UV and normal export, all nine light receivers, the pigment atlas and the fixed camera. A separate Blender reopen reproduced the beauty render within one 8-bit level. The local king review embeds the same exported mesh and the side-by-side comparison. [Delivery checks](delivery.json)
