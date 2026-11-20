# Round 10B · centered, beveled mane

The upper mane has one rounded ridge and two matching 0.024-unit shoulder bevels. The bevels turn downward into the forehead. Their supporting flanks fill the hollow under the two swept ears. The paired ears sit closer to the poll through their middle sections, with a satin finish on the upward-facing wood. The ends of both ears retain their exact coordinates. The existing poll reflector follows the glancing angle of the new bevel.

## Frozen deliverables

| File | SHA-256 |
| --- | --- |
| parent.blend | 8e015620e552bda2c1e67866da8a7a3ba0e671c16deb22d93c07fb6c7859121d |
| knight.blend | 56b1373250def855651b4d4a4306c5a824eec0f58ef198d1496bdd66270bc847 |
| wood.png | bf25dea0c45448cf88fde79b5a9012017e4aedf4e919b2cee404984796c46c64 |
| wood-side.png | cb0b7e7c3d6da7a359d057161ea0b3f4ec8aa976e1f82c1e32b0b1b97ee1e905 |
| pigment.png | 86debdcce4b5b6075ae7510cb25f77066ae912cfb8e1a0c4a49101ed43b79978 |

The two full-resolution walnut images are 144-sample renders from the reopened scene. The packed walnut carries its inherited `Knight walnut | figured cheek pigment 008-A` name. The released 9A model supplies these bytes. The local `pigment.png` and export copy `wood-atlas-improvement-008-A.png` match the packed PNG byte for byte.

## Physical measurements

Native rays were cast at x = −0.8, −0.6, −0.4, −0.2, 0 and 0.14 after undoing the head pose. At every station the highest sample lies at lateral coordinate zero. Height falls monotonically toward both shoulders. Across matched y values from ±0.05 to ±0.17 the mean absolute difference is 0.000032 units and the largest is 0.000398. The median width within 0.004 units of the top is 0.06, compared with 0.04 in the parent.

The full piece is 5.08904 units tall, up 0.32% from 5.07268. The mane reaches z5.12904, up from 5.11268. The two ear tops sit at z4.88667, previously 4.92952. The largest ear displacement is 0.08467 units. The six lower mane rings retain their coordinates. The native subdivided mane and both ears each have zero nonadjacent triangle intersections. The repository validator confirmed seven visible closed components, unit-length normals, finite exported vertices and a matching saved reference camera. Both scenes expose 259 eye samples at the validator’s fixed two-pixel sampling pitch.

## Registered render measurements

| Feature | Original | Black 2 | Parent | 10B |
| --- | ---: | ---: | ---: | ---: |
| Main highlight width at half contrast, px | 29 | 11 | 18 | 10 |
| Main highlight median luma, 0–255 | 81 | 145 | 153 | 141 |
| Luma in the hollow beneath the highlight | 33 | 36 | 33 | 34 |
| Upper ear band, median peak luma | 50 | 67 | 110 | 76 |
| Downward turn of the line near the forehead, px | 8 | 8.5 | 8 | 10.5 |
| Local upper-outline distance from Black 2, px | 5.44 | 0 | 1.73 | 3.58 |
| Local upper-outline distance from original, px | 0 | 5.44 | 7.00 | 1.88 |

The light measurements use five neighboring columns and a two-pixel Gaussian blur. Width is measured halfway between each local peak and the hollow beneath it. The original source has softer pixel sampling than Black 2. In the fixed upper window, native rays hit the exposed far ear at 212 sample locations, down from 441 in the parent. The far ear still contributes to the upper outline.

## Visual tradeoffs

The lower ear seating brings the elevated outline closer to the original and further from Black 2. The true side and opposite views show slightly slimmer ear roots. A small flat facet survives at the junction with the brow. The bevel reflection is more uniform in intensity than the irregular highlight in Black 2. The fixed camera and all meshes outside the mane and ears retain their parent geometry.

## Evidence

- `crest-comparison.png` shows the two registered sources, the released parent and the reopened candidate. `crest-comparison.json` contains the individual luminance traces.
- `top-sections.png` plots six actual surface cross sections. `frozen-sections-and-height.json` verifies the symmetry, central peaks, physical heights, ear endpoints, pigment and triangle-intersection counts.
- `matched-clay-turns.png` and `matched-walnut-turns.png` pair parent and candidate under the same parent lamps. `flat-comparison.png` pairs the fixed and registered side in neutral clay.
- `board-and-side.png`, `contact.png` and `clay-turn.webp` show the fixed sprite, board size, side, front, rear and opposite profiles.
- `verified.json` records the frozen source and export checks. `parameters.json` records the source-image digest, sculpt, studio card and both reopened render hashes. `ear-visibility.json` contains the native far-ear hit coordinates.

## Reproduction

The commands below run in a copy of this candidate directory at the same depth inside the staging build tree. Blender 5.2 supplies the mesh and ray tools. The offline image studies require Pillow and NumPy. All generated files land in the candidate directory.

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
& $blender -b --python-exit-code 1 -P check_final.py -- 12
& $blender -b --python-exit-code 1 -P carve.py -- --build 12 --studio --parent-flat --orbit
& $blender -b --python-exit-code 1 -P matched.py
& $blender -b --python-exit-code 1 -P verify.py
& $blender -b --python-exit-code 1 -P freeze_quality.py
& $blender -b --python-exit-code 1 -P ear_visibility.py
& $blender -b --python-exit-code 1 -P top_sections.py -- ../../.. parent.blend crest-parent.json
& $blender -b --python-exit-code 1 -P top_sections.py -- ../../.. knight.blend crest-B.json
python plot_top_sections.py . parent B
python review.py
python matched_sheet.py
```
