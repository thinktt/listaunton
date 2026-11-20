# Round 15A · Upper eyelid and ear seat

The upper lid begins as a fine cut at the earward corner, rises over the ocular surface and tapers into the nasal bridge. On the real side the earlier hook below the swept ear has softened into the skull. With a moving lamp, the eye retains an almond-shaped opening after its central reflection leaves. The newly tucked ear root sits farther back from the lid in profile. [True profiles](true-profiles.png) · [Earward corner](earward-corner.png) · [Moving-light comparison](moving-light.png)

| Fixed 54° measure | Black 2 | Parent 14B | 15A |
| --- | ---: | ---: | ---: |
| Earward crease displacement, px | 0 | −2.93 | +1.60 |
| Middle crease displacement, px | 0 | +0.17 | −0.58 |
| Noseward crease displacement, px | 0 | +2.85 | +1.24 |
| Inner reflection, x / y | 504 / 473 | 503 / 480 | 507 / 472 |
| Inner reflection luminance | 154 | 107 | 101 |
| Visible insert area, px | — | 1,090 | 846 |

The crease offsets use downward-positive image coordinates. At the original sprite's native scale the aperture reads more quietly under the brow. The inset is 22% smaller in the fixed view, and Black 2 has a brighter central reflection and carries its small noseward glint nine pixels farther forward. The side opening remains visible under grazing light. [Registered detail](eye-study.png) · [Upper crease and glint measurements](upper-eye-sweep.png) · [100-pixel board](board.png) · [Fixed and registered 7° renders](fixed-and-side.png)

## Carving and validation

The local sculpt modifies the skull and its underlying support, the paired ear undersides and both closed eye inserts. The crown, mane and body keep the accepted walnut atlas. The upper orbital plane rolls under the brow, while a local vertical displacement lifts the nasal commissure through the skull and insert together. The two layers of each insert travel together. A small increase in wax coverage on the central eye helps it reflect the existing lamps. The camera, lighting and pigment remain identical to 14B.

The sampled exposed areas of the two eyes overlap by 99.39% when mirrored. Native surface intersections and solid-ray integration put 46.43% of the near insert and 46.05% of the far insert inside the skull. The closed surfaces cross at 1,194 and 1,202 non-tangent triangle pairs. The far and near rims carry each cap around a small central cavity. All six edited parts passed nonadjacent self-intersection and zero-area triangle checks. The viewer export passed its UV, normal, index, varnish and packed-texture checks with 156,861 vertices and 288,430 triangles. [Native intersections](sculpt-check.json) · [Eye seating](release-eye-seating.json) · [Paired eyes](paired-eyes.png) · [Viewer manifest](web-export/mesh.json)

All 40,086 skull vertices outside the edit volume agree with their parent by original vertex ID. The 7° render's entire alpha channel agrees exactly. In the 54° view, Catmull–Clark subdivision carries a small change into the far ear above the edited cage. Fourteen silhouette pixels cross the 50% opacity threshold between x414–440 and y303–307. Fixed silhouette intersection over union is 0.999957. The mane and pedestal geometry are byte-identical. [Protection checks](protected.json) · [Silhouette measurements](silhouette.json)

| Deliverable | SHA-256 |
| --- | --- |
| Frozen knight.blend | 6a062fcb3b3eb525d3f10f137f6725d3db4b66f74cd0c8e79d9b0e4662741418 |
| Packed atlas and pigment.png | f6e6b26fad1baf22bbf7dd0eb0427cb61b9064245af6acbd268d31068502f4c8 |
| Reopened 144-sample wood.png | aedb05c42b445c0af3bf9042acbdae2ab9a8cfc616d5031eda63a7dedc546e26 |
| Reopened 144-sample wood-side.png | a73198c4c3ad1a5b93346885713be0c35a0221395468df6b782841eb418c6569 |
| Parent 14B | c404e26928309df6233e2e7b3595d5d10025632a18e61e635294eb08b411f33e |

## Reproduction

Use Blender 5.2.2 with the supplied `parent.blend`, `pigment.png` and `source-anchors.json`. The project rendering scripts are resolved from the staged tree. Run these commands from the trial directory.

~~~text
blender -b --factory-startup --python-exit-code 2 --python survey.py
blender -b --factory-startup --python-exit-code 2 --python sculpt.py
blender -b --factory-startup --python-exit-code 2 --python pictures.py -- parent
blender -b --factory-startup --python-exit-code 2 --python pictures.py -- final
blender -b --factory-startup --python-exit-code 2 --python moving.py
blender -b --factory-startup --python-exit-code 2 --python seating.py
blender -b --factory-startup --python-exit-code 2 --python export_check.py
blender -b --factory-startup --python-exit-code 2 --python eye_portraits.py -- ../../.. knight.blend portraits
blender -b --factory-startup --python-exit-code 2 --python eye_portraits.py -- ../../.. knight.blend turn-study --turn
python study.py knight
python measure.py final
python sheets.py
~~~

The reported frozen file went through the same sculpt using the `inspection` argument, passed `check.py -- native`, and was copied byte-for-byte to `knight.blend`. Trial pose, physical curve controls, bilateral vertex counts and maximum displacements are in [parameters.json](parameters.json). The Blender files include the packed atlas. The external atlas is its exact binary copy.
