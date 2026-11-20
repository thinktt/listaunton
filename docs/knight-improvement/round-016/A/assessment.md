# Upper mane, round 16A

The broad crown now rolls into a small, continuous physical bevel on both sides. The bevel turns down toward the forehead above the swept ear, then runs into a short carved shoulder in the skull. In the true rear quarter, the crown, cutting edge and dark plane below it remain readable as the piece turns. See `full-turns.png`, `crest-study.png` and the 100 px `board.png`.

## What changed

I recovered the original section order from the applied mane mesh and reshaped its existing vertices. Five measured sections have a bevel 0.0130–0.0164 model units wide in the lateral direction. At station 2 the cap meets it with 16.69° of normal rotation. Below it the slope rises smoothly from 0.87 to 2.39 without a second outward ridge. The five paired sections agree across the unposed symmetry plane to within 0.0000015 units. The largest moves were 0.033575 on the mane and 0.014060 at the forehead seat. See `sections.png` and `native-proof.json`.

The shape changes where the light turns even in the old studio. I also eased the finish on the dark plane, increased wax coverage along the bevel and fitted two real warm elliptical lights linked to the mane. The retuned rear light measures 2.204 × 0.060 at 54 W. The new front light measures 1.341 × 0.082 at 8.2 W. `matched-light.png` isolates the carving and finish under the original lights, then adds the two fitted ellipses. Lamp locations and colors are in `parameters.json`.

## Registered appearance

| Measure at 54° | Original | Black 2 | 15A | 16A |
|---|---:|---:|---:|---:|
| Upper glint centroid, x in pixels | 435.3 | 437.6 | 380.3 | 404.7 |
| Middle glint, red minus blue | 110.3 | 88.3 | 21.0 | 69.3 |
| Front glint, red minus blue | 93.0 | 54.3 | 31.3 | 53.0 |
| Brightness on the return | 77.1 | 148.4 | 87.8 | 125.4 |
| Underface brightness near the return | 36.9 | 43.5 | 69.7 | 77.4 |

The warmer edge reads farther along the arch at board size. The remaining mismatch is concentrated above the forehead. Its underface catches too much light, and the strongest glint still sits about 33 px behind Black 2. The source terminates the edge more cleanly than the slightly lobed transition visible in the 54° crop. The side, rear quarter and opposite views show a continuous shoulder. Crops are in `profile-study.png`, with full-piece comparisons in `full-piece.png`.

## Verification

The native meshes of the ears, eyes and pedestal agree exactly with their parent. The lower mane from station 3.75 onward and all 69,584 skull vertices outside the edit have zero displacement. All UVs match byte for byte. The registered fixed and side silhouette overlaps are 0.999939 and 0.999779. In the fixed eye crop the 95th-percentile absolute luminance change was zero. On the lower mane blade, median luminance moved from 32.43 to 33.00 out of 255 across 3,987 sampled pixels.

The mane and edited skull each have zero nonmanifold edges, degenerate triangles and self-intersections. The closed noseward cap seats into the skull with 384 triangle-pair intersections in the front joint. The WebGL exporter produced 288,430 indexed triangles and 156,861 vertices. The verifier checked index ranges, finite normalized normals, UV bounds, varnish length and packed atlas bytes. The export is in `web-export/`. Blender studio light linking is specific to the native render.

## Files and reproduction

The private inputs are `parent.blend`, `parent-wood.png`, `parent-side.png` and `pigment.png`. The fixed and registered side PNGs were rendered after reopening the frozen native scene, with 144 samples each. The packed pigment bytes and sidecar match the parent. `appearance.json`, `inspection-qa.json`, `image-proof.json`, `native-proof.json`, `evaluated-mesh.json` and `renders.json` hold the measurements.

| File | SHA-256 |
|---|---|
| Parent scene | e865a0c635e99bb07a5262a48499140dc34b0e61c757d1e362913fa1c12aef6a |
| knight.blend | 9f911cbdd0f2cc66b800e0b377c87ab4f3773ebc552027759a2e9b2c4cb0750c |
| pigment.png | f6e6b26fad1baf22bbf7dd0eb0427cb61b9064245af6acbd268d31068502f4c8 |
| wood.png | 19acfe74e458ea72cf85d1ab5558030b76eeb544278b4ca6721ebfd1bf9c4f36 |
| wood-side.png | 938346eef7710218754929e89e0f068261ba4d889d1376ca777f7eb464ae0f35 |

To reproduce in a separate copy of this directory inside the staged tree, run the following in PowerShell with Blender 5.2 and the supplied Python environment. The scripts use the staged mission renderer, the original sprite and Black 2. Blender saves may vary in byte identity. `parameters.json` records the digest of each new save.

```powershell
blender -b --factory-startup --python-exit-code 2 --python chart.py
blender -b --factory-startup --python-exit-code 2 --python sculpt.py -- inspect
blender -b --factory-startup --python-exit-code 2 --python geometry_qa.py -- inspection
Copy-Item inspection.blend knight.blend -Force
blender -b --factory-startup --python-exit-code 2 --python pictures.py -- parent-crops
blender -b --factory-startup --python-exit-code 2 --python pictures.py -- final
blender -b --factory-startup --python-exit-code 2 --python pictures.py -- turn-parent
blender -b --factory-startup --python-exit-code 2 --python native_proof.py
blender -b --factory-startup --python-exit-code 2 --python evaluated_mesh.py
blender -b --factory-startup --python-exit-code 2 --python export_check.py
python study.py knight
python measure.py final
python sheets.py
```
