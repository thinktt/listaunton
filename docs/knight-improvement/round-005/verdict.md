# Round 5 · Candidate A

A recuts the mane as a ribbon of wood with a broad flat face. Follow its narrow bevel from the top of the head around either side and down toward the collar. The eye has two tapered corners, a shallow bed beneath the brow, and a curved lower lid. It retains a small catchlight at 54°. The parent has a round mane and a raised, oval eye. B makes a gentler bevel and a clean slit in side view, but the eye looks like a triangular facet from the playing angle.

| Model | Reference at 54° (45%) | Side (35%) | Form (15%) | Finish (5%) | Weighted / 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Round-four parent | 86 | 72 | 78 | 80 | 79.60 |
| A | 88 | 85 | 86 | 79 | 86.20 |
| B | 85 | 82 | 83 | 79 | 83.35 |

These are judgments of this three-way comparison. Toby’s feedback about the mane and eye changed how I assessed the parent in profile. The previous round’s scores remain in its own record.

## The two surfaces

All three models were rendered with the same clay material, studio lights and camera for each view. The side, far flank and rear quarter show A’s continuous ridges in relief. A section through the middle of the mane at height 3.05 has a straight or nearly straight profile over 67.5% of its perimeter in A, 27.5% in B, and 0% in the parent. The section was sampled at constant arc length with a two-degree local turning threshold. The lower tip remains attached to the neck on all three models.

A’s recessed eye reads in both walnut and clay. The walnut far side and rear keep the grain and tone of the rest of the carving. The forward corner of A’s eye still puckers slightly. The lower lid in black candidate 2 turns gradually into the cheek and casts a wider, brighter reflection. On A, that light is weaker and falls too low. Two mane facets meet in a small triangle at the poll. B’s carving is tidier around the eye corners in clay, though the eye opening looks more angular at the fixed camera.

## The original and selected reference

| Fixed-view measurement | Parent | A | B |
| --- | ---: | ---: | ---: |
| Silhouette overlap with the original black sprite | 97.22% | 97.24% | 96.99% |
| Silhouette overlap with black candidate 2 | 96.63% | 96.64% | 96.57% |
| Mean RGB error on the shared opaque region vs black 2, out of 255 | 11.74 | 12.09 | 12.12 |

The silhouette numbers only measure the outside edge. At board size A preserves the original’s sweep. The point where the lower mane turns into the neck moves four pixels up in the 1254 px image, increasing mean local outline error against the original from 1.93 to 2.26 pixels. The larger facets also dim the poll highlight, and color error rises slightly. The eye and mane are the reasons for choosing A.

## Reproducing the comparison

Start each sculpt with the saved model at `e931993` as `parent.blend`, in `build/knight-mission/improvement-005-A` or `improvement-005-B`. Copy the sculpt and its companion diagnostic script from the corresponding directory. A runs `sculpt.py` in Blender background mode. B’s documented production command is in its assessment. Both reopen the candidate for their 144-sample registered walnut renders. A also rendered its candidate under the parent’s reflection lights for a separate matched-light check.

Run `carving_light.py -- <checkout> <model.blend> <output>` in Blender for the independent common-light inspection. Run `mane_sections.py -- <model.blend> <sections.json>` for the physical profiles, followed by `draw_sections.py <round-directory> parent A B` in ordinary Python to plot them. The packed atlas is the same for all three candidates. The finished model and the gallery derive from A’s scene with adjusted local reflection cards.
