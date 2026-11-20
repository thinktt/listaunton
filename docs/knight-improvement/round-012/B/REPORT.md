# Round 12B · The inner sweep of the mane

The broad blade now curves from the back of the poll to a single concave turn under each ear. The neck widens underneath it and rounds forward into the breast. The cut grows shallower as it approaches the seat. In two real flank views, one softbox moving from the rear toward the nose reveals the same arcing ridge and hollow. At board size the sweep separates the mane from the neck throughout the turn.

## Registered measurements

| Feature | 11B parent | 12B | Black 2 | Original black |
|---|---:|---:|---:|---:|
| Mane-side luminance | 25.22 | 29.17 | 27.38 | 23.60 |
| Luminance in the photographed hollow | 35.68 | 7.47 | 8.55 | 9.13 |
| Neck-side luminance | 50.42 | 58.55 | 54.66 | 41.58 |
| Darkest offset from the photographed hollow | −19 px | 0 px | +1 px | +2 px |

These measurements are the median horizontal brightness profiles through rows 470–625, blurred by 2.5 pixels. Across thirteen visible cross sections from rows 460 to 640, the native mane/neck intersection misses the center of the reference hollow by 1.38 pixels on average, compared with 44.31 pixels for 11B. The bottom of the physical recess is within 1.77 pixels on average. The full front mask overlaps its parent by 99.964%. The registered side mask differs by one pixel. The evaluated height is 5.08904 units in both scenes.

The new cut is stronger than the photographed hollow near the bottom, and the adjacent walnut neck is about four luminance levels brighter than Black 2. The rear-facing wood reads darker than one of the UV reflow studies. I selected the version with an uninterrupted blade surface and the original fine figure across its face. Some figure at the top of the newly exposed neck remains stretched. The connection into the seat retains a small visible taper at close range.

## Geometry and wood

The previously accepted subdivision of the mane was applied before sculpting. Native sections from both flanks establish the width and the crossing of the original mane and skull. One shared deformation narrows the swept blade, widens the underlying neck, and preserves their overlap. A continuously curved transverse section shapes the blade before it turns inward. The lower sections blend into the neck envelope and a small longitudinal correction keeps the back silhouette smooth. Both hidden construction lofts follow the same transfer. All active lights, light receivers, camera settings and varnish attributes match the parent. The eyes, ears and pedestal have zero positional displacement, as do the upper crest and forward cheek outside the carving window.

The delivered UV layout preserves the grain scale of the previously accepted mesh. Applying Blender’s subdivision changes individual numerical UV coordinates by at most 0.00092 of an atlas texel. A broad 0.69 sRGB color multiplier on the physical faces of the descending blade blends out toward the midline, crown and seat. It changes 337,063 of the 9,437,184 texels. Those texels are exclusive to the mane. The original figure remains visible, and the other parts retain their exact color samples.

With both parts rendered in the same uniform brown, the frozen sculpture measures 35.49 / 5.09 / 52.95 across blade, groove and neck. With illumination removed, the corresponding raw pigment values are 46.56 / 59.97 / 61.70. The dark groove therefore comes from the actual carve and its shadow. The physical sections and moving-light evidence show the same fold on both flanks.

## Verification and files

Both source and scene keep seven visible components and two hidden guides. All evaluated polygon topologies match the parent. In the reopened scene, all 25,600 mane triangles and 29,669 triangles in the neck region passed the nonadjacent-triangle self-intersection check. The native exporter and repository viewer validation passed closed components, positive volumes, unit normals, finite geometry, bounds, source hash and camera.

| File | Contents |
|---|---|
| `knight.blend`, `pigment.png` | Frozen editable model and exact packed atlas bytes |
| `wood.png`, `wood-side.png` | Reopened 144-sample studio views |
| `registered-and-board.png`, `paired-side.png` | Approved photographs, native-size read and same-camera parent comparison |
| `geometry-and-light.png`, `material-control.png` | Native transverse sections, measured reflection profile, raw pigment and uniformly stained geometry |
| `moving-light.png`, `orbit-proof.png`, `clay-turn.webp` | Both real flanks under a moving lamp, five walnut directions and sixteen clay views |
| `parameters.json`, `verified.json`, `proof.json` | Frozen design, native and export checks, render and source hashes |
| `reproduce.ps1` | Rebuilds from the included parent, measures, exports and renders the evidence in an independent copy of this working directory |

| Delivered file | SHA-256 |
|---|---|
| 11B canonical parent | `c4e629d930d907d77885c01dd430cab58e99e26a26e04b63d2a36b373ecdac58` |
| Frozen 12B model | `2d03d00e333c39326a8660eceae5cf19f43c4b36899812ef5c845b8451f0d0c7` |
| Packed atlas and `pigment.png` | `1e35b27f1eea257ee9bacc6ae60aa26cbeaf80fad5139365d58be1db395dd78b` |
| Fixed walnut | `c27b948d48073ac9f5f0dca03635200ed319d78378a1414c954da7d830b1658d` |
| Side walnut | `e22a283426831400c0ad2cd0f8b65d251ce47b669e9426762a1c3d0e8bba56c9` |

The packed atlas’s release name is `wood-atlas-improvement-012-B.png`. The 11B parent pigment has SHA-256 `beee98c4ee1af2c55823485a4c0149dea5332c7eaeaa07e06d82ae7022918fe7`.
