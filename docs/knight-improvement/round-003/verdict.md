# Round 3 · Candidate A

A's reflection follows the arch between the ears more closely at the fixed 54° camera. The dark band immediately below it distinguishes the two layers of carving at playing size. Its side still reads as a smooth sweep, although the lower mane loses some of its light. B seats the eye more convincingly in profile, but the cheek develops a broad patch of light below the eye that draws attention away from the carved lid.

| Model | 54° fit (45%) | Side (35%) | Form (15%) | Finish (5%) | Weighted score / 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Round-two parent | 87 | 84 | 84 | 83 | 85.30 |
| A · poll reflection | 89 | 84 | 84 | 84 | 86.25 |
| B · eye and lid | 87 | 85 | 84 | 82 | 85.60 |

The median width of A's highlight drops from 24 px to 17.5 px, toward the 9 px in black candidate 2. Its average position error falls from 8.31 px to 4.39 px. The shadow just below it drops from 67.0 to 52.5 on the 0–255 luminance scale, against 47.5 in the reference. A keeps the geometry and pigment from round two. Under the original rig, the revised polish on its own gives a 26 px band. Most of the gain comes from a narrow oval studio source and reduced light on the mane. The consequence is clearest in the lower mane, where mean side-view luminance falls from 40.1 to 29.8. In the rear view the walnut still follows the carving.

B recovers the sign of the lower eyelid contrast seen in both references. The lid is 19 luminance units brighter on average than the cheek just below it. The parent is 16 units darker, the original sprite is 21 brighter, and black candidate 2 is 42 brighter. B also makes the lens smaller and more inclined on both sides. Its fixed-camera cheek reflection is too broad, and the local per-channel RGB error across the eye region rises from 13.46 to 13.99. Both candidates preserve the parent's full silhouette at the registered threshold.

## Next shape study

On the left side of the fixed image, near the bottom of the mane, the two references put the silhouette at x=258–259 at y=640. The accepted model puts it at x=289. Two pixels inside this edge the saved mesh resolves to the swept mane. At y=650 the outermost visible part already resolves to the pedestal. The references carry the sweep lower and meet the base farther out. The close crop and the row-by-row outline observations are saved with this verdict.

## Reproducing the two candidates

Use the scene at `00c74e3` as `parent.blend` in each candidate directory under `build/knight-mission`, named `improvement-003-A` and `improvement-003-B`. For A, copy its two Python files and the registered reference crop array into its directory and run `sculpt.py` in Blender 5.2 background mode. For B, copy `eye.py` and `selected.json`, provide round two's `mane.py` in the sibling `improvement-002-B` directory for the diagnostics, and run `eye.py` with `-- --final`. The gallery uses the reopened winning scene's walnut renders. The interactive viewer reproduces the geometry, mapped walnut and varnish with its own lighting.
