# Round 7B

The new breast was carved directly into the accepted 6A head-and-neck mesh and its editable chest loft. It opens the space below the jaw and controls the glare on the two diagonal walnut bevels. **Both common-light clay profiles reveal a pointed lower breast and a steep shoulder across its front.** The 54° opening improves, but the physical lower breast needs another sculpt.

## Cause of the ledge

Two cuts overlap at the front of the chest, and their influence ends across a band only 0.151 units wide before it reaches the preserved flank. Cross-sections through the frozen meshes show the result. At z2.44 the front surface moves back 0.228 units at lateral distance 0.50, just 0.044 at distance 0.60, and zero at distance 0.70. This rapid transverse change makes the steep shoulder. The central breast recedes 0.235 at z2.44 but only 0.010 at z1.84, leaving the original low volume projecting below it. See `breast-sections.json` and `clay-turn.webp`.

A subsequent sculpt can keep the open throat by defining a convex front arc for each horizontal section and carrying those arcs through the base-facing return. The side profiles and a rear-quarter clay view expose the turn where that sphere-like volume meets the shoulder. The sharp relief on the sides can then follow that rounded volume.

## Registered chest measurements

| Fixed-view outline | Parent to original | 7B to original | Parent to black 2 | 7B to black 2 |
| --- | ---: | ---: | ---: | ---: |
| Upper chest, rows 540–580 | 18.49 px | 2.63 px | 22.44 px | 1.76 px |
| Lower chest, rows 581–655 | 11.24 px | 3.23 px | 14.16 px | 5.13 px |

At row 545, the parent edge is x622, the original x600, black 2 x597 and 7B x600. At row 600 the parent is x682 and 7B reaches x669, matching the original. The accepted pedestal begins to set the combined silhouette as the chest rounds down. At row 645 its geometric edge alone is x704.23 while both image references put the outline at x697. `part-profiles.json` records independent intersections with the chest and pedestal meshes.

With the same chest lights and pigment, mean shoulder and crest luminance are 130.01 and 135.85 in 7B, against 129.99 and 135.92 in 6A. Black 2 measures 138.29 and 156.86. At the lower end of the bevels, the 90th-percentile luminance falls from 113.5 in the unmodified transfer to 93.35 in the finished 144-sample view. Black 2 measures 91.18 and the parent 94.83. The inset has a firmer outer edge near its lower end and the thin crest is still dimmer than black 2.

## Eyelid

The eye insets and orbital geometry have the same positions as 6A. A softer finish on the convex cheek and a small, real reflected light lift the lower eyelid. The central eye glint remains visible from the side. In the fixed view, mean lower-lid luminance rises from 74.05 to 87.42, compared with 122.80 in black 2. The cheek immediately below measures 104.77. Stronger attempts created conspicuous white bands. The delivered version retains less lower-lid contrast than the reference. The mean change across the registered side eye crop is 0.27 levels of luminance.

## Verification and files

The repository export and validation passed for all seven visible components and both hidden construction meshes. The vertex positions of the accepted head above z3.36 match exactly. The near eye covers the same 161 fixed-view probe samples. The cameras, packed images, topology, UVs, mane and turned pedestal match the parent. The finish changed on the cheek and the existing lower-eyelid light changed. The saved file was reopened for both 144-sample PNGs. The clay orbit contains sixteen views, with five corresponding walnut views in the same coordinates.

| File | SHA-256 |
| --- | --- |
| `parent.blend` | `1837b02f0c472044a8e86ffd112d15dbe007eb70d9a4330d86f8f073b7440208` |
| `knight.blend` | `b0b15ee070862ede2ea6f199f00853bf359e3260a05ff3201f53002ebf1151af` |
| `wood.png` | `2865a41bd5be4cd91451d95e34c2a88f8bfb2d3cdcb7f451a5fe6758e1cd47ca` |
| `wood-side.png` | `8caa5adb8a4a2ecf86cea51617de0dbcc3640dafd1a7bd7e87eb773d368b4857` |

`selected-details.png` compares the two references and both models. `contact.png` contains the board-size and diagnostic views. `flat-comparison.png` and `clay-turn.webp` show the underlying geometry. `verified.json` contains the native repository results.

From this directory, use the original parent copy and Blender 5.2 to recreate the saved geometry and views.

```powershell
blender -b --python-exit-code 1 -P carve.py -- --build 8 12 --studio --parent-flat --orbit
blender -b --python-exit-code 1 -P verify.py
python -B selected.py
python -B review.py
```

`carve.py` defines the upper and lower breast cuts in unposed coordinates. `eyelid.py` describes the physical finish and reflector. Its recorded parent surface rays are in `parent-eyelid-rays.json`. `diagnostics.py` and `evidence.py` define the matched cameras, clay setup and walnut renders.
