# Bishop 026 · A shorter bishop beside the queen

On the ruler from Toby’s lineup, the bishop now stands at **74.48% of the king’s height**, down from 81.94%. The queen stands at 83.29%. The 026 bishop has an editable height of **4.13599** and a foot diameter of **1.93652** model units. Those are 90.90% and 94.80% of checkpoint 025. [Open the bishop review](../../../bishop-review.html)

![King, queen, bishop 025 and bishop 026 at the original board scale](frozen-lineup.png)

The lineup uses the king, queen and board records from the revision shown in Toby’s screenshot. Both bishops share one pixel scale and one floor. The 100% scale, 90.9% height and 94.8% width controls in the screenshot were applied once. The original queen-to-king relationship reproduces the displayed 83.3% to one decimal place. A fresh automatic fit to each piece’s rendered height can make the smaller bishop look taller. [Frozen ruler and screenshot measurements](side-target.json)

Applying the board’s per-piece height-fit formula to the delivered bishop render gives **80.96%** on the same king ruler. The formula enlarges the shorter 54° render until its image spans the old sprite height again. The **Side height comparison** link on the bishop review opens the fixed-scale lineup above.

## Where the height came out

| Section | Bishop 025 | Bishop 026 | Height removed |
| --- | ---: | ---: | ---: |
| Sole through first stem support | 1.2772 | 1.2107 | 0.0664 |
| Exposed stem through the collar underside | 1.4724 | 1.3001 | 0.1724 |
| Collar stack | 0.6227 | 0.5546 | 0.0681 |
| Mitre and button | 1.1778 | 1.0706 | 0.1072 |

The foot, groove, flare, socket and first stem support keep all 40 queen and king control rings. Every radius and height there scales by 0.948 relative to 025. The full turning is now 92.7144% of the donor’s native size. The largest change above it is in the exposed stem. Its waist moves down as the stem shortens. The collar stack takes an independent cut in height and radius. The head and its button both keep 96.53% of their previous width and 90.90% of their height.

The live diagonal cutter follows the mitre. Three rays pass through the slit, and the rays beside it hit wood. The floor is solid. The button still meets the curved head in one transition across 84.6% of the button width. Both editable components are closed. [Reopened-model audit](validation/mission-validation.json) · [Slit and contact measurements](validation/validation.json)

## How the trials compare

| Version | Side outline overlap | Mean side edge error | Original white at 54° | White candidate 3 at 54° |
| --- | ---: | ---: | ---: | ---: |
| Bishop 025 | 80.10% | 4.71 px | 97.39% | 96.84% |
| More height from the stem | 95.95% | 1.07 px | 84.54% | 83.73% |
| More height from the collars and mitre | 94.99% | 1.31 px | 86.17% | 85.30% |
| Balanced | 98.34% | 0.43 px | 85.23% | 84.42% |
| Closest side fit | 98.81% | 0.31 px | 85.38% | 84.58% |
| **Accepted 026** | **98.16%** | **0.48 px** | **85.63%** | **84.77%** |

The target is the visible outline of the 221-pixel-tall bishop in Toby’s screenshot. It spans 104 pixels across the foot. Each test used the same conversion from native model units to screenshot pixels. The original sprite and selected enlargement kept the same orthographic camera, pixel scale, center and crop throughout.

The accepted version gave the highest original-white overlap among trials within 0.75 screenshot pixels of the requested side outline on average. That tolerance is an interpretation for this study. Against the closest side trial, the accepted version gives up 0.17 screenshot pixels of average edge accuracy and gains 0.24 percentage points against the original. The more compressed collar and mitre trial scored higher against the original but visibly misplaced the collar stack in profile. [All five side trials](side-trials.png) · [Measurements from the saved meshes and renders](measurements.json)

![Owner’s lineup crop and level renders, with the target outlined in gold](side-comparison.png)

## What the 54° comparison shows

The reduced height is visible at the fixed camera. The button begins at render row 228, down from 164 in bishop 025. The registered original begins around row 156. The front collar crests land at rows 551, 599 and 638, below the original troughs near 513, 568 and 612. The narrower foot brings the center of its groove up from row 1075 to 1066, closer to the original trough near 1052. Original-white overlap falls by **11.76 percentage points**. Original-black overlap is 86.43%. [Original outline and model edge](comparison/original_white-contours.png)

![Registered original, selected enlargement, previous bishop, accepted bishop and neutral geometry](fixed-comparison.png)

Against the selected enlargement, the outline overlap measures 84.77%. I rated interior form 74%, wood color 82%, grain and surface texture 76%, and lighting 70%. The mitre, slit and collar forms are recognizable, with visible vertical displacement. The gold boxwood, darker stem and streaks on the flare survive the edit. The fixed render still carries bright inherited reflections and darker marks whose placement shifts with the surface. These four ratings are visual judgments. The full reference match remains unfinished. [Scores](scores.json) · [Previous checkpoint](../iteration-025/assessment.md)

## Reproduction

The starting Blender file and original 025 display assets are archived in `history/bishop-mission-025`. The exact regional controls are in [side-refit.json](side-refit.json). `scripts/bishop/side_refit.py` builds, saves and reopens each editable trial, then renders it in level view and at the fixed 54° camera. `fit_side_refit.py` proposes the last two variations from the side contour, fixed-camera outline and front collar positions. `compare_side_refit.py` measures the final rendered versions. The comparison and rotating mesh are generated from the same accepted scene. [Local HTTP verification](validation/served.json)
