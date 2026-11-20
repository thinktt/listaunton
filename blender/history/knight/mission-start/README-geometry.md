# Knight reconstruction

The current instruction is to match the owner-approved side study in `assets/knight/concepts/side-01.png` first, while fitting the original image as well as possible. The broad cheek, thick rounded muzzle, wide S-shaped neck/chest, arched mane, sloping forehead and flat lower plinth now follow that study. The head and cheek remain one envelope joined to the neck. The study is an imagined interpretation, not recovered geometry. The original black and mirrored white Lichess sprites and selected black candidate 2 remain unchanged secondary reference checks.

The previous committed anatomy correction is preserved in `history/knight/11-before-guide-match`. That model was too thin through the neck and cheek and too pointed at the muzzle. This revision rebuilds the large side masses from the guide's coordinates. A single subsequent depth correction narrows the head and upper neck along Y while retaining their XZ profiles. Both eye forms are seated in the evaluated socket surfaces after smoothing the skin.

`assets/knight/guide-comparison.png` places the untouched guide, neutral-clay side render and silhouette overlay at the same 565-pixel base width and 1127-pixel projected floor. The inferred side camera is 7 degrees above level. `guide-camera.json` records that independent framing. `anatomy-angles.png` shows level profile, front, three-quarter, side, opposite and the saved reference camera. These images show the substantial side-shape improvement; silhouette overlap alone does not establish anatomical fidelity. Fine carving, material, depth and unseen surfaces still differ from the study.

Seven visible components are individually closed and connected: continuous head/neck skin, mane, two ears, two eyes and pedestal. Two closed construction lofts remain hidden and editable. The visible export has 203,602 triangles. The separate overlapping components are not fused for manufacturing. Neutral clay is diagnostic; wood materials have not been reconstructed.

## Secondary reference fit

After the side shape was established, a bounded camera study tried yaw angles -12, -6, 0, 6 and 12 degrees at the existing 54-degree elevation, with uniform scale and translation. It did not warp source images or alter their registration. The chosen saved camera uses 12-degree yaw, 0.985 framing scale and an 8.36-pixel shift left and up at 1254-pixel output resolution. Render, Blender camera, exported camera and viewer use the same result.

For the final geometry, original-black silhouette IoU is 85.76% under the frozen previous camera and 88.46% under the fitted camera; mean boundary discrepancy falls from 7.59 to 6.20 original-source pixels. Selected candidate IoU is 88.12%; mirrored original white is 87.98%. `assets/knight/reference-fit/fit.json` records the bounded study, while `frozen-camera.png`, `frozen-camera.json` and `frozen-qa.json` preserve its baseline. The final `qa.json` records the full-resolution fitted result. The broader guide-derived chest and longer side head extent do not simultaneously reproduce the original overhead silhouette. This is an explicit remaining limitation, not a claim of recovered geometry.

## Rebuild

From the repository root, using Blender, ordinary Python with Pillow/NumPy, and Node:

```sh
blender --background --python scripts/knight/build_knight.py
blender --background --python scripts/knight/guide_view.py
python scripts/knight/compare_guide.py
blender --background --python scripts/knight/qa_views.py
python scripts/knight/compare.py
blender --background --python scripts/knight/validate.py -- "$PWD"
python scripts/knight/build_qa_sheet.py
python scripts/knight/build_viewer.py
node scripts/knight/check_viewer.cjs
python scripts/build_candidate_pages.py
python scripts/check_model_site.py
```

The normal build uses the selected framing stored in `profile.json`; it does not rerun the camera study. `fit_reference.py` and `choose_reference_fit.py` document that optional bounded study and do not apply a new choice automatically. Use Windows/UNC paths when Windows Blender works on the WSL repository. The viewer's Front button faces the muzzle; Side shows the horse profile. Reset returns to the fitted reference camera.

Validation checks manifold closed components, one connected shell per component, positive volumes, eye/socket overlap, mesh bounds/normals/indices, source hash and both saved camera matrices. The Node viewer harness passes camera and interaction checks, including Front/Side presets, with sampled projection error below 0.00003 pixels. Native browser rendering has not been independently tested here.
