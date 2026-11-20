# 13A · Brow and nasal fold

The upper lid rises through the brow and narrows into the bridge on both flanks. The lower lid rolls out into the cheek, and the front corner has a smoother plane that lets the reflection fade. The globe still carries the small crescent inside the aperture. In the 54° image, the exposed eye occupies 1,090 pixels, up from 976 on 12B. The outside silhouette matches the released parent at every pixel in both registered views at an alpha threshold of 127.

| Registered measurement | Original | Black 2 | 12B | 13A |
| --- | ---: | ---: | ---: | ---: |
| Middle 80% of lower reflection, pixels | 42 | 42 | 18 | 38 |
| Left / right reflection endpoints | 483 / 525 | 483 / 525 | 493 / 511 | 481 / 519 |
| Lower reflection peak above nearby cheek, 0–255 | 52 | 120 | 111 | 52 |
| Brightness on the nasal continuation, 0–255 | 31 | 27 | 32 | 30 |

The 13A brow is shallower on the real flanks. Across 65 equally spaced sections, the near upper margin has median recess 0.02045 model units, down from 0.04746. The near lower margin changes from 0.02006 to 0.02188. The two exposed apertures overlap by 99.5% after reversing the head pose. The parent’s encircling lower rim recedes in plain clay at all three oblique angles. The nasal extension remains clearest in profile and dissolves before the muzzle.

The lower reflection has the contrast of the original sprite. Black 2 has a brighter central accent and carries more light toward the nose. The forward bridge shadow falls within one pixel of the photographed trace on the final render. At board size the eye reads as one broader, quieter mark. With 12B’s lamps restored, the central crescent is also quieter. The two existing physical eye emitters were repositioned and resized, and the lower one was warmed. The competing white point at x545, y493 now reads as dark walnut, RGB 87, 42, 18.

## Geometry and finish

The sculpt uses the same upper and lower profiles in the coordinates of each cheek. The forehead and cheek around the orbit constrain the surface fit. A local subdivision supports the nasal turn, with a maximum fairing displacement of 0.01564 units there. The original packed grain modulates the local wax coverage and up to 0.0017 units of physical surface relief on the lower cheek. The 12B packed atlas is byte-identical. The sharp mane, swept ears, pedestal, camera and 39,335 skull vertices outside the orbital region are geometrically unchanged.

The final topology uses internal diagonals at the subdivision boundary. The repair preserved every native skull vertex coordinate. All evaluated faces have finite normals and positive measured area. The smallest doubled triangle area on the skull is 1.1660 × 10⁻⁸. Each eye and the continuous skull passed the nonadjacent-triangle self-intersection check. The actual viewer export contains 288,430 triangles and 156,861 vertices, with finite UVs, unit normals and one varnish byte per vertex.

## Files

- `knight.blend` is the editable frozen scene, SHA-256 `cd5de4ca41bf7061e04caf14843f399f49f7a82df8376bb966890d11edada20b`.
- `wood.png` is the reopened 144-sample fixed render, SHA-256 `96b566d290cc892a6818959e1093aa8de10103db091cdf83e9bfe6cb8cf9eaa8`. `wood-side.png` is its registered 7° side, SHA-256 `21dfb1a854d3bee713146d4323373e48c052bc07d1d1de9b5d8d21c120944eec`.
- `pigment.png` matches the packed atlas, SHA-256 `1e35b27f1eea257ee9bacc6ae60aa26cbeaf80fad5139365d58be1db395dd78b`.
- `registered-eye.png`, `board.png` and `comparison.png` show the two black source images at fixed registration. `matched-studio.png` compares inherited and final lights. `flank-portraits.png`, `whole-head-clay.png` and `moving-light.png` show the real carving from both sides and under a moving light. `moving-highlight.webp` animates the walnut light sweep.
- `reproduce.ps1` runs the build and validation in a copy of this directory at the same staging depth. `parameters.json`, `socket-sections.json`, `fixed-measures.json`, `repair.json` and `protected.json` record the numerical evidence. `web-export` contains the tested viewer buffers.
