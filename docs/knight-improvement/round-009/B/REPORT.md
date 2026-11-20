# Round 9B · upper mane and poll

The near crest now carries one continuous chamfer from the rear sweep into the brow. The low crown rolls laterally over the far ear root. Its far edge turns down, which reduces the second exposed reflection from the parent’s ear. The softbox already linked to the mane was refitted to the chamfer. The two ear meshes retain their original coordinates.

| Frozen file | SHA-256 |
| --- | --- |
| parent.blend | 53ca17473c08fc898e6c29bd5189e4188b3573e003719362cabb102ab621f757 |
| knight.blend | c6edd8375c632aa48410186f4a77c575c87a8b91e3d6c353414f45f0c90c8ff3 |
| wood.png | d04f25a96eb1a9a4962b93017f0c14919e98ebbd3d6481c0a2d24938f656a286 |
| wood-side.png | c0565245d8e29099b458af24621bf94e03299e89be81f696bc4ab178b84f854a |

## Measured from the reopened model

| Measurement | Original | Black 2 | Parent | 9B |
| --- | ---: | ---: | ---: | ---: |
| Median main highlight width at half contrast, px | 29 | 11 | 18 | 8 |
| Median main highlight luma, 0–255 | 81 | 145 | 153 | 137 |
| Secondary upper band, median peak luma | 50 | 67 | 110 | 87 |
| Main line’s fall near its forehead end, px | 8 | 8.5 | 8 | 11 |
| Local upper outline mean distance from Black 2, px | 5.44 | 0 | 1.73 | 2.92 |
| Local upper outline mean distance from the original, px | 0 | 5.44 | 7.00 | 8.19 |

These readings average five adjacent columns after a two-pixel Gaussian blur. Width uses the midtone between each peak and its local trough. The original sprite has much softer sampling than Black 2. The outline reading uses the first pixel above luma 16 at 84 columns across the crest, so illumination can influence it.

The evaluated piece is 5.12775 units high, up 1.09% from 5.07268. Its mane reaches z5.16775, previously z5.11268. Both ears top out at z4.92952 and the forehead at z5.09323. The topology and UVs match the parent, and the packed walnut and varnish attributes have the same bytes. The top seven longitudinal rings contain 412 changed points. The largest movement is 0.20644 units. The lower six rings keep their coordinates. The evaluated mane has zero intersections between nonadjacent triangles. Repository validation also confirms seven visible closed components, both seated eyes and an export matching the saved camera and bounds.

## Tradeoffs

The brighter near bevel is thinner than Black 2’s, and its dark underside is more evenly shaded. The grain on the upper face still produces a rough diagonal patch near the poll. In the opposite and front views the crest reads as a wider, slightly asymmetric cap. Physical cuts show a broad, flattened top at several stations, particularly toward the forehead. The outline is a little fuller than both source sprites. The 16-frame clay turn and six measured sections show those changes in three dimensions.

## Evidence and reproduction

- `crest-comparison.png` shows the registered original, Black 2, accepted parent and reopened candidate. `crest-comparison.json` gives the individual samples.
- `flat-comparison.png` pairs the fixed and side clay views under identical symmetric lamps. `matched-clay-turns.png` and `matched-walnut-turns.png` show near, opposite, rear and front under the same parent lighting for both forms.
- `board-and-side.png`, `contact.png` and `clay-turn.webp` show the board-size result, full walnut views and the rotating clay sculpture. `top-sections.png` uses actual intersections of the evaluated surface, measured every 0.01 units across six stations.
- `parameters.json` records the frozen parameters and both 144-sample render digests. `verified.json` records the tested geometry, camera, material, light, height and export checks.

Run the following in a copy of this candidate directory within the staging build tree. The scripts read the shared native knight camera, pose, renderer and exporter. Blender 5.2 and a Python installation with Pillow and NumPy are required. The example uses PowerShell.

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
& $blender -b --python-exit-code 1 -P carve.py -- --build 20 --studio --parent-flat --orbit
& $blender -b --python-exit-code 1 -P check_final.py -- 20
& $blender -b --python-exit-code 1 -P matched.py
& $blender -b --python-exit-code 1 -P verify.py
& $blender -b --python-exit-code 1 -P top_sections.py -- ../../.. parent.blend crest-parent.json
& $blender -b --python-exit-code 1 -P top_sections.py -- ../../.. knight.blend crest-B.json
python plot_top_sections.py . parent B
python review.py
python matched_sheet.py
```
