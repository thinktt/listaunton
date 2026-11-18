# King 018 · Two rings under the cross

The crown seat is the small turned support between the broad top of the Chavet-style head and the cross. Both original sprite colors show two concentric edges. The selected black candidate shows a rounded upper ring sitting inside the footprint of a wider lower ring. The side guide supplies an interpretation of their thickness. [King review](../../../king-review.html)

![The registered crown details above and the level side profiles below](crown-seat-comparison.png)

The previous mesh had one crest in its side profile. The revised mesh has two rounded crests in the same continuous wooden body, with a recessed groove between them. The upper ring measures 84.7% of the lower ring’s diameter. The cross extends into the center of the seat. The crown wall, collar stack and queen-derived base keep their accepted shapes. [Evaluated mesh dimensions](mesh-measurements.json)

| Model dimension | Lower ring | Upper ring |
| --- | ---: | ---: |
| Diameter in Blender units | 0.7085 | 0.5999 |
| Crest height above the floor | 4.2118 | 4.3243 |

## Fit at 54°

The two front highlights fall at rows 223 and 250 on the 1,254-pixel comparison canvas. The selected image puts them at 222 and 249. The original sprite has broader highlights a little higher, at 215 and 243 after registration. The upper groove falls at the same row as the selected image. The darker lines under both rings are softer and lighter in the model. [Front arc measurements](front-arc-measurements.json)

The first two-bead trial placed the seat too low. Raising it aligned both highlights. Tightening the undercuts and rounding the shoulder into the lower bead then gave a stronger separation in both the side and fixed views. The mean absolute difference in 8-bit luma in the same crown patch fell from 23.26 to 21.06 against the original and from 27.98 to 22.47 against black candidate 1.

The complete silhouette overlaps the original by 95.21% and the selected image by 96.45%. The rings lie inside that outline. The visual estimates are 89/100 for interior form, 82 for wood color, 80 for grain and surface, and 69 for lighting. The measured patch and silhouette comparisons are recorded separately from those estimates. [Trials and scores](checkpoint.json)

## Reproduction

Run Blender’s `scripts/king/turn_crown_seat.py` with the [configuration](reproduction.json) after `--`. The script reads the pinned king 017 archive, sets the radii and heights of logical profile rows 74–87, regenerates the light receivers and saves a staged Blender scene. Run the same command with `--validate` after the configuration to reopen both scenes and measure the subdivided mesh.

Use the standard fixed, profile, rear and export pipeline from the king build guide. Run `scripts/king/compare_crown_seat.py` in ordinary Python with the same configuration and an output directory to regenerate this comparison. The model and its previous version use one level camera. The side guide is scaled by the foot and centered on the broad crown shoulder for the detail crop. [Viewer and local delivery checks](delivery.json)
