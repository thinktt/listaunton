# Pawn checkpoint 001

Start from the archived seated clay model in `history/pawn-mission-start`.
The geometrical authority is the original black pawn, checked against the
white sprite. Black candidate 2 is the detail target. Its sphere is about
three pixels wider in radius than the black sprite in the 1254-pixel frame.
The trial keeps the original radius, approved seat and fixed registration.

`scorecard.json` records every trial's five scores, both original IoUs, selected
IoU, hashes, and decision. `checkpoint.json` records the retained result and
independent rebuild comparison. The fixed images are actual Cycles renders.
The side guide is imagined. The side model is registered uniformly by foot
width and baseline. Wrapped grain across unseen surfaces is artistic inference.

To reproduce the retained result from tracked inputs, run from the repo root:

```sh
blender -b --python-exit-code 1 --python scripts/pawn/apply_wood.py -- docs/pawn-mission/iteration-001/reproduction.json
python scripts/pawn/audit_mission.py 006-reproduce-checkpoint-001
```

The rebuild creates a separate trial under `build/pawn-mission`. It reads the
archived closed control, the geometry/light config and the packed pigment
source used for delivery. It leaves the accepted model available to compare.

To investigate the raw pigment derivation, render config 003 with
`mission_trial.py`, measure black/gray/depth with `capture_pigment.py`, then
use `complete_wood.py` with `measure-003` and a separate texture output path.
The old trial shader and the saved PNG use independent render lighting. The
archived source of the hidden pigment is the repository's unlit
`assets/queen/walnut-fine-albedo.png`. See the measured input/output hashes
and confidence method alongside this file.

After visual acceptance run `deliver_mission.py` for the inspected trial,
validate with `scripts/pawn/validate.py`, then run `compare.py`,
`contact_sheet.py`, `build_side_comparison.py`, `build_viewer.py` and
`check_viewer.cjs`. Rebuild only the pawn review with
`python scripts/build_candidate_pages.py --piece pawn`. Validate the site,
original/candidate hashes, model links and saved gallery dimensions. Sync the
local review and its model/texture at each accepted checkpoint.
