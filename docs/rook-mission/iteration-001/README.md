# Initial material study — 2026-11-12

Decision: experimental baseline only; rejected for promotion. Accepted model and all public pages remain unchanged.

The saved trial was reopened before rendering with the NVIDIA GTX 1650 Ti through OptiX. Both fixed and side renders completed. Source model SHA remains 23abce50f4a7bd6544f7844534e69a02e3a337a64ee7ce214e81acc353a26f2c. Geometry, merlon construction and the saved 54-degree camera were preserved. The side camera is an unsaved inspection change.

## Examination

The original clay model has a close exterior outline, four thin walls and a shallow recessed floor. Its base appears too softly inflated, the shaft shoulder is broad, and interior wall/floor curvature needs comparison with both original colors. Source black candidate 8 remains the detail reference.

The first procedural material introduces a plausible brown surface but fails the actual grain pattern. Horizontal bands look mechanically smeared, the floor looks cloudy instead of showing vertical wood fibers, the hue is too neutral, and illumination puts a milky reflection across the cavity. Broad shoulder/base highlights replace the reference's narrow bright edge crescents. The reference's richer orange-red pigment and sharp top-edge glints remain missing.

## Scores

Silhouette: historical full-resolution selected IoU 96.9624%, original 95.6489%, using the older strict mask convention. These are NOT fresh measurements under the mission's component/filled-hole convention and are not used in a new overall mean. This first material diagnostic renders at 60% resolution; geometry is unchanged but fresh full-resolution measurements remain required.

Subjective categories, clay baseline -> procedural trial: interior form 78 -> 78; wood color 0 -> 48; grain/surface texture 0 -> 22; lighting/reflections 25 -> 30. These are visual judgments, not calibrated accuracy. No overall score is asserted until consistent current mask measurements are available. This material is still visibly far from the selected reference.

## Next step

Develop reference-informed pigment with lighting removed or attenuated, and continuous plausible wood on unseen surfaces. Target the directional grain in the floor separately from the turned exterior, without painting reference highlights into the final material. Preserve the accepted model until the real shaded material, fixed and side views, and corresponding interactive viewer are validated together. Refine reflected edge crescents after the pigment baseline is credible. Do not accept the procedural study simply because it is brown.

## Reproduction

Run Blender in background mode with scripts/rook/wood_trial.py. It writes only build/rook-mission/001-procedural-baseline. It imports existing king mission utilities for GPU selection and the initial procedural shader without editing king files. The source hash is guarded; the saved trial is reopened before rendering. The canonical original model, references and site remain unmodified.
