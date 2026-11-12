# First accepted rook wood checkpoint — 2026-11-12

Accepted as a substantial improvement over the neutral reconstruction, not as a completed visual match. Current model SHA: `9eaaaaadfd2195591508cda798d56c27aa263ee3baa9424ded8acf76d6e4349c`. The prior neutral model and its current asset set are preserved under `history/rook-mission-000`.

## Result and remaining defects

The editable lathe and four equal thin merlons now carry a real Principled wood material with packed pigment, microrelief, coat and live illumination. Reference-derived pigment captures the selected image's vertical cavity fibers and turned exterior grain. Three small glossy emitters replace the previous broad softbox reflections. Unseen/grazing wood uses folded front pigment with confidence-based interpolation. Only base color is baked into a 3072-square PNG atlas; actual light sources still produce the reflections. These inferred hidden markings are not historical evidence.

This is visibly closer than clay in color and surface detail. It is still too dull on the thin upper rim, shoulder and foot; glints cluster in the wrong places. The rear interior wall contains stretched/abrupt texture features and the side neck has a conspicuous curved pigment transition. Residual image illumination can remain in the approximate albedo estimate. The floor, wall join and rounded base deserve further geometric comparison against both originals. Do not mistake a high exterior overlap for an accurate interior or completed finish.

Selected-reference silhouette IoU: **97.30350%**; original: **95.67335%**, using the shared largest-component/filled-hole convention. Interior form **78%**, color **76%**, grain/surface **66%**, lighting **41%** are subjective judgments. Working mean **71.66%**, holistic visual range **60–70%**. The model dimensions and owner-approved display proportions are unchanged. New mask results are not directly comparable to the earlier unfilled README measurements.

## Geometry and save validation

Adding UV data caused tiny floating-point changes in Blender's subdivision evaluation, so the initial bit-exact evaluated-position check failed. Its failure is retained in `initial-exact-validation-failure.log`. Investigation found byte-exact editable vertex coordinates, evaluated triangle indices, camera and object transforms. Maximum evaluated position difference was 0.000000715256 model units; maximum normal component difference was 0.0000134623. All five editable/evaluated components remain closed with positive signed volumes. The four merlons remain identical in volume and thickness. The scoped validator permits only measured floating-point precision, not changed controls or topology.

All four shader images are packed and finite; the pigment atlas UVs are bounded. The surface output uses Principled BSDF with zero emission. The atlas pixel save/reopen check passed. The final saved model was independently reopened and rendered: foreground mean difference from the atlas trial is 0.00003539/255, maximum 1/255, with identical alpha. Source reference bytes remain unchanged.

## Viewer and local preview

`rook-model.html` now embeds the exact 62,522-triangle evaluated surface with normals/UVs, packed pigment PNG and saved camera. It includes reference overlay, rotating wood/clay previews and a side comparison. The side render comes from the same saved model and is uniformly aligned to the imagined guide by base width and foot; the guide cannot override the original image.

The actual page's Node VM harness checks texture hash, camera reset, 504 projected vertices, pan/rotation/zoom, reference controls, preserved orbit across tabs, source checks on messages, wood/clay selection and side registration. Maximum reference-camera error is 0.00003633 pixels. This is a runtime harness and saved-render inspection, not a claim of native browser/GPU visual QA. Real-time viewer lighting remains approximate. Shared site checks verified all current model frames and the historical projection studies. The existing Windows preview receives the same rook files; other pieces are not modified by this checkpoint.

## Reproduction

1. Run `scripts/rook/wood_trial.py -- --source history/rook-mission-000/rook-rebuilt.blend` in Blender to recreate isolated 001.
2. Run `scripts/rook/inverse_pigment_trial.py -- --separate-lights` to recreate 003.
3. Run `scripts/rook/complete_and_bake.py` to recreate 004, preserving editable Boolean construction.
4. Run `scripts/rook/prepare_checkpoint.py -- TARGET_ROOT` to save and reopen the deliverable, render fixed/profile/rear and write the portable texture path. Stage the unchanged reference/guide inputs and rook scripts into TARGET_ROOT before exporting there.
5. Export with `scripts/rook/export_mission.py -- models/rook/rook-rebuilt.blend assets/rook`; build side registration and viewer; run geometry, material, viewer and site checks. Compare recreated renders rather than assuming .blend serialization hashes will repeat.

For ongoing work start from the current accepted model, not the original builder. Use `scripts/rook/render_views.py` to render the current saved model without saving inspection camera changes. `scripts/rook/validate_material_trial.py VARIANT --model MODEL --baseline BASELINE` checks actual candidate controls/surface against a chosen accepted archive. Keep rejected experiments isolated. At every accepted iteration synchronize fixed/side/model/viewer and local preview before starting another iteration.

## Next action

Target the narrow reflected crescents and bright turret rim while keeping the new color atlas and geometry fixed. Inspect enlarged cavity/rim crops and both originals to distinguish lighting defects from curvature. Then revisit the residual neck and inside-wall texture transitions. The full mission remains active and incomplete.
