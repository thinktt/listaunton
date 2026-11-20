# Round 6 · Candidate A

The bevel on A’s mane catches the light as it travels over the arch behind the ear. In side clay, the almond-shaped eye now ends cleanly in the cheek. Its lower lid tapers into the face without the short hooked crease that was visible in round five. I chose A for this combination. B also improves the lid corners and gives the head a more open silhouette under the jaw. Its upper mane carries forward the broader, flatter patch of light from the parent.

| Model | Reference at 54° (45%) | Side (35%) | Form (15%) | Finish (5%) | Weighted score / 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Round-five parent | 88 | 85 | 86 | 79 | 86.20 |
| A | 89 | 87 | 87 | 80 | 87.55 |
| B | 89 | 86 | 87 | 79 | 87.15 |

## What changed in the photographs and the mesh

| Measurement | Parent | A | B |
| --- | ---: | ---: | ---: |
| Outline overlap with original | 97.24% | 97.27% | 97.53% |
| Outline overlap with black 2 | 96.64% | 96.67% | 96.93% |
| Average luminance on the black-2 crest highlight path, out of 255 | 90.8 | 134.3 | 90.8 |
| Mean horizontal error along the chest edge against the original, rows 540–580 | 18.49 px | 18.49 px | 4.05 px |
| Mirrored eye-opening overlap, in a head-on view of each socket | 99.50% | 99.71% | 99.85% |
| Mean RGB error on the common opaque area against black 2, out of 255 | 12.09 | 12.26 | 12.61 |

Black 2 averages 141.8 on the sampled crest path. The original is darker with a subdued, continuous arc. A’s bevel produces a narrower, more coherent highlight, though the front part still spreads too widely. All three models preserve the original board-size profile. Their whole-image color errors are a reminder that improving a carving can move some reflections away from the reference.

The eye check casts rays into the evaluated surfaces of both eyes after undoing the head’s turn. The parent’s apertures were already symmetrical. The rough spot was in the skin immediately beyond the corners on both flanks. The matched clay renders show that both candidates smooth it. B makes the neatest tapered aperture. A gives the bottom of the socket a fuller curve. The curved reflection under the eye in black 2 is wider and sits higher than in either candidate.

B reduces the excess chest in the open space below the muzzle while retaining the dark trough and two raised diagonal accents. At row 545 its edge is at x602, against x600 in the original, x597 in black 2 and x622 in the parent and A. The lower breast is still fuller than in the references. A keeps round five’s chest shape, which is the most useful feature to revisit from B.

The rear-quarter clay images show a long, sharp lower mane on both flanks. In the walnut renders the grain remains continuous over the cheek, neck and back. The small facet where the upper mane turns past the ear is still visible in A’s side view.

## Reproduction

Start each proposal from the saved model at `c8060aa` as `parent.blend` in its `build/knight-mission/improvement-006-A` or `improvement-006-B` directory. The editable candidate A has SHA-256 `646675f3647338524b50271b39c571cbe53debd9bf4e9cad4ffffb2b2f4785df`. Candidate B has SHA-256 `c8de5dbdd6019599b74b2f9d12b364b00caba7f38ea28dc348d24a2fdd365254`. The workers’ notes and scripts document their changes. Both walnut views were rendered at 144 samples after reopening each file.

For independent comparison, run Blender with `-b -P bilateral_eye.py -- <checkout> <model.blend> <output-name>` on each file. Use `plot_bilateral_eye.py <round-folder> parent A B` to plot the relief and exposed eye. `carving_light.py` renders the studio clay comparisons under common lighting. The fixed-view comparison uses the same registered candidates and original sprite throughout.
