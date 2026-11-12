# Knight checkpoint 007

This checkpoint improves the carved chest, the walnut markings on that surface,
and its reflected edges. The fixed reference camera remains orthographic at
54 degrees above the board. The original Lichess sprites still govern the form;
black candidate 2 provides detail. The side guide remains an interpretation.

The working mean rises from 81.06 to 83.06 percent. Outline overlap is measured:
96.87 percent on original black, 96.29 on selected black and 95.96 on mirrored
white. Form 86, wood color 87, grain 79 and lighting 67 are subjective ratings,
not calibrated accuracy. The holistic visual estimate is 79-85 percent.
The shoulder reflection, poll, lower eyelid and several wood details remain
visibly different. This checkpoint does not finish the mission.

## Evidence

- [All trial scores and decisions](scores.json)
- [Original, selected, previous and accepted](comparison.png)
- [Chest features at enlarged scale](chest-study.png)
- [Independent imagined side guide](side-study.png)
- [Neutral views around the model](anatomy-views.png)
- [Actual browser views](browser-views.png)
- [Saved-file geometry scope](scope-validation.json)
- [Pigment change scope](atlas-scope.json)
- [Delivered render reproduction](delivered-reopen.json)

The first deep-channel trial was rejected. Trial 037 retains the smaller depth
change; 038 retargets the physical lights and local varnish; 039 corrects
camera-visible pigment; 040 refines the reflectors into shorter spans.
Eleven of sixteen measured finite cards remain. The complete saved scene uses
real geometry, a packed UV pigment image, physical BSDF layers and actual
lights. The browser uses the same mesh, pigment and finish with approximate
lighting. No reference image is composited over the model.

## Reproduction

Start with the accepted checkpoint-006 model from Git commit `3cc794b`, whose
SHA-256 is
`92af7d120a24047d92f359a02aebff6e8c4ee7e484ee52d8825cf534f532fae3`.
Keep it in an isolated working copy or build directory; do not overwrite
the current accepted model. Git preserves the full earlier checkpoint.
Its pigment is `assets/knight/wood-atlas-v4.png`.

Run Blender scripts with background Blender, `--python-exit-code 1`, and script
arguments after `--`. Run ordinary image-comparison scripts with Python and
NumPy/Pillow. The knight render helper explicitly selects NVIDIA OptiX and
records the device; it falls back to CPU if unavailable.

1. Run `scripts/knight/prepare_reference_values.py` using the base scene.
   It creates the unchanged display reference and its inverse-AgX linear values
   under `build/knight-mission/material-observations`. This standalone helper
   reproduces the prior cached fitting inputs without running an old model build.
2. Run `carve_chest_channel.py` with `--source` set to the base scene,
   `--paths docs/knight-mission/iteration-007/feature-paths.json`,
   `--variant 037-fitted-channel --fit --samples 144`.
   The saved paths include the exact source hash, pose and foot-center shift.
   The measured trials and six selected depths are recorded in
   `037-fitted-channel-parameters.json`.
3. Run `refit_chest_studio.py` with the resulting 037 scene, the same paths,
   and `--variant 038-routed-reflections`. Its saved scene and actual mesh
   must stay together for the camera-ray probe.
4. Run `capture_surface_response.py` on the 038 scene with
   `--out build/knight-mission/038-chest-response`.
   Then run the ordinary Python script `refit_face_pigment.py` with
   `--carving 038-routed-reflections --variant 039-chest-walnut`,
   that response directory, `--texture assets/knight/wood-atlas-v4.png`,
   and `--region chest`.
5. Run `render_pigment_grade.py` with the same carving and variant names.
   This packs the exact new PNG into a fresh image and reopens the saved file.
6. Run `refine_chest_reflections.py` on the 039 scene with the saved feature
   paths and `--variant 040-chest-reflection-segments`.
   Preserve the actual measurement records and inspect the fixed and side
   renders; numerical improvement alone does not establish acceptance.

All named scripts above are under `scripts/knight/`. Changes to topology,
camera, source images, frame registration or source UVs require a fresh audit;
do not relax the recorded checks to reproduce a score.

## Saved scene and review checks

`audit_mission.py` uses the established largest-component, filled-hole masks.
The older `compare.py` raw-boundary report is a separate diagnostic with a
different mask convention. Do not substitute its numbers into the mission mean.

`validate_chest_scope.py` compares the saved current model with the base scene.
It verifies unchanged heights, camera, foot center, UVs, faces, upper head and
lower seat, and exact positions for all other components.
`validate_atlas_scope.py` samples every triangle corner and center to check
that the other components retain their pigment. Its explicit sampling
limitation is recorded in the output.

After acceptance, `publish_mission.py` saves and reopens checkpoint 007 with
`wood-atlas-v5.png`, exports its mesh and finish, and renders the fixed and
registered side views. Run `validate.py`, `compare.py`,
`compare_guide.py`, `build_qa_sheet.py`, `build_viewer.py` and
`check_viewer.cjs`. `check_native_viewer.cjs` checks the real shader and
interactions in headless Edge. The accepted fixed and side renders reproduce
the chosen trial with identical alpha and a mean RGB difference below
0.00005 on the 0-255 scale.

The accepted scene SHA-256 is
`c1254b0087c39e4506b34575d88b52d92a1cd376ed9ee4b891c207d5ce51995c`.
Keep the fixed overlay, rotating viewer and side comparison synchronized
from that saved model. Do not expose rejected trials as current choices.
