# Replaying the knight carving

The parent for these trials is the editable knight from commit `67ea10d`. The selected model for checkpoint 008 is trial 043. Its geometry also appears in trial 042. The two trials have different material coverage on the mane and different studio settings. Both use the same graded walnut atlas.

## Rebuild the model

Run these commands from the project root at the checkpoint 008 revision, using Bash with Blender 5.2.2 on the path. The example writes the extracted parent and an optional new model under `/tmp`. Choose an unused output filename. The recipe checks the parent and atlas hashes before making changes.

```bash
replay="$(pwd)/docs/knight-mission/iteration-008/replay"
git show 67ea10d:models/knight/knight-rebuilt.blend > /tmp/knight-16A.blend
blender -b --python-exit-code 1 --python "$replay/rebuild.py" -- \
  . /tmp/knight-16A.blend assets/knight/wood-atlas-mission-008.png \
  --variant 043 --compare models/knight/knight-rebuilt.blend \
  --out /tmp/rebuilt-knight-008.blend
```

Omit `--out` to run the comparison in memory. The `--variant 042` option reproduces the earlier finish. Blender serializes scene bookkeeping when it saves. The comparison checks the evaluated mesh, corner normals, topology, UV coordinates and transforms for all nine mesh objects. It also checks the seven visible parts’ varnish attributes, packed pigment, fixed camera, the lights’ positions, shapes, powers, colors, spreads, and their links to the receiving objects. [Trial 042 replay](rebuilt-042.json) · [Trial 043 replay](rebuilt-043.json)

## Geometry and finish

A fresh rebuild from the parent was saved, reopened and checked against the published checkpoint scene. All nine mesh fingerprints, seven finish attributes, the packed pigment and the fixed camera matched exactly. The checked numeric differences across 27 lights were zero. Independently rederiving the topology and radial section seeds also reproduced both workers’ geometry. [Publication replay receipt](rebuilt-release.json) · [Seed verification](rederived-seeds.json)

- The mane keeps its 49 × 256 station grid and closed end caps. The recipe changes the sections to a shallow crown, broad side faces and a small bevel. [Cross sections](mission008-mane/physical-sections.png) · [Carving recipe](mission008-mane/geometry.py)
- The neck uses the parent’s radial sections, a front face and two oblique side faces. The edges ease into the wider seat. Near the rear weld, the correction tapers into the inherited upper neck. [Cross sections](mission008-neck/sections.png) · [Carving recipe](mission008-neck/neck.py)
- The nine upper rings on the pedestal form the turned shoulder and level ledge. Four rings share the same top elevation. The combined footprint of mane and neck lies inside the ledge at every one of the 360 sampled angles. Front clearance is 0.05350 model units and back clearance is 0.10693, measured within 0.00001 units of the top. Both sculptures intersect the pedestal. [Native contact measurements](native-seating.json) · [Turning profile and polish](level/platform.json)
- Trial 043 uses the physical varnish values on the mane and two area lights linked to that component. The two pedestal strips are set to 50% and 30% of their previous powers. [Mane finish recipe](mane-finish/recipe.json) · [Isolated highlight comparison](mane-finish/crest.png) · [Integrated studio adjustments](finish_043.py)

The shelf measurement can also be run directly on the published model.

```bash
blender -b --python-exit-code 1 --python "$replay/check_seating.py" -- \
  /tmp/knight-seating.json models/knight/knight-rebuilt.blend
```

## Pigment provenance

The permanent atlas at `assets/knight/wood-atlas-mission-008.png` is the output of an earlier upper-turning study. A full Cycles response, a reduced diffuse response and a camera-depth pass on the cove trial isolated visible areas of the pedestal. The gain fades out below its shoulder. The grade changed 79,845 atlas pixels. The later level turning uses those same UVs. [Measured surfaces](cove/measurement.json) · [Grade and source hashes](cove/grade.json) · [Projection and grading code](grade_platform.py)

To remeasure the pigment, use an isolated checkout of `67ea10d` containing the original atlas and its checkpoint file. Keep this replay directory available separately and run the following in the old checkout. The 128-sample Cycles captures require Blender. The projection step uses Python, NumPy, Pillow, and the dependencies imported by the project's knight scripts. Render backend and denoiser differences can affect a new measurement. The release atlas SHA-256 is `8666e40bed34d56756ac035a944396bfbd89eba78d05bc65ed42a31690381d71`.

```bash
blender -b --python-exit-code 1 --python "$replay/turn_platform.py" -- \
  . cove /tmp/knight-008-cove --satin --samples 96 --full
blender -b --python-exit-code 1 --python scripts/knight/capture_surface_response.py -- \
  --source /tmp/knight-008-cove/knight.blend --out /tmp/knight-008-response
python3 "$replay/grade_platform.py" . /tmp/knight-008-cove \
  /tmp/knight-008-response /tmp/knight-008-grade
```

Set `replay` to the absolute path of this packet when running in the old checkout. To rederive the stored topology and neck-section seeds there, run `verify_geometry.py` with the project path and `--rederive-seeds`. The original independent merge and component file hashes remain in the [merge record](level/combination.json) and [input inventory](inventory.json).
