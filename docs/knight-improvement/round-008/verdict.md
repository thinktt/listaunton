# Round 8 · Candidate B

B opens the space beneath the muzzle. Its chest slopes forward into one rounded breast on both sides. The cross-sections explain the difference from the rejected round-seven breast. That earlier cut pulled the center back while leaving a shoulder on each flank. B moves the full front arc together. The dark gap under the jaw now reads clearly at board size.

| Model | Reference at 54° (45%) | Side (35%) | Form (15%) | Finish (5%) | Weighted / 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Round-seven parent | 91 | 88 | 88 | 79 | 88.90 |
| A | 91 | 88 | 88 | 85 | 89.20 |
| B | 92 | 89 | 89 | 78 | 89.80 |

These are visual judgments across the four mission criteria. The measurements below describe specific image features.

| Registered measurement | Parent | A | B |
| --- | ---: | ---: | ---: |
| Silhouette overlap with original | 97.85% | 97.85% | 98.23% |
| Silhouette overlap with black 2 | 97.51% | 97.51% | 97.91% |
| Mean chest edge error to original, rows 540–655 | 13.80 px | 13.80 px | 3.58 px |
| Mean chest edge error to black 2, same rows | 17.09 px | 17.09 px | 6.12 px |
| Mean RGB error relative to black 2 in visible common area, out of 255 | 13.13 | 13.03 | 14.34 |
| Mean RGB error relative to black 2 in eye crop, out of 255 | 16.55 | 15.34 | 16.56 |

B preserves the position of the mane, ears, muzzle and eyes. The two outer edges of its upper head still average 2.25 pixels from the original. On the chest, row 545 moves from x622 to x607 against an original of x600. At row 590 it reaches the original at x661. Across five physical sections the breast slopes continuously away from the center. At height 2.58, the rejected seventh-round breast pushed out a second time by 0.113 model units. This side ledge is gone. A short section just below the chin now falls more steeply. The narrow chest highlight is dimmer over its upper length and brighter at its lower tip, which contributes to the increase in whole-piece RGB error.

## The eye and the mane

A's cheek is the best wood match of the three. Its median RGB values are (95, 46, 15) in a registered patch where black 2 measures (97, 47, 17) and the parent measures (130, 65, 27). Its local log-luminance contrast is 0.270 against 0.268 for black 2. The lighter near cheek takes more stain than the already-dark far cheek. Under matched lights the fine figure remains visible on both sides.

A also broadens the fold beneath the eye and seats the small inner eye more deeply. The mirrored eye openings agree by 99.9%. The visible area of the near eye drops by a quarter on the common physical sampling grid. At 54°, it looks pinched. The reflection draws a long line across the lower fold. In black 2 the exposed eye looks fuller and the lower reflection breaks into a short, bright patch. The parent’s opening gives a better starting shape for that detail. A’s cheek texture is worth carrying forward independently.

On the mane, both candidates retain the sharp long edge down the back. At the top there are two parallel ridges of reflected light where black 2 has one dominant edge. The upper crown of the mane should round into that sharp edge. A pointed triangular plane remains where the mane meets the forehead. The archived upper-mane close-up marks matching points on the actual model and the reference, including the transition from the mane mesh to the upper head.

## Reproduction

Use the released model at `73426c5` as `parent.blend` in each round-eight candidate directory. The candidate folders contain their building scripts and notes. The selected B design uses the parent’s measured center profile in `section-guide.json` and design index 17. Both proposals were reopened and rendered at 144 samples from the saved 54° and registered side cameras. All three were independently checked in neutral clay and under one symmetrical walnut studio with cameras at equal elevation on opposite sides of the head.

The sheets show the reference view at board size, enlarged cheek and eye, the two flanks, five physical chest sections and the center profile. The scene and render digests in the measurements identify the exact proposals. B’s side profile and fixed image are also preserved in the winner gallery.
