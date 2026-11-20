# Rook reconstruction pipeline

Read the root AGENTS.md, MISSION-ROOK.md and latest docs/rook-mission-log.md before work. The original black/white Lichess sprites determine proportions; selected black candidate 8 supplies detail. Preserve their bytes and registration.

The current accepted model is shoulder-light checkpoint 078. It retains the continuous subdivided lathe, shallow recessed floor and four equal thin curved merlons, joined through editable exact Boolean modifiers. Hidden merlon construction objects remain editable. A packed 3072-square pigment atlas on `Pigment atlas` UVs supplies color; live Principled BSDF, relief, coat and lights supply shading. The reconstruction remains incomplete. See docs/rook-mission/iteration-078 for current scores, validation and reproduction. Pigment atlas v2 contains a local floor correction; other source-derived pigment retains illumination artifacts. Six derived receivers support foot/shoulder-only glossy strips, turret-restricted reflectors, upper-bevel-only strips and a floor-edge strip; render_regions.py checks exact surface coverage and bounded normal/UV rounding. Export the closed editable control, not the receiver subsets. Regenerate receiver copies after any geometry edit.

The saved camera is orthographic, 54 degrees elevation with -0.35-degree roll. Export the evaluated visible union, not the hidden construction objects. The textured mesh has 62,866 triangles and 32-byte position/normal/UV vertices. Keep the same saved model in the overlay, rotating viewer and side comparison.

## Update current accepted views

Run from the repository root:

```sh
blender -b --python scripts/rook/render_views.py
blender -b --python scripts/rook/export_mission.py -- models/rook/rook-rebuilt.blend assets/rook
python scripts/rook/build_side_comparison.py
python scripts/rook/build_viewer.py
blender -b --python scripts/rook/validate.py -- "$PWD"
node scripts/rook/check_viewer.cjs
python scripts/build_candidate_pages.py --piece rook
python scripts/check_model_site.py
node scripts/check_candidate_review.cjs
```

The rendering helper selects NVIDIA OptiX in-process; saved global preferences alone are insufficient. Rendered profiles are 600x900 and use uniform foot/base-width registration to the imagined side guide. Do not alter gallery defaults or treat generated side images as historical evidence. Native viewer lighting is approximate; the exact camera and mesh are checked by the runtime harness.

For a new material candidate, isolate outputs under build/rook-mission, reopen and render, use audit_mission.py for the shared mask convention, and validate_material_trial.py against the preceding accepted archive. It verifies byte-exact controls/topology/camera, finite packed images, real shaded material and tightly bounded subdivision floating-point changes after UV edits. Preserve the best accepted result until validation and web synchronization complete.

`build_rook.py` and `profile.json` describe the historical neutral reconstruction. Do not run that builder over the accepted wood checkpoint. The original neutral model is archived in history/rook-mission-000. Recreating the early pigment studies requires that explicit archived source. Routine refinement starts from the latest accepted model, as recorded in the mission log.

## Checkpoint 037

Historical checkpoint 037 added two 1500W strips linked to upper rim bevels, with five exact-position render partitions. Original controls, shader/pigment, camera and old lights are preserved. See docs/rook-mission/iteration-037. Reproduce via upper_bevel_rim.py, rim_strength.py, rim_bevel_only.py and stage_rim_checkpoint.py. Remaining texture contamination and floor-edge glint prevent mission completion.

## Checkpoint 047

Floor control rows 53–58 are lower by six profile pixels at fixed 54 degrees. Local pigment repair and perimeter registration are baked into atlas v2; a warm 1000W strip is linked to floor_edge only. Rebuild receivers after geometry edits; the helper now preserves existing floor partitions by default. Export a staged new atlas with --asset-root pointing at that stage. Current public model remains physically shaded; pigment still includes inherited illumination. See iteration-047 for saved/baked/side/viewer checks and measured UV rounding bound.

## Checkpoint 063

Small upper-body pigment repair restores local grain using actual UV/camera correspondence. Geometry, UVs, shader settings and lights remain checkpoint 047. Atlas outside the repair mask is byte-identical. Source reproduction uses history/rook-mission-047; see iteration-063. Lower bands, side seams and reflections remain unfinished.

## Checkpoint 066

Small lower-body pigment repair restores local grain using actual UV/camera correspondence. Geometry, UVs, shader settings and lights remain checkpoint 063. Atlas outside the repair mask is byte-identical. Source reproduction uses history/rook-mission-063; see iteration-066. Residual contrast, side seams and reflections remain unfinished.

## Checkpoint 072

Inferred neck pigment removes the baked side-view arc. Donor tone .563090750970072 was fitted from actual renders. A small high-res neck color tradeoff is documented alongside improved original-color error and side continuity. Geometry, UVs, shader settings and lights are unchanged from 066. Reproduce from history/rook-mission-066 with the fitted-neck scripts; see iteration-072. Finish remains incomplete.

## Checkpoint 078

Two targeted 650W glossy-only shoulder area lights replace the uniform strip, preserving geometry, pigment and other lights. Measured flank peaks and central gap are closer to the reference. Reproduce from history/rook-mission-072 using shoulder_flanks_refined.py; see iteration-078. Fixed/side/viewer assets remain synchronized; full finish is incomplete.
