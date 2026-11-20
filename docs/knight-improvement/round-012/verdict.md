# Round 12 · Candidate B

B has the clearest sweep from the ear to the bottom of the neck. In the parent, a broad strip of mane covers the neck and ends in a near-vertical seam. B pulls the leading edge back, fills the neck behind it and carves a hollow between the two. Under plain clay there is one continuous change of direction down the side of the neck. In walnut the edge casts a shadow in the same place as the dark curve in the original sprite. A also moves the joint close to the source. Its tighter turn just beneath the ear introduces a kink and a bright streak in the registered view.

| Knight | Fixed 54° · 45% | Side · 35% | Form · 15% | Finish · 5% | Weighted / 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Parent, round 11B | 94.5 | 92.5 | 92 | 87.5 | 93.08 |
| A | 94.5 | 93 | 92.5 | 87 | 93.30 |
| B | 95.5 | 94 | 93 | 88 | 94.23 |

The scores express my judgment of the complete carvings. I judged the fixed view against both black references and compared profiles rendered from the actual models. The relative scores favor B’s clean sweep and the way the lower edge seats into the neck on both flanks. [Playing-size comparison](board-read.png) · [Three profiles in clay](carving-three-way.png) · [Both walnut flanks](paired-walnut.png)

## Position and shadow

At the registered 1,254-pixel resolution, the two black references agree on the location of the dark hollow down the middle of the neck. Between rows 490 and 575 the parent’s visible mane edge sits 54.38 pixels too far toward the nose on average. A reduces the mean absolute difference to 4.17 pixels. B reduces it to 0.69 pixels. Higher up, between rows 460 and 489, the differences are 56.70, 9.50 and 2.30 pixels respectively. These figures compare the actual visible parts of the mesh with the photographed shadow. [Marked and unmarked crops](mane-boundaries.png)

| Group of fixed-camera samples | Original black | Black 2 | Parent | A | B |
| --- | ---: | ---: | ---: | ---: | ---: |
| Brightness on the mane near the cut, 0–255 | 23.60 | 27.38 | 25.22 | 26.23 | 29.17 |
| Brightness at the source hollow | 9.13 | 8.55 | 35.68 | 14.07 | 7.47 |
| Brightness on the adjacent neck | 41.58 | 54.66 | 50.42 | 59.92 | 58.55 |
| Position of darkest median sample, pixels toward nose | +2 | +1 | −19 | −3 | 0 |

At row 532 the parent surface is almost flush with a chord drawn across the hollow. The corresponding depths in A and B are 0.095 and 0.270 model units. On the six central sections, the median fraction of the outward hemisphere blocked by nearby geometry rises from about 1% in the parent to 55% in A and 80% in B. The directional-light falloff also remains visible with a uniform material. The photographs locate the hollow and show its shadow. Its physical depth is an interpretation. [Light across the edge](mane-light.png) · [Native surface sections](physical-mane-sections.png) · [Flat material and true rear views](back-clay.png)

B retains the upper mane, eye and pedestal. Overlap of the outer silhouette with the original rises from 98.37% to 98.38%, and with black candidate 2 from 97.70% to 97.73%. Most of the visible improvement is inside that outline. A and B both pass the paired mesh-ray test for gaps between the mane and neck. Their evaluated mane and neck pass the separate native checks for self-intersections. [Opposed flank samples](mane-flanks.png) · [Geometry and silhouette](registered-edge-detail.png) · [Round fingerprints](decision.json)

## Remaining work

The back plane of the mane needs more visible wood figure. In black candidate 2 its rear and inner thirds measure 39 and 25 on the brightness scale. The original measures 31 and 21. B measures 23 and 29, so the wood across the broad face changes brightness in the opposite direction even though the incision itself matches. In the rear view the longitudinal figure continues around the piece. In profile the exposed neck also carries a vertical crease below the cheek that can catch too much light. [Brightness across the broad face](whole-mane.png) · [Walnut from behind](back-walnut.png)

The next eye pass should connect the upper lid to the brow and nose. Black candidate 2 has a single long descending fold, a cheek that rolls up to the lower lid, and a gradually fading nose-side corner. In the current profile a deep perimeter gives the eye a separate inset appearance. On the continuation beyond the eye, the brightness difference just below the traced fold is 37 levels in black candidate 2, 14 in the original, and 12 in the parent. The source fold passes over both the swept ear and the cheek when its locations are projected onto the parent. The projection helps locate the relevant surfaces for sculpting. The side view remains an artistic judgment. [Brow trace on the photographs](brow-to-nose.png) · [The same locations on the actual side](brow-side.png)

## Reproduction

Start with the round-eleven scene at commit `558af02` and its packed atlas `wood-atlas-improvement-011-B.png`. The archived A and B folders contain the production scripts, reconstruction steps and native measurements. Use each folder in the staging layout described in its report. The source shadow trace also lives in the [round-eleven measurements](../round-011/mane-hollow.json). The B scene packs walnut atlas `1e35b27f1eea257ee9bacc6ae60aa26cbeaf80fad5139365d58be1db395dd78b`. The winner gallery uses fixed and side walnut renders from the reopened accepted scene at 144 samples.
