# Round 8B

The breast now recedes under the jaw and rolls into the collar as one volume. The anterior half of each horizontal section carries both diagonal bevels with it. The accepted muzzle, eye, mane, pedestal, finish and studio are preserved.

## Physical form

The discarded 7B pulled the sternum away from nearly fixed flanks. At z2.58, its outline turned outward again by 0.113 model units before reaching the side. The new model uses the same continuous transform across each anterior half-section. The transform moves points only in the front-to-back direction. It uses the measured sagittal center of the accepted parent at each height to keep the side profile rounded.

| Physical measurement | Parent 7A | Discarded 7B | Round 8B |
| --- | ---: | ---: | ---: |
| Secondary outward rise at z2.36 | 0.000 | 0.079 | 0.000 |
| Secondary outward rise at z2.58 | 0.000 | 0.113 | 0.000 |
| Largest turn over 0.10 units of height in the low breast | 13.04° | 24.87° | 14.36° |
| Reversal of center-profile direction, z1.90–2.85 | 0.00° | 5.91° | 0.20° |
| Height of the most forward point | 1.96 | 1.87 | 1.90 |

All five sampled horizontal sections have a single central arch through lateral positions −0.70 to +0.70. Neither the lateral coordinates nor the heights of the chest vertices change. At the sagittal midline the breast emerges from the turned collar at z1.690, compared with z1.648 on the parent. The fixed-view comparison uses the full piece, including the accepted base where its rim begins to determine the outline.

The same-light near and far clay images are in `roundness.png`. `breast-sections.png` shows the parent, discarded 7B and saved 8B sampled along the same rays. `chest-B.json` and `chest-study.json` contain the coordinates and measurements.

## Fixed-view result

| Chest outline | 7A to original | 8B to original | 7A to black 2 | 8B to black 2 |
| --- | ---: | ---: | ---: | ---: |
| Upper breast, rows 540–580 | 18.49 px | 5.61 px | 22.44 px | 9.56 px |
| Lower breast, rows 581–655 | 11.24 px | 2.47 px | 14.16 px | 4.24 px |

At row 545 the edge moves from x622 to x607. The original is x600 and black 2 is x597. The remaining upper fullness accommodates the continuous shape in both side views. The neck descends more steeply for a short distance immediately beneath the chin. Across the full silhouette, overlap increases from 0.97850 to 0.98231 against the original and from 0.97508 to 0.97910 against black 2.

The broad shoulder bevel holds nearly the same measured light under the inherited wood setup, 128 versus 130 for 7A. The thinner bevel moves with the front plane and falls from 136 to 111 along the reference trace. Its lower end catches a stronger reflection, with the 90th-percentile luma rising from 95 to 122 in that region. Black 2 measures 91.

## Source and reproduction

The accepted parent has SHA-256 `8d984d59beea0f86d69bbb5b8f5dc57becf7e707e576412eb8eda4503e81a948`. The frozen candidate has SHA-256 `4e954e74ba4e40957bbe6ddfae623e01e0e383745c5e97febc7984b512e9dd2c`.

| Reopened 144-sample image | SHA-256 |
| --- | --- |
| `wood.png` | `b2ff44472cbbd1475a5fe937ac34c806dca9be172e8b91b276e0939bfd1a58ed` |
| `wood-side.png` | `49904938e3599e79ace20a23a3c1ce62c6a9df1d5092a4df24d763f4302ca160` |

The native exporter and validator passed for all seven visible components and both construction meshes, with zero nonmanifold edges. Only the joined head-and-neck surface below z3.36 and the underlying chest loft changed. The studio lights, mesh topology, UVs, local finish, packed pigment and camera passed direct comparisons against 7A. The numerical derivative of the anterior remapping stays positive throughout the edited surface, including the deepest cut.

Run these commands in this directory using Blender 5.2 and Python with NumPy and Pillow. The recorded `section-guide.json` contains rays from the frozen parent. The optional `--guide` switch recreates them. The two walnut PNGs are rendered from the saved scene after reopening it.

```powershell
blender -b --python-exit-code 1 -P carve.py -- --guide --build 17 --studio --parent-flat --orbit
blender -b --python-exit-code 1 -P verify.py
python -B study.py
python -B plot_chest.py . parent 7B B
python -B roundness.py
python -B review.py
```
