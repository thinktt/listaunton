# Round 11B · A crescent carved under the eye

The two eyes have a shallow convex upper form, a lower crescent that turns toward the nose, and a tear corner supported by the cheek. The median upper and lower reflections in the registered view are 9 pixels apart. The centered crest and both ears retain the accepted 10B geometry.

## Comparison

| At x508–516 in the registered image | Parent | 11B | Black 2 |
|---|---|---|---|
| Upper interior, y / luma | 482 / 53 | 479 / 81 | 481 / 90 |
| Separation, y / luma | 487 / 28 | 484 / 37 | 485 / 35 |
| Lower interior, y / luma | 494 / 51 | 488 / 89 | 489 / 92 |
| Lower cheek, y / luma | 500 / 73 | 499 / 139 | 501 / 161 |

The parent’s lower interior measurement falls at the boundary of the search window, where luminance is already rising toward the cheek. The new crescent has a distinct local peak. Inner-eye luminance correlation with Black 2 rises from 0.203 to 0.401. The lower cheek’s average absolute luminance error falls from 27.23 to 25.85, although its spatial correlation falls from 0.667 to 0.619. Its brightest patch is still shorter and more central than the reference. The noseward tip also remains darker. At board size the inner structure reads as one subdued reflection.

In the matched 54° clay view the added crescent is visible below the convex inner form. Under the parent’s walnut lights it catches a weak reflection. The brighter pair of glints requires the fitted eye lamps in the saved studio.

Both the 54° and side foreground masks match the corresponding parent renders at every pixel at an alpha threshold of 127. The whole piece measures 5.08904 model units high. Near-side visible insert area falls 7.2% by native sampling. Opposite openings overlap by 99.51% after undoing the head pose at 0.005-unit pitch, compared with 99.45% for the parent.

## Native carving and finish

Each original closed eye received two levels of simple subdivision with interpolated UVs and varnish. The native eye has 7,938 vertices and 15,872 evaluated triangles. Both were carved in the same unposed longitudinal coordinates. The sloping back retains its original seat. The internal crescent’s lower surface rises toward the nose then tapers before the front corner. The shallow crown varies by about 0.028 units in depth. A matching return on the surrounding cheek rises about 0.018 units. The continuous skull has zero positional change beyond the orbital window.

Only the two eye UV islands and a two-pixel bleed received new pigment. They take the high-frequency grain from adjacent inherited cheek walnut at its physical scale, with a slight lift in the noseward stain. This changes 8,032 texels of the 3,072-square atlas. Exactly the same pigment file is packed and supplied separately. The grain also modulates physical eye relief and varnish. The existing upper and lower eye softboxes were refitted to the curved surfaces. Both inserts can receive the lower light together with the cheek. The lamps and pose for the remaining studio stay as accepted. Independent side portraits and a three-position light sweep show how the carving responds outside the studio setup.

Both evaluated inserts and 17,500 nearby skull triangles passed the nonadjacent-triangle self-intersection check. The actual viewer exporter and repository validator passed all seven visible and two hidden components, finite mesh coordinates, unit normals, camera, source hash, and bounds. Every component is closed with positive signed volume. The only topology changes are the two eyes.

## Evidence

| File | Contents |
|---|---|
| `knight.blend` | Frozen editable sculpture and packed pigment |
| `wood.png`, `wood-side.png` | 144-sample studio renders from the reopened frozen scene |
| `fixed-and-board.png`, `eye-comparison.png` | Registered original, Black 2, parent and frozen proposal |
| `two-flanks.png`, `moving-light.png` | Matched real left and right eyes and a moving broad light |
| `common-fixed.png` | Both sculptures at 54° under the parent studio, common neutral clay and their own saved studio |
| `orbit-proof.png`, `clay-turn.webp` | Near, front, far, rear-quarter, rear and sixteen clay directions |
| `bilateral-eyes.png`, `eyes-B.json`, `native-check-knight.json` | Evaluated side-ray apertures, depth and self-intersections |
| `verified.json`, `review-copy/assets/knight` | Native and exported viewer checks and the actual exported buffers |
| `parameters.json`, `eye-pigment.json`, `proof.json` | Numerical design, lamp placements, atlas change and file hashes |

## SHA-256

| File | Digest |
|---|---|
| Parent source | `7fe492399fa2738d264e73e9e85c427c1531cb902234d43ce1e5012468488922` |
| Frozen scene | `1a308c3a5428897032a3689452db3b79fe19efa3658fb3442eaa8d7f9f5c4d0a` |
| Inherited 008-A pigment | `86debdcce4b5b6075ae7510cb25f77066ae912cfb8e1a0c4a49101ed43b79978` |
| Packed 011-B pigment and external `pigment.png` | `beee98c4ee1af2c55823485a4c0149dea5332c7eaeaa07e06d82ae7022918fe7` |
| Fixed walnut | `6d9ca722895cc7b81b14c58be63a53c17bebec2997de42244195e8ff52af8b48` |
| Side walnut | `e62d634d0ffd72d28b867cfd79ea2d3f48fe938f896ad2343bb535b1da837b18` |

The packed image’s release filename is `wood-atlas-improvement-011-B.png`. To reproduce the sculpture and proof, run the commands in `reproduce.ps1` from an independent copy of this directory within the same mission tree. Blender’s runtime metadata can change the binary .blend digest on subsequent saves. The table identifies the delivered frozen files.
