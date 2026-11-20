# Round 7 · Candidate A

The crest of A sits farther back over the neck, giving the upper head the sweep visible in both references. The pointed ear keeps its place under the arch. Viewed from the side and rear, the long bevel of the mane curves down to the collar. B makes an equally valuable correction beneath the jaw, but its lower breast projects into a pointed ledge. The ledge becomes particularly clear when the knight turns to its opposite flank.

| Model | Reference at 54° (45%) | Side (35%) | Form (15%) | Finish (5%) | Weighted / 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Round-six parent | 89 | 87 | 87 | 80 | 87.55 |
| A | 91 | 88 | 88 | 79 | 88.90 |
| B | 91 | 82 | 83 | 80 | 86.10 |

## Where the silhouettes agree

| Registered image measurement | Parent | A | B |
| --- | ---: | ---: | ---: |
| Whole silhouette overlap, original | 97.27% | 97.85% | 97.67% |
| Whole silhouette overlap, black 2 | 96.67% | 97.51% | 97.15% |
| Upper head, mean edge error against original | 17.55 px | 2.25 px | 17.55 px |
| Upper head, mean edge error against black 2 | 19.82 px | 2.79 px | 19.82 px |
| Chest edge below jaw, mean error against original | 13.80 px | 13.80 px | 3.02 px |
| Chest edge below jaw, mean error against black 2 | 17.09 px | 17.09 px | 3.94 px |
| Mean RGB error over the shared opaque area against black 2, out of 255 | 12.26 | 13.13 | 12.78 |

The upper-head measure samples both outer edges across rows 310–355. The chest measure samples the outside edge across rows 540–655. At row 325 A spans x249–512. The original spans x249–513, and black 2 spans x242–512. All views use the saved 54° camera and the same source registration.

The first revision of A moved the visible ear point back by 27 pixels along with the crest. Tracing the actual ear onto the two images showed the extra length. The finished sculpt corrects the free ends of both ears. Its visible near-ear point begins at x271, y386 and the front end remains at x556, y466. The ear sits naturally under the crest in profile, though its lighting at 54° still differs from black 2. The underside of the muzzle already follows the original to less than one pixel on average across the sampled common columns. Neither proposal changes its outline there.

## The clay and walnut

B’s breast lines up with the original at x600 on row 545 and gives the eye a slightly lighter lower rim. In profile, however, a steep change in curvature leaves a distinct shelf just above the collar. The matched near- and far-side clay renders and the source-edge overlay preserve both observations. A retains the fuller parent chest and its rounded sweep. The next chest sculpt needs to satisfy both views.

The base in all three walnut renders has close average color to black 2. The fine figure reads softer in the chest and base, and the cheek is lighter. A’s RGB error increases in the upper head as its surfaces and highlights move. The walnut on the back still follows the same material and grain scale as the two flanks. The exposed eye, fixed camera and pigment atlas in A remain traceable to the parent.

## Reproduction

Start each proposal with the released model at `031f0fd` as `parent.blend` in `build/knight-mission/improvement-007-A` or `improvement-007-B`. A’s assessment documents the contour fit and ear correction. B’s report documents the chest and lower lid. Each proposal includes its necessary input files and building scripts. Both gallery candidates were rendered from the reopened scene at 144 samples.

Run `outline_comparison.py <checkout> 7 A B` with the parent still installed to reproduce the two-band outlines. To trace an ear, run Blender with `-b -P trace_ear.py -- <checkout> <model.blend> <round-folder>/ear-A.json`, substituting the appropriate model and label. Then run `ear_overlay.py <checkout> 7 parent A B`. The neutral inspection used identical lighting and materials on all three saved models. The record includes the actual turns, paired fixed and side views and the comparison at board size.
