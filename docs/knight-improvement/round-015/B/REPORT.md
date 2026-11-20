# Round 15B · the carved eye

The central eye reflection rises six pixels in the registered walnut view. It now sits at (506, 474), beside Black 2’s (504, 473) and the original sprite’s (505, 472). The sloping brow and lower crescent remain visible from both flanks. [Registered comparison](upper-eye-sweep.png) · [Board-size comparison](fixed-and-board.png) · [Both flanks](two-flanks.png)

## Carving

I worked in a shared physical chart across the two eyes, with the head twist removed. Rays through the original skull and eye meshes supply their outer surface. The carving eases the sharp orbital return, blends a broad oblique central face into the existing wood, and rolls a smaller crescent toward the nose. The two corners and their neighboring cheek move together. Both eyes retain the original softboxes and timber. The burnished fraction increases on the broad central plane and falls toward the carved return.

The near-side upper and lower socket recesses measure 0.0112 and 0.0122 model units at the median. The parent measures 0.0193 and 0.0219. The far-side measurements are 0.0112 and 0.0116. Each number is the depression relative to a chord spanning the lid margin. Black 2 and the original provide a projected appearance. The section depths are sculptural choices. [Physical sections](socket-sections.png)

## Registered appearance

| Measurement | Original | Black 2 | Released 14B | 15B |
|---|---:|---:|---:|---:|
| Central reflection, x and y | 505, 472 | 504, 473 | 503, 480 | 506, 474 |
| Central peak luminance | 64.72 | 153.66 | 107.06 | 134.32 |
| Brighter interior reflection falling on the nose side | 53.68% | 32.00% | 46.57% | 38.57% |
| Middle 80% of lower cheek light, x range | 483–525 | 483–525 | 481–519 | 483–522 |
| Forward upper crease displacement vs Black 2 | −0.79 px | 0.00 px | +2.85 px | +1.45 px |
| Nose crescent peak, x and y | 536, 482 | 538, 484 | 528, 486 | 519, 487 |

The secondary highlight still gathers too far toward the middle. The parent’s forward triangular flash becomes quieter, although the candidate’s crescent falls short of the photographic nose corner. The ear-side crease also runs 2.27 pixels above Black 2, compared with 2.93 on the parent. Its contrast on the exact source trace is −6.13 versus Black 2’s +11.84. Rays through the photographed upper line between x483 and x507 reach the overhanging ear. Preserving the ear limits how far the exposed socket can carry that line. At true side, the almond stays open, with a broader lower seat and a cleaner turn toward the muzzle. The central patch remains more regular than the photographed walnut. [Measured trace](upper-eye-sweep.json) · [Interior and lower reflection](comparison.json) · [Moving near light](moving-near.png) · [Moving far light](moving-far.png)

## Native and viewer checks

The two exposed eye masks agree across 99.50% of their union on the 0.006-unit ray grid. All 15,872 triangles in each insert and 60,038 nearby skull triangles passed the nonadjacent intersection check. The validation export counted 889 intersecting eye-to-head face pairs on the near side and 896 on the far side. A native spherical UV correspondence preserves the narrow hidden far-eye return. I triangulated one buried quad, face 5492, to maintain clearance between two nearly tangent surfaces. All original vertex UV coordinates survive in every layer. [Bilateral visibility](bilateral-eyes.png) · [Geometry verification](verified.json)

The pedestal, ear and mane vertices reproduce the released geometry exactly. Height stays at 5.089041 model units. The registered fixed and side silhouettes each match the parent at every pixel above 50% alpha. The posed cameras, lights, light linking and packed pigment match the parent. Only the two eye meshes change varnish coverage. A second in-memory build from the parent reproduces the frozen mesh coordinates, topology, UVs and finish byte for byte. The private browser review draws 288,430 triangles and passes the synthetic and live Chromium camera and material checks. [Rebuild verification](replay.json) · [Chromium results](webgl/native-qa.json) · [Walnut and clay orbit](orbit-proof.png)

## Files and reproduction

| File | SHA-256 |
|---|---|
| Frozen knight.blend | `d5aa43f9cdcead682f1228413869e4a58b482b8d80895dff240333faac067ad9` |
| Fixed wood.png, reopened at 144 samples | `540a04d73a0af1e8de0ef51c7766ad1ac89c17f3a9bd0ee4f5a7e69c3f5ff5eb` |
| Side wood-side.png, reopened at 144 samples | `cba4516262579ae6ad8d16c7d3f75c41c303c2f20605b06edffa1a40c5fe58e5` |
| Released parent at 108b391 | `c404e26928309df6233e2e7b3595d5d10025632a18e61e635294eb08b411f33e` |
| Packed wood-atlas-improvement-014-B.png and pigment.png | `f6e6b26fad1baf22bbf7dd0eb0427cb61b9064245af6acbd268d31068502f4c8` |

Extract source-and-seeds.zip to a fresh directory and run reproduce.ps1 inside the extracted candidate folder. The archive includes the released scene, accepted atlas, registered views, two approved black references, source measurements, recipe 10, native sculpt and verification programs, and mission export/viewer helpers. It uses Blender 5.2, Python with NumPy and Pillow, Node with Playwright, and Chromium. [Recipe and parameters](parameters.json) · [Seed and source digests](support.json) · [Proof digests](proof.json)
