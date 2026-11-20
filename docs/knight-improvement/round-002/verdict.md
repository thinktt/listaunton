# Round 2 · Candidate B

The difference is easiest to see by turning from the right flank to the back. The parent has a line of repeating diamonds down the mane. B carries fine walnut fibers around the arch. The rear retains its dark value and the near flank retains the carving selected in round one. The close rear-quarter render and the registered side view show the transition under the same studio lights.

| Model | 54° fit (45%) | Side (35%) | Form (15%) | Finish (5%) | Weighted score / 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Round-one parent | 87 | 84 | 84 | 76 | 84.95 |
| A · poll and ear | 86 | 85 | 84 | 74 | 84.75 |
| B · walnut on the mane | 87 | 84 | 84 | 83 | 85.30 |

A improves the definition of the poll edge in profile. At 54°, the shadow immediately below the ridge darkens from 67 to 59 on a 0–255 luminance scale, toward 48 in black candidate 2. The near ear develops a rectangular specular patch and the band at the poll still measures 25 px wide against 9 px in the reference. A's overlap with the original sprite improves from 0.9690 to 0.9696 while overlap with candidate 2 falls from 0.9630 to 0.9627.

B keeps the parent geometry, studio and fixed-camera silhouette. Its median rear pigment stays at RGB (94, 50, 23). The local texture and its continuous transition over the far flank account for the finish gain. The frontal highlights on the poll, cheek and chest remain visible discrepancies.

## Reproducing the studies

Use the accepted model at `7aecbe6` as `parent.blend` in each trial folder under `build/knight-mission`. A's folder is `improvement-002-A`; run its sculpt script in Blender 5.2 background mode. In `improvement-002-B`, run `mane.py` in Blender with `-- --prepare` to sample the parent surface. Run `grain.py` with ordinary Python, then run `mane.py` in Blender with `-- --build --render`. The editable winner and release texture are in the project's knight model and asset folders. The process keeps the original UV map and embeds the same PNG used in the viewer.
