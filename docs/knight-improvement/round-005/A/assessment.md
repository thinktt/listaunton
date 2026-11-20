# Round 5A carved mane and eye

The mane carries eight broad faces around its cross-section, with narrow real bevels at their junctions. The centerline and lower attachment follow the released sculpture. The final two sections taper to 94.5% and 79% of their previous widths. Both eyes have upper and lower lids cut into the continuous skull. A shallow convex walnut floor sits behind each lid. Its maximum thickness on the visible side fell from 0.1383 to 0.0318 scene units.

The fixed-camera measurement sees 150 eye-floor samples at two-pixel spacing, compared with 222 for the parent. Its visible axis descends 11.3° towards the nose, up from 4.8°. See the side and fixed crops in `matched-features.png` for the sculptural change under the parent rig and `final-features-wood.png` for the final finish. The groove at the forward eye corner is stronger in the side view than in the fixed view.

The poll oval was reduced from 112 to 27 W and upper mane varnish was multiplied by 0.47. The upper eye reflector was aimed at the floor and the lower reflector was aimed at the lower eyelid. A broad reflection still follows the upper plane. The packed wood textures matched the parent byte for byte.

The fixed and side silhouettes overlap the parent by 99.84%. Against the original and black candidate 2 respectively, fixed-view silhouette overlap is 97.24% and 96.64%. The lower mane departed slightly from the previous fit. Over rows 580–686 the mean contour error rose from 1.93 to 2.26 pixels against the original and from 2.21 to 2.49 against black candidate 2. The visible union contour turns at row 660 compared with 664 in the parent and 667.5 in the two references.

All seven visible meshes have manifold edges and finite UVs and corner normals. Evaluated meshes have zero triangles with double area below 1e-10. The pigment-projection and wood-atlas UV layers remain on every mesh, and both eye floors retain their additional original UV map. The editable head carries 49,131 vertices, up from 43,499 after local subdivision around the sockets.

## Files and reproduction

- `knight.blend` is the editable candidate. Its SHA-256 is `eb6ba369c8c4a54f99e25eda22652155fd3fb95eda4ad0a12d19bd198ff59d26`. The input alongside it, `parent.blend`, is the released e931993 model.
- Run Blender 5.2 in background mode with `--python sculpt.py` from this folder to rebuild and render in the mission directory layout. The script checks the input hash and uses the shared scripts under `scripts/knight`. `diagnostic_views.py` reopens the candidate for the 144-sample `wood.png` and `wood-side.png` plus the wood turn views. `parameters.json` records the parameters, camera, device and render hashes.
- Run Blender in background mode with `--python inspect_features.py` for the matched parent-light wood and fixed, side, front, back and both rear-quarter clay evidence. Run `--python evaluated_mesh.py` for the post-subdivision mesh audit.
- From the mission's Python environment, `review.py` builds the comparison sheets. `clay-ridges.png`, `reference-comparison.png`, `diagnostics.png` and `clay-turn.webp` contain the additional views. `mane-profile.png` and `mane-profile.json` document the lower-mane fit.
