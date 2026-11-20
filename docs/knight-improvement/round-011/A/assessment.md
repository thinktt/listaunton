# Round 11A

The upper lid grows out of the brow and narrows into a forward crease. The lower lid sweeps down around the corneal surface, then turns outward into the cheek. Both eyes have a shallow, elongated pupil cut and a second crescent on the lower corneal plane. These contours remain visible in the untextured clay and as the head turns through 60 degrees. The paired walnut side portraits show how their reflections change with the viewing angle.

At the fixed camera, the 10B eye showed one central reflection at y477. The 11A gallery gives two inner peaks at **y470 and y473**, against **y467 and y473** in Black 2. The broader cheek glint reaches its maximum at **y501**, compared with y497 in 10B and y500 in Black 2. In the registered eye crop, luminance-pattern correlation with Black 2 improves from 0.203 to 0.421. In the lower-lid crop it moves from 0.667 to 0.807. The 11A cheek measures RGB 100, 48, 16. The source measures 97, 47, 17.

With the original 10B emitters restored for a control render, the 11A inner peaks land at y467 and y475, with a weaker third return at y484. The cheek glint is less intense and peaks at y502. The gallery uses the same two world-space eye emitters refocused on the new surfaces. The underlying walnut pigment, all other emitters, fixed camera and pose are identical to 10B.

The exposed surface grows from 1,036 to 1,128 fixed-camera pixels. In the unposed side-ray test the 11A aperture spans 0.535 × 0.175 scene units along its principal axes. The parent spans 0.505 × 0.148. The whole aperture still slopes steeply, measuring 50.7° down from the head horizontal compared with 47.8° in 10B. The shallow pupil and curved corneal plane give the central eye a different orientation. The lower cheek highlight remains more concentrated and irregular than the source at full enlargement. The near and far apertures overlap by 99.34% under mirroring.

The 10B ears, mane and pedestal retain exact native geometry, UVs and varnish. Both registered silhouette masks agree with the parent at every tested pixel. Their source overlaps are 0.98370 with the original black sprite and 0.97701 with Black 2. The chest sample remains RGB 106, 52, 21.

## Validation and files

- `knight.blend` is the frozen editable sculpture. `wood.png` and `wood-side.png` are its reopened 1254×1254, 144-sample gallery renders. `matched-parent-fixed.png` and `matched-parent-side.png` are separate full 144-sample controls using the original 10B lights.
- `source-comparison.png` compares the original at native 300-pixel size with Black 2, the parent, the parent-light candidate and the gallery candidate. `matched-carving.png` shows both real flanks and the clay turns. `eye-turns-clay.png`, `eye-turns-walnut.png`, `paired-walnut.png` and `diagnostics.png` give the other angles.
- Both ocular surfaces were twice subdivided with native UV interpolation before the carving pass. Each now has 7,682 editable vertices. The native UV atlas bounds and source pigment are preserved. The WebGL exporter produced all seven parts with 243,666 triangles and 135,271 bytes of per-vertex varnish.
- The evaluated ocular forms and the continuous skull have zero non-adjacent self-intersections. All visible meshes are manifold, and the evaluated mesh audit found zero triangles below its area threshold. Native geometry and finish remain exact on all 41,328 sampled skull vertices outside the orbital editing region.
- `parameters.json`, `assessment-metrics.json`, `validation.json`, `matched-studio.json`, `self-intersections.json`, `skull-intersections.json` and `evaluated-mesh.json` contain measurements, parent and candidate identifiers, and geometry and render checks.

## Reproduction

1. Place the supplied `parent.blend` in this folder inside the mission staging layout. Blender 5.2 in background mode with `--python sculpt.py` verifies the parent digest, rebuilds the bilateral socket profiles and closed ocular geometry, focuses the two physical cards, saves the scene and reopens it to render the gallery. `anatomy.py` contains the rest-space profiles and `cards.py` contains the emitter setup. `--python sculpt.py -- --render-only` rerenders the frozen deliverable directly.
2. In Blender, run `parent_studio.py` for the unchanged-light controls, `verify_and_export.py` for native and WebGL checks, and `evaluated_mesh.py` for evaluated triangle and normal checks. Run `self_intersection.py` for the ocular surfaces and append `-- --skull` for the continuous head.
3. `carving_light.py`, `eye_portraits.py`, `paired_walnut.py`, `eye_footprint.py` and `bilateral_eye.py` take the staging root, scene and output path after `--`. Add `--turn` after the portrait output folder for the three oblique close-ups. The parent controls are bound to the canonical parent digest in their respective manifests.
4. Run `report.py` with Python and Pillow for the comparison sheets, geometry, trace peaks and silhouette metrics. `eye_turns.py . parent A`, `walnut_sides.py . parent A` and `plot_bilateral_eye.py . parent A` reproduce the individual turn and flank sheets.

| Frozen output | SHA-256 |
|---|---|
| Parent | `7fe492399fa2738d264e73e9e85c427c1531cb902234d43ce1e5012468488922` |
| 11A scene | `9f3100d8a3b41a055cbe54574f7c1c80633749d2bd9eb66bd7b9312e3b892e8a` |
| Fixed gallery | `0efa5a5e2cce64638ac9506c925f1579de28977532290db219bf75ec2707ea37` |
| Side gallery | `ec75cd1c6d29f98f5b57c031516c52817eae5bff5802f6acd05f3422f4115971` |
