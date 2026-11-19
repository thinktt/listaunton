# Bishop 027. Fitting the original at the chosen height

The bishop stands at **74.48% of the king**, with its sole at zero and its button at **4.135986328125** model units. Against the original white Lichess sprite at the saved 54° camera, outline overlap rose from **85.63% to 95.72%**. White candidate 3 rose from **84.77% to 95.31%**. The comparison uses the original scale, registration and floor. [Open the interactive bishop review](../../../bishop-review.html)

![Original sprite, selected enlargement, previous bishop, new bishop and new untextured bishop in the same camera frame](fixed-comparison.png)

## What made the bishop look swollen

In the owner’s recording, the grey collar faces and lower turning looked inflated when switching from the reference. A single outside-width score missed these internal edges. The surviving frame comparison shows the reported defect on that earlier mesh. [Frames 107 and 131 from the recording](../iteration-019/owner-recording-detail.png)

On 026, the three front collar rims landed about 26–36 pixels below their corresponding dark troughs. On 027 they land at rows **516.7, 566.6 and 610.8**, compared with **515, 567 and 611** in the original. These are separate measurements of a physical rim and a photographic shadow. Across the collar region the average absolute half-width error is now **0.83 pixels**. The foot at its widest spans 529 pixels, compared with 503 before and 531 in the registered original.

The sole through the socket uses the same 40 turning rings as the king and queen, enlarged uniformly by 5.11% from 026. I moved the collar stack up and gave the stem more length, then rounded the mitre shoulder. The height for these changes came from shortening the mitre and button section by 0.282 model units.

| Test | Original white at 54° | White candidate 3 at 54° | Overlap with the earlier side lineup |
| --- | ---: | ---: | ---: |
| Bishop 026 | 85.63% | 84.77% | 98.16% |
| Wider foot and socket | 89.91% | 89.82% | 94.68% |
| Raised collar stack | 94.09% | 93.96% | 86.91% |
| Fit to the collar arcs | 95.15% | 94.84% | 86.46% |
| Fuller mitre | 95.23% | 94.82% | 85.94% |
| Smoother mitre shoulder | 95.72% | 95.31% | 85.94% |
| **Accepted 027, with the refitted slit** | **95.72%** | **95.31%** | **85.93%** |

The side outline now averages 4.04 pixels from the owner's 221-pixel-tall side guide, up from 0.48 pixels on 026. The most visible change in profile is the shorter, wider mitre above a longer stem. Each profile has its feet on the same baseline. The original black sprite also improves at 54°, from 86.43% to 94.96%. [Level profile comparison](side-comparison.png) · [King, queen and both bishops on the fixed physical ruler](frozen-lineup.png)

## One cut through the wood

I traced the original white slit onto the uncut subdivided model, then rotated the existing rounded saw about two axes. Fitting the plane on this mitre gave 1.79 pixels RMS across the original optical samples. The same fit with no rotation about the vertical axis gave 12.02 pixels. After cutting, rays through the saved model located the slit center within **0.93 pixels on average** across 14 rows, down from 21.29. The bottommost visible cut moved from **(505.5, 480)** to **(509, 421)**. The soft original ends around **(512, 420)**. The frontal saw trial missed the stroke by 5.11 pixels on average.

Moving the real cut exposed a second stripe in the inherited wood. It was the old opening painted into the color atlas. I replaced it with neighboring wood grain. The repair changes **45,089 of 4,194,304 texels** (1.08%) and preserves every alpha value. The saved Blender shader and browser use the same repaired pigment. The cut passes through the head at three sampled elevations, has solid wood below its floor, and retains a rounded end. The button meets the head across 85.2% of its diameter. [Cut comparison in wood and neutral clay](slit-comparison.png) · [Plane fit](cut-plane.json) · [Packed pigment audit](validation/pigment-validation.json)

## What still differs

The original tip begins at row 156. The new button first appears at row 224, and the raised mitre behind it first appears at row 209. A centered button at the fixed height would need to extend at least **0.55 model units** toward the rear to reach the source tip in this camera. Its actual radius is about **0.26**. I kept the compact, seated button. The rear base flare averages about 15 pixels too narrow on each side in rows 620–789, and the front groove lands at row 1074 against a dark trough around 1053 in the original.

In the wood render the foot reflection is narrower and brighter than the broader source streak. The collar and stem still carry some baked shading, and the wood retains a strong orange band at the foot. My visual scores against white candidate 3 are **85% interior shape, 82% wood color, 78% grain and 70% lighting**. Only the silhouette score is an area measurement. [Registered outline and finish evidence](comparison/comparison.png) · [All trial measurements](measurements.json) · [Scores](scores.json)

Checkpoint 026 is archived. The camera, source images and physical lineup ruler are pinned in the checkpoint. The editable scene was reopened and its two closed components, live Boolean, contact, UVs, normals and light receivers were checked against the exported rotating model. [Geometry audit](validation/mission-validation.json) · [Interactive viewer checks](validation/viewer.json)
