# Round 4 · Candidate B

B gives the end of the mane a neck to sit against. In profile the mane follows the curve of the neck down to a short taper above the collar. The opposite side and rear-quarter clay views show a fuller, continuous neck under it. A also carries the mane down convincingly, but ends in a broader, rounder tab with a dark seam at the collar. The parent leaves a visible step higher up on the neck.

| Model | 54° fit (45%) | Side (35%) | Form (15%) | Finish (5%) | Weighted score / 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Round-three parent | 89 | 84 | 84 | 84 | 86.25 |
| A · extended mane | 90 | 85 | 85 | 83 | 87.15 |
| B · extended mane and neck root | 91 | 87 | 87 | 83 | 88.60 |

## The outline at 54°

| Measurement on the 1254 px image | Original | Black 2 | Parent | A | B |
| --- | ---: | ---: | ---: | ---: | ---: |
| Left edge x at row 640 | 258 | 259 | 289 | 256 | 258 |
| Row at the deepest indentation | 667.5 | 667.5 | 640 | 666 | 664 |
| Mean absolute horizontal error to original, rows 580–686 | 0 | 1.12 | 10.60 | 3.15 | 1.93 |

A puts the turn closest to the correct height. B follows the curve more closely above and below it, with 2.21 px mean error against black candidate 2. Its whole-piece silhouette overlap rises from 96.90% to 97.22% against the original and from 96.30% to 96.63% against candidate 2. Both workers retained the registered angle and framing.

The atlas and upper arch are preserved in both candidates. Extending the geometry stretches some grain at the bottom. On B, the median long-direction stretch is 1.11× on the lower mane surface, and the 95th percentile is 1.41×. The side and rear renders still show a recognizable walnut figure. The darker seam just above the collar and the broad transition on the far flank remain visible. Mean RGB error over the shared opaque area rises slightly, from 11.58 to 11.74 out of 255. The judgment favors the visible improvement to the shape.

## Reproducing the studies

Toby's feedback before the next round was that the mane needs sharp edges and that the eye needs a redesign. Round four positions the lower mane. The shape of the mane's cross-section and the eye are the next sculpting targets.

With the parent renders in the checkout and the two candidate folders populated, run `mane_study.py <checkout> 4 A B` in Python to reproduce the outline table. Run Blender with `-b -P wood_stretch.py -- <parent.blend> <candidate.blend> <report.json>` for the lower-mane deformation measurements.

Use the saved model at `8625be4` as `parent.blend` in `build/knight-mission/improvement-004-A` and `improvement-004-B`. Copy each candidate's scripts and input JSON from this record. Run A's `sculpt.py` in Blender 5.2 background mode. Run B's `sweep.py` in the same mode with `-- --final`. Both scripts reopen the saved model to render the fixed and side views. The contour and grain measurements identify their input models. The winner is saved with its round metadata, then reopened again for the gallery and rotatable viewer.
