# Round 9 · Candidate A

A’s eye is easier to read from the board angle and from both sides. Its upper lid rises into the brow, the nose-side corner extends into the cheek, and the wood beneath the eye carries a short glint. The near and far cheeks retain their grain under matched light. B gives the mane a crisp sweeping edge and suppresses the second bright band across its top. In the front and rear views the top of B’s mane becomes a broad, uneven shelf. I chose A and kept B’s bevel study for the next mane sculpt.

| Model | Reference at 54° (45%) | Side (35%) | Form (15%) | Finish (5%) | Weighted / 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Round-eight parent | 92 | 89 | 89 | 78 | 89.80 |
| A | 93 | 90 | 89 | 85 | 90.95 |
| B | 93 | 90 | 84 | 79 | 89.90 |

## The eye

I projected the exposed inner eye onto both references using a ray through every pixel in the registered crop. The central upper edge rises from y472 to y467 across x495–504. Black 2 puts its visible crease near y464–466. The rear corner stays at x477 and the front moves from x529 to x540. The updated opening contains 1,028 pixels against the parent’s 658. The photographed crease is visible above the eye. Its precise boundary is uncertain in the small original.

The short reflection below the eye moves from a center near (498, 490) to (496, 497), close to (498, 499) in black 2. It is still narrow. Its bright patch is 16 × 6 pixels where black 2 measures 31 × 9 using the same local half-peak threshold. The model’s eye also looks more uniformly polished. A retains a readable almond shape under plain clay lighting. Opening the physical lids accounts for the shape, while refocusing the lower studio light accounts for much of the glint.

The new cheek measures RGB (97, 47, 16) in a wood patch where black 2 measures (97, 47, 17). The parent was (130, 65, 26). Local log-luminance contrast is 0.263 against 0.268 in black 2. In a second, symmetrical studio the two flanks show the same scale of wood figure, with the far side naturally darker. The physical eye apertures overlap by 99.45% when mirrored across the unposed head.

## The mane

B carves a narrow bevel around the upper sweep and moves the existing reflector over it. At 54° one strong curved edge runs down the mane. At the crest the elevated far ear previously caught enough light to look like a second edge. In the new cut that reflection recedes. B keeps the actual ear tops and the long lower mane edge in place. Its total height increases from 5.073 to 5.128 model units, about 1.1%.

The side and front tell different parts of the story. B’s line flows better from the top of the head down the neck in profile. Across the width, however, B’s mane has an almost flat top. At three of the measured stations the far shoulder rises above the near one. From straight ahead this looks more like the end of a squared block than the rounded crest in the reference. The next sculpt should keep the fine edge and bring both shoulders into one centered arch. The diffuse-only image and the fixed-camera neutral-finish image identify where a pigment change can help and where the geometry and varnish determine the result.

| Registered measurement | Parent | A | B |
| --- | ---: | ---: | ---: |
| Silhouette overlap with original | 98.23% | 98.23% | 98.10% |
| Silhouette overlap with black 2 | 97.91% | 97.91% | 97.82% |
| Mean edge error to original over upper-head rows 310–355 | 2.25 px | 2.25 px | 2.72 px |
| Mean RGB error against black 2 in eye crop, out of 255 | 16.56 | 15.05 | 16.56 |
| Mean RGB error against black 2 in the shared visible area, out of 255 | 14.34 | 14.22 | 14.20 |

## Reproduction

Use the released scene from `e7f2890` as `parent.blend` in each candidate’s staging folder. Each folder contains its sculpting script, parameter record and assessment. Both frozen candidates were reopened and rendered at 144 samples with the registered 54° and side cameras. The review also includes matched lighting, near and far sides, wood and clay, and the small original at board size.

A uses the round-eight A cheek atlas with SHA-256 `86debdcce4b5b6075ae7510cb25f77066ae912cfb8e1a0c4a49101ed43b79978`. The accepted copy is in `assets/knight/wood-atlas-improvement-008-A.png`. For a rebuild, copy that image into the candidate directory as `pigment.png` and the preceding accepted atlas as `source-atlas.png`. To regenerate the pigment from its source, use the archived round-eight A extraction and pigment scripts with their recorded parent. B uses design 20 from its parameterized section sculpt. Each comparison uses the fixed and side renders from the same saved model, with neutral and diffuse-only passes linked to the model by digest.
