# Queen projection and proportion study

Seven physically different queen interpretations are compared at **48°, 51.5°, 52°, 54°, 56°, 60°, and 64°**. The 51.5° entry retains the accepted queen's editable shape and is the default. These historical alternatives and their renders remain unchanged. The current queen was later refit at 54° and is documented in [the current queen notes](queen-54-wood.md). Their 39 original hashes are recorded in `assets/queen-projections/baseline-preservation.json`; a separately recorded LF-normalized checksum permits only newline changes in recognized text files after checkout. The review page and its interaction regression test are excluded because the authorized fourth-tab integration changes those two UI files. The original 40-file snapshot passed strict byte checks before excluding that test. The 39 protected inputs are now archived under `history/queen-before-54-finish`.

[Open the comparison](../queen-projections.html). It provides front profiles, free rotation, and overlays against the original black sprite or selected queen reference. The original black sprite is the default overlay source. The references are embedded unchanged, with the existing uniform alignment retained. Each Blender download contains the candidate's own saved reference camera.

## Geometry and framing

The study uses the accepted one-piece body, continuous eight-tip splash crown, and egg finial: 192 segments around 117 control rings. Five smoothly blended feature groups—foot, socket, collars, crown, and egg—receive vertical and bounded radial adjustments. The assumed camera elevation changes the physical height needed to explain the image. This changes actual editable geometry; each candidate is exported and rendered from that geometry.

The fit objective gives the original silhouette 80% weight and the selected reference 20%. Preserved front-ring arcs constrain interior detail, and radius limits keep the accepted chunky carving. The foot radius and floor are fixed. The 51.5° baseline has zero fit parameters; it is translated to ground level, with camera compensation, and uses the same lower subdivision level as the other study candidates.

All candidates have a 2.07342148-unit base diameter and floor at z = 0, within floating-point tolerance. Profiles use the same 600 × 900 orthographic camera, 6.2-unit view height, and target z = 2.9. Rotation uses one shared center and frame. Switching candidate or tool preserves orbit, pan, zoom, and projection; choosing a candidate's reference camera is explicit. No per-candidate height normalization is applied.

## Results and limits

| Assumed camera | Height / base diameter | Original IoU | Selected IoU | Mean original boundary error (px) |
| --- | ---: | ---: | ---: | ---: |
| 48° | 1.7571 | 0.9298 | 0.9157 | 2.8030 |
| 51.5° (current shape) | 1.8862 | 0.9348 | 0.9163 | 2.7729 |
| 52° | 1.9093 | 0.9383 | 0.9200 | 2.5414 |
| 54° | 1.9984 | 0.9288 | 0.9104 | 3.0031 |
| 56° | 2.0871 | 0.9189 | 0.9007 | 3.5124 |
| 60° | 2.2892 | 0.8980 | 0.8799 | 4.5481 |
| 64° | 2.5556 | 0.8751 | 0.8569 | 5.7013 |

The 51.5° baseline is held fixed while the alternatives receive bounded refits, so these scores compare interpretations rather than estimating a uniquely identifiable camera. Silhouette scores use alpha > 128 and maximum reference RGB > 12 to exclude the black background and shadow; dark surface shading and that threshold affect the reported overlap. Boundary errors are expressed in the original sprite's pixel scale.

At higher elevations the queen becomes taller relative to its base, and the circular ring ellipses and crown cavities change. Preserving the accepted carving leaves increasing mismatch at the endpoints. A single shaded sprite cannot determine hidden depth or the original camera uniquely. Neutral and brown viewer materials are diagnostic; wood finish remains later work.

The [front profiles](../assets/queen-projections/profiles.png) show all seven candidates at the same scale. The [original comparison plate](../assets/queen-projections/original-comparison.png) shows each candidate from its own reference camera, with cyan reference and orange model contours. Each angle folder contains the reference render, common-camera profile, original overlay, original and selected contours, fit parameters, export, camera, and QA records.

## Mesh size and verification

Study meshes use subdivision level 1: 89,474 vertices and 178,944 triangles each, compared with 715,776 triangles in the archived canonical level-2 mesh. The embedded binary is 4,294,704 bytes per candidate. The saved Blender sources remain editable control meshes.

For each candidate, 5,041 vertices sampled from its dense level-2 surface were compared with the nearest triangle on its level-1 surface. The largest sampled distance across all seven candidates was **0.132605 original-pixel equivalents**, at 64°. This is a sampled surface-distance measurement, not an exhaustive geometric error bound. The reduced 51.5° baseline render has **0.9996488 silhouette IoU** against the unchanged canonical dense render, with mean boundary difference **0.013847 original pixels** and 126 differing pixels at the 1,254-pixel render resolution.

All seven saved Blender files were reopened without modification. Checks compare their control geometry with the recorded fit, confirm the eight-tip continuous crown, compare the saved reference camera with the exported matrices, and sample each reduced surface against its level-2 counterpart. Every exported mesh is closed, has positive volume, finite normalized attributes, and valid indices. Base diameters, floors, increasing physical heights, and identical profile cameras are checked separately.

The offline HTML is **51,345,071 bytes**, below the 65 MB budget. The runtime test passed **2,121** mesh/camera samples across seven candidates and three viewport shapes, with maximum projection error **0.000039213 pixels**.

The viewer JavaScript is executed by the Node checker with a simulated DOM and recorded WebGL uniforms. It checks responsive projection against saved-camera matrices, candidate and tool switching, orbit/pan/zoom persistence, original and selected references, opacity endpoints, downloads, and the image-only fallback without WebGL. This is runtime and matrix verification, not a native browser GPU rendering test. Rendered comparison images were inspected directly.

## Rebuild and checks

From the repository root with Blender, Python plus NumPy/Pillow, and Node:

```sh
blender -b --python scripts/queen/extract_projection_baseline.py
python scripts/queen/fit_projections.py
blender -b --python scripts/queen/build_projection_models.py
python scripts/queen/analyze_projection_renders.py
blender -b --python scripts/queen/check_projection_models.py
python scripts/queen/build_projections_viewer.py
python scripts/queen/check_projection_variants.py
node scripts/queen/check_projections_viewer.cjs
```

For an interrupted model build, append `-- --resume` to its Blender command to preserve completed candidates and resume missing renders or models. Run analysis and viewer generation after all candidates finish. The extraction, fitting, and model builders are for deliberate rebuilds; they are unnecessary when checking the delivered study.

`check_projection_variants.py` requires all 39 protected canonical files by default. Its `--allow-partial-baseline` option exists only for isolated staging folders and validates every protected input present there; the full repository check must pass before delivery. Binary checksums remain exact. The initial strict byte-for-byte preservation result is retained in the baseline preservation report.
