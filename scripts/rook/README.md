# Rook reconstruction pipeline

Read the root AGENTS.md, MISSION-ROOK.md and latest docs/rook-mission-log.md before work. The original black/white Lichess sprites determine proportions; selected black candidate 8 supplies detail. Preserve their bytes and registration.

The current accepted model is wood checkpoint 004. It retains the continuous subdivided lathe, shallow recessed floor and four equal thin curved merlons, joined through editable exact Boolean modifiers. Hidden merlon construction objects remain editable. A packed 3072-square pigment atlas on `Pigment atlas` UVs supplies color; live Principled BSDF, relief, coat and lights supply shading. The first wood finish is incomplete. See docs/rook-mission/iteration-004 for scores, limitations and reproduction.

The saved camera is orthographic, 54 degrees elevation with -0.35-degree roll. Export the evaluated visible union, not the hidden construction objects. The textured mesh has 62,522 triangles and 32-byte position/normal/UV vertices. Keep the same saved model in the overlay, rotating viewer and side comparison.

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
