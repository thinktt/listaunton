# Round 1 · Candidate A

A wins for the transition from cheek to jaw to nose. In profile the parent has a small inward notch and a relatively blunt terminal curve. A fills the rear cheek and lifts the chin, so the lower contour tapers smoothly while the throat stays open. A's matching clay flanks show a wider cheek on both sides. A small bright patch on the near cheek and the inherited displacement at the jaw tip are still visible.

| Model | 54° fit (45%) | Side (35%) | Form (15%) | Finish (5%) | Weighted score / 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Parent 007 | 87 | 77 | 81 | 77 | 82.10 |
| A · cheek and muzzle | 87 | 84 | 84 | 76 | 84.95 |
| B · brow and eyes | 86 | 78 | 81 | 76 | 81.95 |

Scores express the lead's visual judgment. Both candidates improve on the parent's outline at the registered 54° camera. Against the original sprite, muzzle-region intersection over union rises from 0.9621 to 0.9775 for A. Against black candidate 2 it rises from 0.9196 to 0.9230. The whole-piece mean RGB error on shared opaque pixels rises from 11.77 to 12.02 out of 255 for A. At playing size both changes are subtle. The clearer cheek and jaw in the side view decide this round.

B brings the fixed-view eye tilt closer to the reference, from 4.76° to 15.71°. Its outline is strong, but the lower lid casts a longer dark line and makes the eye look outlined. In the centered front and mirrored clay views the paired eye angles agree. All three knights have a visibly coarser grain pattern on the rear mane than on the face under the same studio lights.

## Reproducing the studies

Use checkpoint 007 at commit `e6ac135` as the parent. Put the A and B sculpt scripts in `build/knight-mission/improvement-001-A` and `improvement-001-B` respectively. Copy the parent scene into those folders as `parent.blend` for A and `parent-007.blend` for B. Run each script with Blender 5.2 in background mode. For B pass `-- --build --wood --diagnostics`. Both scripts reopen the saved candidates for rendering. Candidate metrics record the exact scene, source images and fixed render hashes. The winning scene is resaved with release metadata and reopened for the gallery and interactive viewer.
