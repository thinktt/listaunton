# Round 6A

Round 6A refines the eye ends and the upper mane of the released c8060aa model. The continuous skull carries the bilateral upper and lower lids. The lower shelf extends outwards onto the cheek and the opening ends in a smooth taper. The forward corner visible in side clay loses its short vertical ridge. Against the parent, median surface-normal change across adjacent 0.005-unit samples in the cheek immediately beyond the visible eye fell from 6.18° to 2.19° on the near side and from 7.20° to 2.21° on the far side. The mirrored eye openings overlap by 99.71%. The fixed camera sees 163 eye-floor samples at two-pixel spacing, up from 150.

The crown bevel follows an arch through the existing longitudinal quad rows. A gently rounded shoulder joins the bevel to the broad side plane and fills the projected space below the far ear. The innermost side of the forehead joint extends towards the near ear. The lower six mane sections retain their parent coordinates. The upper bevel receives a stronger varnish finish than its neighboring satin planes. Two existing studio sources were adjusted, the poll oval and the lower-eye reflector. The saved scene uses fixed world-space area lights and the parent's packed textures.

Across the registered poll trace, median half-height reflection width falls from 23 to 13 pixels. Black 2 measures 7 pixels. Median peak position error falls from 3 to 1 pixel. The new arch still has a broader band at its forward end and the small triangular plane at the ear junction is visible in true side. The shadow below the band measures 49 on the 0–255 channel-average scale, compared with 55 in the parent and 44 in black 2.

The fixed contour has zero internal alpha gaps in the crown check over columns 254–479. Candidate outlines overlap the parent by 99.9675% at 54° and 99.9815% in registered side. Against the original sprite and black 2 the fixed outline overlaps by 97.268% and 96.669%. All seven visible meshes have manifold edges and finite UVs and corner normals. No evaluated triangle has double area below 1e-10. The packed image hashes match the parent.

## Model and renders

| File | SHA-256 |
| --- | --- |
| parent.blend | `8a53403942a3e5bea1df92e3f28c9bfd5d80c61a1026a03549f1c21fd4c96cb6` |
| knight.blend | `646675f3647338524b50271b39c571cbe53debd9bf4e9cad4ffffb2b2f4785df` |
| wood.png | `3b1709ceae7a32785150cf771b8a7f008882992859698c466631aa6e543897da` |
| wood-side.png | `6890e63bf743ce14c240d8d214d9a7033846c04f16ca3ed015ad079dc1c60701` |

## Reproduction and inspection

- From this folder inside the staging tree, run Blender 5.2 with `-b --python-exit-code 2 --python sculpt.py`. It checks the input hash and builds the editable model. `glint.py` positions the two studio sources. `diagnostic_views.py` reopens the saved model for both full 144-sample gallery renders, three additional wood angles, and a 16-angle clay turn. `parameters.json` records the settings and resulting hashes.
- Run Blender with `--python inspect_features.py` for two candidate walnut renders under the unchanged parent rig and identical clay views. Run `--python evaluated_mesh.py` to check the triangles and corner normals. See `verified.json` and `evaluated-mesh.json`.
- From the mission Python environment, run `review.py` and `final_study.py` for `final-features.png`, `matched-features.png`, `reference-comparison.png`, `clay-ridges.png`, `diagnostics.png`, and `clay-turn.webp`. The gallery feature comparison includes the original and black 2 at nominal board resolution.
- The independent `bilateral_eye.py` accepts the staging root, blend and output stem after Blender's `--`. Generate `eyes-parent` and `eyes-A` for the two models. Then run `plot_bilateral_eye.py . parent A` for the surface comparison and `corner_metrics.py` for the surface-turn and alpha measurements. `card_metrics.py` measures the finished gallery perceptually against the registered parent and black 2 crops. The position-trial swatches in its sheet were exploratory renders from before the final bevel polish.
