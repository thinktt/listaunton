# 14B · the wood figure on the mane

The mane now reads as a broad face turning into one sharp, dark cut. The earlier dark arc through the middle of the wood has given way to short walnut pores. The material turns continuously across the rear shoulders and the center back.

## Registered comparison

| Measure at 54° | Original | Black 2 | 13A parent | 14B |
| --- | ---: | ---: | ---: | ---: |
| Darkness along the parent's extra arc | −8.4% | −3.7% | 26.8% | −4.8% |
| Strongest continuous dark marking across the face | 2.7% | 6.9% | 26.8% | 6.2% |
| Rear-third / inner-third luminance | 31.1 / 21.4 | 39.9 / 24.5 | 23.4 / 29.3 | 39.2 / 25.6 |
| Grain direction from horizontal | 53.5° | 1.0° | −86.1° | 7.8° |
| Contrast of fine pores at 0–2 pixels | 0.006 | 0.100 | 0.061 | 0.100 |

The first row samples the same curve in each image. A negative value means the center is brighter than the average of its two shoulders. An independent search over the full permitted width gives the second row. The source sprite has little detail at pore scale and slight directional coherence. Its broad tone is the stronger guide at playing size.

The unlit material reduces the extra arc from 33.3% contrast to 4.4%. The 54° studio render places the darkest point of the real cut within a median of two pixels of Black 2's hollow. Its center remains darker than either source, about 5 versus 8 on the 0–255 luminance scale. The candidate's pore direction is slightly more oblique and less coherent than Black 2's. Grain remains more figured on the shoulders than on the center back, where most of the original billet is still visible.

## Restoration

The working chart follows actual cross sections at successive heights of the unposed mane. The middle of the chart is the true back. A smooth exposure correction estimates the broad stain from the adjacent wood on each physical flank and suppresses the long axial anomaly. A second, smaller correction eases the old narrow stain at the center back. The crown and distal end taper into the inherited wood.

Short grain comes from the adjacent neck of the same knight. Native rays recover the neck's existing atlas coordinates. Two ranges of genuine pore detail are transferred onto the mane in model units. A guard tapers corrections before the sampled donor patch ends. The inherited high-frequency figure continues through the repair. The registered source images inform judgment and measurement after rendering. The restoration itself takes the parent atlas and measured native surface as inputs.

The correction changes 346,467 texels, including border bleed, on the 3,072 × 3,072 atlas. All texels occupied by other visible components and their two-texel guard are identical to the parent. The active texture remains packed in the editable scene. The sidecar is byte-identical to the packed PNG.

## Delivery and verification

| File | SHA-256 |
| --- | --- |
| parent.blend | eaecb543e309c713db12fc83888bb2ffc0142686a06917ee6c76d24e7d2b2188 |
| knight.blend | 768e8da32b31736302b3b9b99a747d2a8116aee23887dc227eccd33c233d47fd |
| pigment.png, packed as wood-atlas-improvement-014-B.png | f6e6b26fad1baf22bbf7dd0eb0427cb61b9064245af6acbd268d31068502f4c8 |
| Parent pigment from 12B | 1e35b27f1eea257ee9bacc6ae60aa26cbeaf80fad5139365d58be1db395dd78b |
| wood.png | d3726be6bbd7555c88d622cddb3a67865e457acc0dd6d1d39ad72b047cbe1659 |
| wood-side.png | bbafa6d4b8ed8bd7fb974dc21a41eb9ee1627e7704fc7a60ed8e963797f61e8c |

Both 144-sample renders came from the reopened frozen scene. Verification compared every evaluated mesh, polygon layout and UV layer against 13A, together with varnish values, lights, light linking, camera and physical height. All matched. The hairline surface relief supplied by the existing material responds to the restored pores, visible in the neutral-finish crop. Across that entire crop the mean absolute pixel difference is 0.11 on the 0–255 RGBA scale. Fixed and side silhouettes match the parent pixel for pixel at alpha 128. The native fold checks on the mane and neck passed. The export passed the repository's checks for component topology, bounds, surface normals, camera and eye seating.

Chromium's WebGL 2 renderer compiled the actual viewer shader and drew the exported 288,430 triangles. Its fixed and side presets, neutral finish and drag rotation produced distinct frames. The private side comparison overlays the two actual studio side renders from this round. The viewer's camera agreed with the exported camera to within 0.000028 pixels across 502 sampled vertices.

Run `reproduce.ps1` in a copy of this candidate directory at the same depth beneath the staging root to rebuild the material, export, renders and proof. The local seed inputs are `parent.blend`, `parent-pigment.png`, `parent-wood.png`, `parent-side.png`, `arc-samples.json` and `hollow-samples.json`. The last two supply the inherited mark and source hollow for post-render measurements. The parent atlas supplies the wood for both the receiving surface and the donor. All intermediate NPZ files and the restored atlas are regenerated.

The staging root supplies its existing `scripts/knight` helpers and viewer template, plus `assets/knight/ref.png`, `original.png` and `original-alignment.json` for the two registered references. The script uses Blender 5.2, the bundled NumPy and Pillow Python runtime, Node, the bundled Playwright runtime and installed Chrome. `support.json` lists the exact hashes of the six local seeds, candidate programs, external helpers and approved comparison references. Blender may assign fresh internal identifiers when serializing another editable scene. The frozen digests above identify the delivered files. The board sheet, matched pigment and neutral controls, four-angle material comparisons and 16-frame clay turn accompany the export.
