# Round 16B · the upper mane

The main edge reads as warm walnut at playing size, with a smaller reflection on the shoulder as the cap rolls toward the forehead. The cap’s brightest region moves from x380.33 on 15A to x434.75 on 16B. The original places it at x435.32 and Black 2 at x437.55. The full 54° silhouettes of the parent and candidate agree at every pixel above 50% alpha. [Registered piece and board crop](fixed-and-board.png) · [Crest detail](crest-comparison.png)

## Carving and finish

I drew both upper shoulders inward, carried the outer face down and outward as a continuous surface, and gave the cap a shallow, symmetrical dome at its forward end. The front turns 0.057 units noseward and 0.053 downward at full strength, tucking the terminal cut into the forehead. Holding the paired ears at their original coordinates leaves a small strip of the far ear visible above the cap. Six cross sections have a single medial high point and descend toward both shoulders. The average paired height difference is 0.000054 model units, with a maximum of 0.000316. [Physical cross sections](top-sections.png) · [Native checks](verified.json)

Burnish follows the existing grain on the upper surface and the paired narrow bevels. The pigment restoration carries short figure from the billet’s neck through the top and both flanks. It preserves the native UVs, stitches continuously across the ridge and tapers out below the cap. The donor contains local pore and figure variation recorded in model space. It has no photographic highlight. The atlas changes 99,183 texels, all on the mane, with the lowest changed texel at z4.725. [Material measurements](pigment-proof.json)

The original rear oval becomes a warm amber strip aimed at the physical bevel. A small elliptical light above the forehead catches the front roll. Both lamps illuminate the mane. The wood and clay checks rotate one separate broad area light from behind to overhead and then forward, looking at both flanks. [Light isolation](controlled-light.png) · [Near flank](moving-near.png) · [Far flank](moving-far.png) · [Full turn](clay-turn.webp)

## Registered measurements

| Measurement | Original | Black 2 | 15A | 16B |
|---|---:|---:|---:|---:|
| Forward cap centroid x | 435.32 | 437.55 | 380.33 | 434.75 |
| Forward cap centroid y | 333.74 | 332.54 | 332.39 | 332.56 |
| Middle edge luminance | 81.35 | 148.38 | 153.81 | 129.83 |
| Middle edge red minus blue | 110.33 | 95.00 | 23.67 | 93.00 |
| Underface luminance beneath the middle edge | 39.00 | 42.49 | 56.14 | 46.91 |
| Forward shoulder relative pore contrast | 0.0537 | 0.1814 | 0.0934 | 0.0796 |
| Noseward return luminance | 76.75 | 142.77 | 87.67 | 98.89 |

The front cap patch is smaller than in the straight-edge trials. Its wood figure is quieter than Black 2, and the remaining reflection across the cap is more linear. At the forehead the reflected strand still fades before completing the bright downturned arc in Black 2. The forward underface is also lighter than the source. [Full measurements](crest-comparison.json)

## Geometry and delivery

The carve moves 4,028 mane vertices. All 25,600 mane triangles pass the nonadjacent intersection check. Vertex counts, topology and every evaluated UV layer match 15A. Every other component retains its exact geometry. The seven visible components pass the native validator, and the private Chromium viewer passes its camera, orbit and material checks. An in-memory rebuild reproduces the native coordinates, UVs, varnish, packed atlas and studio. [Replay](replay.json) · [Viewer verification](webgl/native-qa.json)

The physical height rises from 5.08904 to 5.11109 units, or 0.43%. The raised cap changes 691 silhouette pixels in the registered 7° side view, with silhouette IoU 0.99843. Outside the fixed crest crop, the mean absolute luminance change on the piece is 0.0183 levels on a 0–255 scale. It is 0.00092 levels around the accepted eye. [Silhouette and exposure measurements](extent.json) · [Turn views](orbit-proof.png)

| File | SHA-256 |
|---|---|
| Frozen knight.blend | `945f97db359cf093a13be4490e96026770706f17caa1c83106b14759641f4617` |
| Reopened 144-sample wood.png | `e7b54e1a2e61755320b1b58d8a8d5f8b15ab4e87ae7a9d8418fc9da0b973032a` |
| Reopened 144-sample wood-side.png | `de6c4d55ab3c3c52f7a0bbe9c29b489aa6c0dd06565a48fe902a160f6b107ecb` |
| Packed wood-atlas-improvement-016-B.png and pigment.png | `b56e8104f8845b4d221e82b1c20ff40f16d4361435d30a0a83b8be8882d6e69d` |
| Released 15A model at eeb1016 | `e865a0c635e99bb07a5262a48499140dc34b0e61c757d1e362913fa1c12aef6a` |
| Released 014-B atlas | `f6e6b26fad1baf22bbf7dd0eb0427cb61b9064245af6acbd268d31068502f4c8` |

Extract source-and-seeds.zip and run reproduce.ps1 in its private candidate folder. The package includes the accepted model and renders, the released atlas, the native neck-figure seed used for the accepted 14B timber restoration, the two black references, recipe 33 and all required source and review helpers. It uses Blender 5.2, Python with NumPy and Pillow, Node with Playwright and Chromium. [Parameters](parameters.json) · [Source and seed digests](support.json) · [Evidence digests](proof.json)
